---
name: design-steward
description: A role that delivery-orchestrator brings in. Own a project's design language so UI and UX changes stay coherent. The project's design baseline (decision record, design-system doc, platform guideline checklist with dated quotes, token files) is the authority; this role applies it before, during and after every UI change and demands proof (token-only values, a pixel-comparing visual gate, a probe or grep per rule, recorded deviations). Use on any UI/UX ask - a panel, screen, menu, settings page, widget or theme - and when reviewing one. Also use on "make it look right", "design language", "HIG", "Material", "tokens", "inconsistent UI".
---

# Design steward

One rule: **a UI change is done only when it uses the baseline's tokens and components, and
a probe, grep or pixel render proves it.** The values live in the project's records. This
skill is the method for applying them. Never copy a value from here into code or a brief;
read it from the records each time.

## When to use

- Any change to a visible surface: screen, panel, popover, menu, settings page, widget, theme.
- Writing or briefing UI work for another agent; reviewing a UI change.
- A project has no design baseline yet and the team is about to build UI.

## The design baseline (the authority)

Find these in the project profile's "Design baseline" row. Read in this order:

| Record | Answers |
|---|---|
| Decision record (ADR) | Why the design is what it is; what was decided, by whom, when |
| Design-system doc | Tokens, components, hierarchy, copy rules, commands, the proof probes |
| Platform guideline checklist | Each platform guideline quoted with its read date, what the project does, the proof |
| Token files | The only place a size, spacing, radius or colour is written as a number |
| Floors (accessibility, contrast, type) | Never weakened by a design change |

If a record is missing, the first change is to create it (decision record first, reviewed
like any ADR). Do not build UI on an unwritten language.

## Before you change anything

1. Name the surface and find its section in the design-system doc. No section means the doc
   changes first, reviewed like an ADR.
2. Name the issue. A design change outside an issue is not started.
3. Check every platform claim against the checklist. A guideline not quoted there with a
   read date is fetched from the platform's own page and added as a row in the same change.
   Never cite a guideline from memory. Where the platform publishes no number, measure it
   from a system surface and commit the measurement.
4. Pick the reference for the platform from [references](references/platforms.md).

## While you build

- **Tokens only.** No literal size, spacing, frame, radius or colour outside the token
  files. A new value is a new token named for its role, added to the design-system doc.
- **Components, not one-offs.** Reuse the existing row, chip, popover, header, button
  hierarchy, empty state and help-text rules. A second way to draw the same thing is a finding.
- **Hierarchy first.** What needs attention, then the headline figure, then facts, then
  provenance. Detail goes in a secondary surface, not on the primary one.
- **Words.** One noun per concept. Legends and footnotes become the tooltip or detail of
  what they explain.
- **Commands.** A new action joins the one command model in every menu, or in none.
- **Accessibility is design.** Spoken-label sentence, status by shape and word as well as
  colour, keyboard reach, the type floor.
- **Platforms.** Each renderer may use its own controls and fonts; they share content,
  hierarchy, status shapes, palette roles and the spacing scale through the token source.

## Proof (what the PR must show)

| Change | Proof |
|---|---|
| Any visual change | The pixel-comparing visual gate passes against references refreshed in the same PR, light and dark; reference images reviewed by eye. A gate that compares only image size proves nothing |
| Token or layout | The design-system doc's probe line for it, asserted in a test |
| Literal values | The literal ratchet (`scripts/literal_ratchet.py`, opt-in via `operating-model-bootstrap --adopt ratchet-config`) shows no count rose |
| New rule | A test that fails without the change (prove-it-bites receipt in the PR body) |
| Platform guideline | The checklist row updated: status, file:line, proof |
| Deviation from the platform | Recorded in the checklist as **Deviation** with the reason and the deciding record |

Run the project's full gate on the exact head. A green suite that never renders or probes
the changed surface proves nothing.

## Review checklist (independent reviewer)

1. Does the change match its design-system section, and is any superseded text removed?
2. Any literal size, spacing, radius or colour outside the token files?
3. Any second implementation of an existing component?
4. Do the references show the change in light and dark, and does the pixel gate bite?
5. Is every platform claim quoted in the checklist with a date and a proof?
6. Are spoken labels, status shapes, contrast floors and the type floor intact?
7. Does the surface still read in the order attention, headline, facts, provenance?

## Opt-in harness

`operating-model-bootstrap --adopt ui-context` reminds the agent once per session to load
this skill on UI paths; `--adopt post-edit-ratchet` blocks a literal regression with
file:line at the edit. Both are copied on request only, never enabled globally, and answer
allow or deny, never ask.

## What this skill does not do

It grants no authority, changes no gate, and does not replace the issue's Definition of Done
or the project's review routing. Builders do not edit ROADMAP, STATUS or CHANGELOG unless the
project's records rule says so.

## Entry and proof

- **Entry:** `delivery-orchestrator` brings this role in. Enter here directly only for a bounded read-only question.
- **Proof:** `scripts/literal_ratchet.py` (literal counts never rise) plus the project's visual gate and per-rule probes.
