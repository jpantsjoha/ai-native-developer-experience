#!/usr/bin/env python3
"""Measure which skill a host loads first for a fixed set of persona prompts.

Skill selection is a model decision, so the result is a rate, not a guarantee.
Each prompt runs headless in a copy of the fixture consumer with only this
checkout's skills available. On Claude Code the checkout is the only plugin and writes
and shell are denied. On Codex the skills sit at project scope, the Codex home is empty
apart from the sign-in, and the sandbox is read-only; Codex has no session-start hook.

    python3 scripts/routing_eval.py --label before --out evals/routing/results
"""
import argparse
import concurrent.futures
import datetime
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'devex-charter:'
ORIENTATION = 'using-the-harness'
VALID_ENDINGS = ('success', 'error_max_turns')
SKILL_FILE = re.compile(r'skills/([a-z0-9-]+)/SKILL\.md')


RAW_DIR = None


def keep_raw(case: dict, stream: str) -> None:
    """Keep the host's event stream when --raw names a directory, so a run can be rescored."""
    if RAW_DIR:
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        (RAW_DIR / f"{case['id']}.jsonl").write_text(stream)


def parse_stream(stream: str) -> dict:
    """Return the charter skills that loaded successfully, in order, and how the run ended.

    A Skill call whose tool result is an error did not load and is listed under failed.
    """
    calls, errored, ending = [], set(), None
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get('type')
        if kind == 'result':
            ending = event.get('subtype')
            continue
        content = event.get('message', {}).get('content', []) if kind in ('assistant', 'user') else []
        for block in content if isinstance(content, list) else []:
            if kind == 'assistant' and block.get('type') == 'tool_use' and block.get('name') == 'Skill':
                name = str(block.get('input', {}).get('skill', ''))
                calls.append((block.get('id'), name.removeprefix(PREFIX)))
            elif kind == 'user' and block.get('type') == 'tool_result' and block.get('is_error'):
                errored.add(block.get('tool_use_id'))
    return {
        'loaded': [name for call_id, name in calls if call_id not in errored],
        'failed': [name for call_id, name in calls if call_id in errored],
        'ending': ending,
    }


def parse_codex_stream(stream: str, known: set) -> dict:
    """Codex has no skill tool: a skill loads when a command reads its SKILL.md.

    Skills read by one command are listed in the order the command names them. A skill
    counts as loaded when its frontmatter name appears in the command's output, whatever
    the exit code: one missing file makes a combined read exit non-zero.
    """
    loaded, failed, ending = [], [], None
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'turn.completed':
            ending = 'success'
        elif event.get('type') in ('turn.failed', 'error'):
            ending = ending or 'error'
        item = event.get('item') or {}
        if event.get('type') != 'item.completed' or item.get('type') != 'command_execution':
            continue
        output = str(item.get('aggregated_output', ''))
        for name in SKILL_FILE.findall(str(item.get('command', ''))):
            if name in known:
                (loaded if f'name: {name}\n' in output else failed).append(name)
    return {'loaded': loaded, 'failed': failed, 'ending': ending}


def score(case: dict, parsed: dict, entry: str) -> dict:
    """Score one case. A run that did not end normally scores no hit and counts as invalid."""
    valid = parsed['ending'] in VALID_ENDINGS
    loaded = parsed['loaded'] if valid else []
    chosen = [name for name in loaded if name != ORIENTATION]
    first = chosen[0] if chosen else None
    return {
        'id': case['id'], 'persona': case['persona'], 'direct_ok': case['direct_ok'],
        'loaded': parsed['loaded'], 'failed_loads': parsed['failed'], 'ending': parsed['ending'],
        'valid': valid, 'first': first,
        'orchestrator_first': first == entry,
        'direct_specialist': case['direct_ok'] and first == case['role'],
        'role_reached': case['role'] in chosen,
        'no_skill_after_orientation': valid and first is None,
        'no_skill_at_all': valid and not loaded,
    }


def run_claude(case: dict, consumer: Path, plugin_dir: Path, model: str, max_turns: int) -> dict:
    command = [
        'claude', '-p', case['prompt'], '--plugin-dir', str(plugin_dir),
        '--setting-sources', 'project', '--strict-mcp-config',
        '--output-format', 'stream-json', '--verbose', '--model', model,
        '--max-turns', str(max_turns), '--disallowedTools', 'Write', 'Edit', 'Bash',
    ]
    done = subprocess.run(command, cwd=consumer, text=True, capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=420, check=False)
    keep_raw(case, done.stdout)
    return parse_stream(done.stdout)


def run_codex(case: dict, consumer: Path, plugin_dir: Path, model: str, home: Path) -> dict:
    """Skills at project scope, read-only sandbox, and an empty Codex home (sign-in only).

    HOME is replaced too, so user skills under ~/.agents/skills cannot take part.
    """
    (consumer / '.agents').mkdir()
    shutil.copytree(plugin_dir / 'skills', consumer / '.agents/skills')
    subprocess.run(['git', 'init', '-q'], cwd=consumer, check=False)
    codex_home = home / 'codex-home'
    codex_home.mkdir()
    source = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'auth.json'
    (codex_home / 'auth.json').symlink_to(source)
    command = ['codex', 'exec', '--json', '--skip-git-repo-check', '-s', 'read-only',
               '-m', model, '-c', 'model_reasoning_effort=medium', case['prompt']]
    done = subprocess.run(command, cwd=consumer, text=True, capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=600, check=False,
                          env=dict(os.environ, CODEX_HOME=str(codex_home), HOME=str(home)))
    known = {path.parent.name for path in (plugin_dir / 'skills').glob('*/SKILL.md')}
    keep_raw(case, done.stdout)
    return parse_codex_stream(done.stdout, known)


def run_case(case: dict, plugin_dir: Path, model: str, max_turns: int, entry: str, host: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        consumer = Path(tmp) / 'consumer'
        shutil.copytree(ROOT / 'evals/routing/fixture', consumer)
        try:
            if host == 'codex':
                parsed = run_codex(case, consumer, plugin_dir, model, Path(tmp))
            else:
                parsed = run_claude(case, consumer, plugin_dir, model, max_turns)
        except subprocess.TimeoutExpired:
            parsed = {'loaded': [], 'failed': [], 'ending': 'timeout'}
    return score(case, parsed, entry)


def git(plugin_dir: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(plugin_dir), *args], text=True,
                          capture_output=True, check=False).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--plugin-dir', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, default=ROOT / 'evals/routing/results')
    parser.add_argument('--host', choices=('claude-code', 'codex'), default='claude-code')
    parser.add_argument('--model', help='default: sonnet on claude-code, gpt-6.1-sol on codex')
    parser.add_argument('--max-turns', type=int, default=4)
    parser.add_argument('--raw', type=Path, help='directory for raw event streams (not committed)')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()

    global RAW_DIR
    RAW_DIR = args.raw
    args.model = args.model or ('gpt-6.1-sol' if args.host == 'codex' else 'sonnet')
    spec = json.loads((ROOT / 'evals/routing/prompts.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(
            lambda case: run_case(case, args.plugin_dir.resolve(), args.model, args.max_turns, spec['entry'], args.host),
            spec['prompts']))
    total = len(results)
    count = lambda key: sum(bool(r[key]) for r in results)
    dirty = bool(git(args.plugin_dir, 'status', '--porcelain', 'skills', 'hooks'))
    report = {
        'label': args.label, 'host': args.host, 'model': args.model,
        'max_turns': args.max_turns if args.host == 'claude-code' else None,
        'date': datetime.date.today().isoformat(),
        'commit': git(args.plugin_dir, 'rev-parse', 'HEAD'),
        'skills_tree': git(args.plugin_dir, 'rev-parse', 'HEAD:skills'),
        'hooks_tree': git(args.plugin_dir, 'rev-parse', 'HEAD:hooks'),
        'skills_dirty': dirty,
        'prompt_set_version': spec['version'], 'total': total,
        'valid_runs': count('valid'),
        'orchestrator_first': count('orchestrator_first'),
        'direct_specialist': count('direct_specialist'),
        'role_reached': count('role_reached'),
        'no_skill_after_orientation': count('no_skill_after_orientation'),
        'no_skill_at_all': count('no_skill_at_all'),
        'results': results,
    }
    if dirty:
        print('WARNING: skills or hooks have uncommitted changes; this result is not bound to a commit')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / f"{args.label}.json").write_text(json.dumps(report, indent=2) + '\n')
    for r in results:
        print(f"{r['id']:7} {r['ending']} first={r['first']} loaded={r['loaded']} failed={r['failed_loads']}")
    print(' '.join(f"{key}={report[key]}/{total}" for key in (
        'valid_runs', 'orchestrator_first', 'direct_specialist', 'role_reached',
        'no_skill_after_orientation', 'no_skill_at_all')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
