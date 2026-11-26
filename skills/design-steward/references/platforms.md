# Platform guideline sources

Fetch each guideline from the platform's own page, quote it in the project's checklist with
the **read date**, and never cite from memory. Guidance changes between releases; a quote
without a date is a finding. Where the platform publishes no number for your case (for
example a desktop margin), measure it from a system surface and commit the measurement.

| Platform | Where to fetch | Name the checklist rows by |
|---|---|---|
| Apple HIG (macOS, iOS, widgets) | developer.apple.com/design/human-interface-guidelines. The page data is also served as DocC JSON at `developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`. For widgets read the Widgets page; also Typography, Color, Layout, Accessibility | Page name and section heading |
| Material Design 3 | m3.material.io (foundations, styles, components). Design tokens are in the Material token reference there | Component or foundation name, token role |
| GNOME HIG | developer.gnome.org/hig | Pattern name (for example Navigation, Typography, Dark style) |
| KDE HIG | develop.kde.org/hig | Page name and section |

## Checklist row shape

```text
| Source (page, section) | Read date | Quote (short) | What the project does | Status | Proof (file:line or test) |
```

Status is one of: Met, Partial, Deviation (with reason and deciding record), Not applicable.

## Rules

- One row per guideline the project relies on. A guideline not relied on needs no row.
- Quote briefly; link the page. Do not paste whole pages.
- Re-read and re-date a row when the platform ships a major release or the project targets
  a new OS version.
- Cross-platform projects keep one checklist section per platform plus one shared token source.
