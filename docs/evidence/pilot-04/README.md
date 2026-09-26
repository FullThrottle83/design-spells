# Pilot 04 browser evidence

Actual Chromium captures at 1440×900 and 390×844, with client JavaScript disabled.

- [Before contact sheet](before-contact-sheet.png) and [raw measurements](before-observations.json)
- [After contact sheet](after-contact-sheet.png) and [raw measurements](after-observations.json)

Each spell has initial, genuinely activated and simulated no-anchor-support
(fallback) captures. Before the change ds-79's activated capture showed a closed
menu, ds-89's menu rendered detached at the viewport's top-left corner, and
ds-142 showed a grey placeholder with tofu glyph pins. Contact sheets are
rebuilt deterministically from the raw captures with
`scripts/pilot04_contact_sheet.py` (optional Pillow utility, not part of the
build). These screenshots do not establish assistive-technology behavior or
cross-browser support.
