#!/usr/bin/env python3
"""bashwrites: resolve what a Bash command writes, as absolute paths.

  writes(command, cwd) -> list[str]   absolute, normalised paths the command would write.

Why it exists: judging a Bash command by the text of its protected-file names misses a bare
name after `cd`, a glob, a variable, or an interpreter one-liner. records-guard loads this
module from beside itself and matches protected globs on the RESOLVED path. Static only:
nothing is executed. What it follows:
  - `cd X`, `pushd X`, `git -C X` and `&&`/`;`/`|`/newline chains, so a bare filename after
    `cd docs` resolves against docs;
  - redirects (`>`, `>>`), write verbs (tee, cp, mv, rm, touch, install, ln, rsync, truncate,
    dd, sed -i, perl -i, git checkout/restore/apply) and their operands;
  - globs, brace lists, `VAR=value` and `$(echo ..)`/`$(printf ..)`/backtick names;
  - `bash -c`, `sh -c`, `eval` strings (re-parsed), and inline interpreters (`python3 -c`,
    `node -e`, ruby/perl/php, heredoc bodies): every string literal next to a write call is a
    candidate, with `'a'+'b'`, `join('a','b')` and `Path('a')/'b'` folded, and `chdir('d')`
    followed.
The one edge that bites: names built at run time from input, files or the network, and
`printf` with a format string, are not resolved; keep records-guard `--staged` in pre-commit
as the backstop. Python 3 standard library only.
"""
from __future__ import annotations

import glob
import os
import re
import shlex

INTERP = re.compile(r"^(python[\d.]*|node|nodejs|deno|bun|ruby|perl|php|osascript)$")
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
WRITE_VERBS = {"tee", "cp", "mv", "rm", "touch", "install", "ln", "rsync", "truncate", "dd", "sponge",
               "unlink", "rmdir", "ditto", "patch", "chmod", "mkdir"}
GIT_WRITES = {"checkout", "restore", "apply", "mv", "rm", "stash", "reset", "clean", "am", "cherry-pick"}
CODE_WRITE = re.compile(
    r"(writeFile|appendFile|createWriteStream|copyFile|renameSync|rename\(|unlink|rmSync|truncate|"
    r"write_text|write_bytes|\.write\(|\bwrite\b|shutil|os\.replace|os\.remove|os\.rename|"
    r"open\s*\([^,)]*,\s*(?:mode\s*=\s*)?['\"][^'\"]*[wax+]|File\.(?:write|open|delete)|file_put_contents|fopen|"
    r"\$>|>>|>\s*['\"]|\bsed\b.*-i|system\(|exec\(|spawn|subprocess|os\.system)")
LITERAL = re.compile(r"""(['"`])((?:\\.|(?!\1).)*)\1""")
NOISE = re.compile(r"(?:&>|\d*>>?)\s*/dev/(?:null|stderr|stdout)|\d*>&\d+")
SUBST = re.compile(r"\$\(\s*(?:echo|printf)\s+(?:-[a-zA-Z]+\s+)*([^()]*?)\s*\)|`\s*(?:echo|printf)\s+(?:-[a-zA-Z]+\s+)*([^`]*?)\s*`")
ASSIGN = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def _expand_braces(token: str) -> list[str]:
    m = re.search(r"\{([^{}]*,[^{}]*)\}", token)
    if not m:
        return [token]
    out: list[str] = []
    for alt in m.group(1).split(","):
        out.extend(_expand_braces(token[:m.start()] + alt + token[m.end():]))
    return out


def _resolve(path: str, cwd: str) -> str:
    path = os.path.expanduser(path)
    return os.path.normpath(path if os.path.isabs(path) else os.path.join(cwd, path))


def _expand(token: str, cwd: str) -> list[str]:
    """One token to absolute candidates: brace lists, then globs against the disk."""
    out: list[str] = []
    for tok in _expand_braces(token):
        absolute = _resolve(tok, cwd)
        if any(c in tok for c in "*?["):
            found = sorted(glob.glob(absolute))
            out.extend(found if found else [absolute])  # unmatched glob kept: callers fnmatch it
        else:
            out.append(absolute)
    return out


def _vars(text: str, env: dict[str, str]) -> str:
    return re.sub(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)\}?", lambda m: env.get(m.group(1), m.group(0)), text)


def _substitute(text: str, env: dict[str, str]) -> str:
    for _ in range(4):
        new = SUBST.sub(lambda m: re.sub(r"""['"]""", "", (m.group(1) or m.group(2) or "")).strip(), text)
        new = _vars(new, env)
        if new == text:
            break
        text = new
    return text


def _split_segments(command: str) -> list[tuple[str, str]]:
    """(segment text, heredoc/extra code) pairs. Heredoc bodies are lifted out and kept as code."""
    segments: list[tuple[str, str]] = []
    lines = command.split("\n")
    i = 0
    buf = ""
    while i < len(lines):
        line = lines[i]
        i += 1
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        body = ""
        if m:
            end = m.group(2)
            body_lines = []
            while i < len(lines) and lines[i].strip() != end:
                body_lines.append(lines[i])
                i += 1
            i += 1
            body = "\n".join(body_lines)
            line = line[:m.start()] + line[m.end():]
        segments.append((buf + line, body))
        buf = ""
    return segments


_QUOTED_OPS = {ord(c): 0xE000 + i for i, c in enumerate(";&|<>()")}


def _tokens(text: str) -> list[str]:
    # A quoted operator (`grep ">" file`) is an argument, not a redirect: mark it so it stays one.
    text = re.sub(r"""(['"])([;&|<>()]+)\1""", lambda m: "\x01" + m.group(2).translate(_QUOTED_OPS), text)
    lex = shlex.shlex(text, posix=True, punctuation_chars=";&|<>()")
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:
        return text.split()


def _code_candidates(code: str, cwd: str) -> list[str]:
    """String literals in interpreter code that sits next to a write call, resolved against cwd."""
    if not CODE_WRITE.search(code):
        return []
    code = re.sub(r"%[wWiI]([(\[{<])(.*?)[)\]}>]",
                  lambda m: " ".join("'" + w + "'" for w in m.group(2).split()), code, flags=re.S)  # Ruby %w()
    code = re.sub(r"%[qQ]?([(\[{<])(.*?)[)\]}>]", lambda m: "'" + m.group(2) + "'", code, flags=re.S)  # Ruby %q()
    folded = code
    for _ in range(3):
        folded = re.sub(r"""(['"])\s*\+\s*\1""", "", folded)                 # 'a'+'b' (same quote)
        folded = re.sub(r"""(['"])\s*\+\s*(['"])""", "", folded)              # 'a'+"b"
        folded = re.sub(r"""(['"])\s*\)?\s*/\s*(['"])""", "/", folded)         # Path('a')/'b'
        folded = re.sub(r"""(['"])\s*\)\s*\.\s*joinpath\s*\(\s*(['"])""", "/", folded)  # Path('a').joinpath('b')
    lits = [m.group(2) for m in LITERAL.finditer(folded)]
    for m in re.finditer(r"join\s*\(([^)]*)\)", folded):                       # join('a','b')
        parts = [x.group(2) for x in LITERAL.finditer(m.group(1))]
        if len(parts) > 1:
            lits.append("/".join(parts))
    for m in re.finditer(r"""(?:chdir|cwd\s*=|cd)\s*\(?\s*(['"])([^'"]+)\1""", folded):
        lits.extend([x + "/" + y for x in [m.group(2)] for y in [m2.group(2) for m2 in LITERAL.finditer(folded)]])
    out: list[str] = []
    for lit in lits:
        lit = _substitute(lit, {})
        if lit and len(lit) < 400 and "\n" not in lit:
            out.extend(_expand(lit, cwd))
    return out


def writes(command: str, cwd: str, _env: dict[str, str] | None = None, _depth: int = 0) -> list[str]:
    cwd = os.path.normpath(cwd)
    env = dict(_env or {})
    found: list[str] = []
    command = NOISE.sub(" ", command)
    for text, heredoc in _split_segments(command):
        text = _substitute(text, env)
        tokens = _tokens(text)
        # split on control operators, tracking cwd and assignments across segments
        group: list[str] = []
        groups: list[list[str]] = []
        for t in tokens:
            if t and set(t) <= set(";&|") :
                groups.append(group)
                group = []
            else:
                group.append(t)
        groups.append(group)
        for gi, g in enumerate(groups):
            body = heredoc if gi == len(groups) - 1 else ""
            cwd = _group(g, body, cwd, env, found, _depth)
    return found


def _group(g: list[str], body: str, cwd: str, env: dict[str, str], found: list[str], depth: int) -> str:
    g = [t for t in g if t not in ("(", ")", "{", "}")]
    # leading VAR=value assignments
    while g and ASSIGN.match(g[0]):
        k, v = ASSIGN.match(g[0]).groups()  # type: ignore[union-attr]
        env[k] = v
        g = g[1:]
    g = [_vars(t, env) for t in g]
    if not g:
        return cwd
    # wrappers that hand the real command on
    while g and os.path.basename(g[0]) in {"sudo", "env", "command", "exec", "nohup", "time", "xargs", "nice"}:
        g = [t for t in g[1:] if not t.startswith("-") or t == "-"] if os.path.basename(g[0]) != "env" else \
            [t for t in g[1:] if not t.startswith("-") and not ASSIGN.match(t)]
    if not g:
        return cwd
    cmd = os.path.basename(g[0])
    args = g[1:]
    if cmd in ("cd", "pushd"):
        if args:
            cwd = _resolve(args[0], cwd)
        return cwd
    # redirect targets are writes whatever the command is
    for i, t in enumerate(g):
        m = re.match(r"^\d*>>?(.*)$|^&>>?(.*)$", t)
        if t in (">", ">>", ">|", "&>") and i + 1 < len(g):
            found.extend(_expand(g[i + 1], cwd))
        elif m and (m.group(1) or m.group(2)) and not (m.group(1) or m.group(2)).startswith("&"):
            found.extend(_expand(m.group(1) or m.group(2), cwd))
    flags = [t for t in args if t.startswith("-")]
    operands = [t for t in args if not t.startswith("-") and t not in (">", ">>", "<", "<<")]
    if cmd in SHELLS or cmd == "eval":
        code = None
        if cmd == "eval":
            code = " ".join(args)
        else:
            for i, t in enumerate(args):
                if t.startswith("-") and "c" in t.lstrip("-") and i + 1 < len(args):
                    code = args[i + 1]
                    break
        if code is not None and depth < 3:
            found.extend(writes(code, cwd, env, depth + 1))
        if body and depth < 3:
            found.extend(writes(body, cwd, env, depth + 1))
        return cwd
    if INTERP.match(cmd):
        code = ""
        for i, t in enumerate(args):
            if t in ("-c", "-e", "-p", "-pe", "-pi", "--eval", "-r", "-E") and i + 1 < len(args):
                code += "\n" + args[i + 1]
        code += "\n" + body
        found.extend(_code_candidates(code, cwd))
        return cwd
    if cmd == "git":
        i = 0
        gcwd = cwd
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-C" and i + 1 < len(args):
                gcwd = _resolve(args[i + 1], gcwd)
                i += 1
            i += 1
        sub = args[i] if i < len(args) else ""
        if sub in GIT_WRITES:
            rest = [t for t in args[i + 1:] if not t.startswith("-")]
            for t in rest:
                found.extend(_expand(t, gcwd))
        return cwd
    if cmd == "sed" and any(f.startswith("-i") or f == "--in-place" or re.match(r"^-[a-zA-Z]*i", f) for f in flags):
        for t in operands:
            found.extend(_expand(t, cwd))
        return cwd
    if cmd == "perl" or cmd == "ruby":
        pass
    if cmd in WRITE_VERBS:
        for t in operands:
            found.extend(_expand(t, cwd))
        return cwd
    if cmd == "curl" or cmd == "wget":
        for i, t in enumerate(args):
            if t in ("-o", "-O", "--output", "-P") and i + 1 < len(args):
                found.extend(_expand(args[i + 1], cwd))
    return cwd
