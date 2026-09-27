# Pilot 05 browser evidence

Actual Chromium captures at 1440×900 and 390×844, with client JavaScript disabled.

- [Before contact sheet](before-contact-sheet.png) and [raw measurements](before-observations.json)
- [After contact sheet](after-contact-sheet.png) and [raw measurements](after-observations.json)

Each spell has initial, genuinely activated, simulated no-`@starting-style`
(fallback) and reduced-motion activated captures. Before the change the ds-75
thumbnail and its enlarged view were different gradients and the enlarged view
rendered 0×0; ds-77's sheet clipped its Done action on short viewports; ds-66
and ds-106 opened without backdrop treatment or teaching copy. Contact sheets
are rebuilt deterministically from the raw captures with
`scripts/pilot05_contact_sheet.py` (optional Pillow utility, not part of the
build). These screenshots do not establish assistive-technology behavior or
cross-browser support.
