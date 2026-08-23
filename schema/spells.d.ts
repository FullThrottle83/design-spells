/**
 * Design Spells — strict TypeScript contract for the catalogue.
 *
 * This is the interface AI agents and editors should code against when
 * integrating spells. It mirrors schema/spells.schema.json and the output of
 * scripts/build.py (public/spells.json / public/spells.js).
 *
 * Refer to spells by their stable `id` (e.g. "ds-43"). Selection priority:
 * Baseline -> Newer -> Progressive. Never add client JS for something a
 * spell already solves with zero JS.
 */

export type BrowserLevel = "yes" | "partial" | "no";

export type Status = "baseline" | "newer" | "progressive";

export type StatusLabel = "Baseline" | "Newer" | "Progressive";

/** "none" = zero JS. "markup" = zero JS but needs a native HTML pattern
 *  (details, checkbox, popover, dialog, etc.). */
export type JsNeed = "none" | "markup";

export type JsLabel = "0 JS" | "Markup";

export type PreviewEnvironment = "shadow" | "document";

export type PreviewActionKind =
  | "none"
  | "invalid-input"
  | "activate-control"
  | "toggle-disclosure"
  | "adjust-range"
  | "scroll"
  | "resize"
  | "swipe"
  | "activate-link"
  | "select-text"
  | "toggle-control"
  | "hover-or-focus"
  | "hover"
  | "keyboard-focus"
  | "focus"
  | "press";

export interface PreviewAction {
  kind: PreviewActionKind;
  hint: string;
}

export interface BrowserSupport {
  chrome: BrowserLevel;
  edge: BrowserLevel;
  firefox: BrowserLevel;
  safari: BrowserLevel;
}

export interface Spell {
  /** Stable identifier, e.g. "ds-43". */
  id: string;
  /** Canonical number (e.g. "43") or "bonus". */
  number: string;
  title: string;
  /** Top-level section in the source document. */
  section: string;
  /** Normalised functional category used for filtering. */
  category: string;
  /** Category as authored in the source document. */
  rawCategory: string;
  status: Status;
  statusLabel: StatusLabel;
  jsNeed: JsNeed;
  jsLabel: JsLabel;
  note: string;
  description: string;
  /** Required markup (may be empty for CSS-only spells). */
  html: string;
  /** The modern-CSS source to copy. */
  css: string;
  /** Isolation model used by the live preview. */
  previewEnvironment: PreviewEnvironment;
  /** Trigger metadata and interaction guidance. */
  previewAction: PreviewAction;
  /** Self-contained markup used by the live preview. */
  previewHtml: string;
  /** Preview CSS with :root/html/body rewritten to :host. */
  previewCss: string;
  /** All detected compatibility feature keys in registry order. */
  featureKeys: string[];
  /** Summary of the CSS features the spell depends on. */
  feature: string;
  browsers: BrowserSupport;
  /** Detailed browser-support note, including versions where relevant. */
  supportNote: string;
}

export interface Catalogue {
  /** UTC date on which the browser-support registry was verified. */
  supportAsOf: string;
  total: number;
  spells: Spell[];
}
