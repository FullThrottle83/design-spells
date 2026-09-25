# Integration bundles

The canonical README remains the source of spell HTML/CSS. The build generates
`/bundle/ds-N.txt` for every spell, in addition to the existing runnable demo
`/download/ds-N.html`. Bundles are intentionally generated and not tracked.

**Bundle** is a copyable HTML starting point. It contains the spell's original CSS,
authored HTML where available, and only recursively referenced variables from the
shared demo token registry. CSS-only spells use an explicitly marked **demo fixture**,
not a claim that the fixture is required markup. Unknown project variables are
listed in a CSS comment; provide them or check their `var()` fallbacks. Root
scroll-state presets are included only for ds-43 and ds-47.

Bundle source does not include catalogue styling, full resets, fonts, browser
polyfills, remote media, or working application behavior behind illustrative
buttons/links. Document-wide effects (ds-14, ds-143) are labelled as such;
the cross-document transition requires both downloadable demo files. Nothing
in this export promotes browser-support or WCAG verification status.

The classic catalogue and individual spell documentation pages expose a native
**View integration source** link that works without scripting. Their optional
**Copy integration bundle** buttons fetch exactly that plain-text document and
report success only after the clipboard write succeeds. On individual docs,
the copy enhancement is served separately by `/spell-copy.js`; the hosted
demo, runnable download and exported integration source remain script-free.
Document-level spells ds-14 and ds-143 retain their native source links
without a copy button because their behavior cannot be represented by a
single integration snippet. Raw CSS and the existing stack-of-snippets path
remain raw, with their own labels; they are not represented as dependency-
resolved exports. The MCP `get_spell` response includes the corresponding
`integrationBundleUrl` and `integrationBundleFormat`.

Build: `npm run build`. Test: `npm test` and the separate Firefox/WebKit suite.
