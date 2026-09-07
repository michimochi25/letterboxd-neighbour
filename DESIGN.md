---
version: alpha
name: Letterboxd Neighbour
description: Companion UI for Letterboxd — dark, dense, poster-forward, colour only on data.
colors:
  background: "#14181c"
  on-background: "#d8e0e8"
  surface: "#2c3440"
  surface-bright: "#384250"
  on-surface: "#ffffff"
  on-surface-variant: "#99aabb"
  outline: "#445566"
  primary: "#00e054"
  on-primary: "#14181c"
  secondary: "#40bcf4"
  on-secondary: "#14181c"
  tertiary: "#ff8000"
  on-tertiary: "#14181c"
typography:
  metric-display:
    fontFamily: Graphik
    fontSize: 72px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Graphik
    fontSize: 36px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Graphik
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.2
  body-md:
    fontFamily: Graphik
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-caps:
    fontFamily: Graphik
    fontSize: 12px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0.08em
rounded:
  sm: 2px
  md: 4px
  full: 9999px
spacing:
  base: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  measure: 768px
components:
  score-dial:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.metric-display}"
    rounded: "{rounded.full}"
    padding: "{spacing.xl}"
  score-dial-low:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
  score-dial-high:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.on-secondary}"
  metric-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 0 20px
  button-primary-hover:
    backgroundColor: "#00c74a"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-background}"
    rounded: "{rounded.md}"
    height: 40px
  input-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: 40px
    padding: 12px
  poster:
    rounded: "{rounded.sm}"
    width: 80px
    height: 120px
  overlap-bar:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    height: 48px
  dialog:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-background}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
---

## Overview

A companion tool to Letterboxd, so it wears Letterboxd's clothes rather than
inventing its own: near-black blue-grey ground, small dense type, tight radii,
and saturated colour strictly on data — ratings, overlap, scores — never on
decoration. The product asks one question and answers it with one number, so
the score is the only element allowed to be loud.

Palette reconstructed from the Letterboxd interface (the site sits behind
Cloudflare and rejects non-browser clients) and corroborated by hex already
committed in `App.css` and `App.tsx`. Check individual greys in a browser before
treating them as exact.

## Colors

- **Background (#14181c):** The Letterboxd ground. There is no light theme —
  poster art and the accent trio are tuned for the dark.
- **Surface (#2c3440):** Cards, inputs, dialogs, bar tracks. `surface-bright`
  is its hover state, `outline` its 1px rule.
- **Primary (#00e054):** Letterboxd green — star ratings, the single CTA, the
  shared segment of the overlap bar.
- **Secondary (#40bcf4):** Letterboxd blue — links, the user-2 segment.
- **Tertiary (#ff8000):** Letterboxd orange — the user-1 segment, error text.

The trio doubles as a score band: tertiary 0–30, primary 31–60, secondary
61–100. The bands differ in hue, not lightness, so they read as identical to a
red-green colour-blind viewer — always print the numeral beside the fill, and
keep the thresholds in one `scoreTone()` helper rather than per component.

## Typography

Letterboxd sets its UI in **Graphik** (licensed, not bundled). Fall through to a
neo-grotesque system stack — `-apple-system, "Segoe UI", Roboto, "Helvetica
Neue", Arial, sans-serif` — so there is no webfont fetch and no layout shift.

Metrics use tabular figures and are the one loud element. Headings are sentence
case in two weights only, 400 and 700 — never 500 or 600. `label-caps` is the
Letterboxd signature: uppercase 12px at 0.08em tracking in `on-surface-variant`,
used for metric captions, table headers and legends. It is what keeps the chrome
quiet under a big number.

## Layout & Spacing

One centred column on a 4px scale, capped at `measure` so the dial, the overlap
bar and the disagreement table share a single width. Page padding `lg`, section
rhythm `xl`, gaps inside a card `sm`. Verified by eye at 375px, 768px and
1280px; `pnpm build` type-checks but sees nothing visual.

## Elevation & Depth

Flat. Hierarchy comes from the single surface step (#14181c → #2c3440) and 1px
`outline` rules, never shadows — the poster art supplies the contrast. The
dialog is the one exception: it sits over a `rgb(0 0 0 / 0.6)` scrim, and still
casts no shadow. Motion is 150ms ease-out on hover, 400ms for bar segments
growing to width, 0ms under `prefers-reduced-motion: reduce`.

## Shapes

Near-square. Posters take `sm`, everything rectangular takes `md`, and the score
dial alone is `full`. Posters are 2:3 with a `1px solid rgb(255 255 255 / 0.08)`
inset border so pale artwork does not bleed into the surface, and a 2px
`primary` outline on hover — the Letterboxd film-link affordance.

## Components

**Score dial.** The answer: a filled circle in the band colour with `on-primary`
ink. Its two inputs — taste match and library overlap — are `metric-card`
panels, not accent fills; three saturated fields side by side flattens the
hierarchy. Only the dial is filled.

**Button.** One primary per screen ("Compare Users"), disabled while loading
with the spinner inline in its label rather than stacked below the form.
`button-secondary` is for dialog dismissal only.

**Input.** Paired username fields of equal width with `vs.` between them set in
`label-caps`, not a heading. Focus is a `primary` border plus a
`0 0 0 2px rgb(0 224 84 / 0.25)` ring — never the browser default blue.

**Overlap bar.** Orange, green, blue for user-1-only, shared, user-2-only. A
count sits inside a segment only above 8% width; otherwise it lives in the
legend, and the tooltip carries the label as well as the value.

**Disagreement table.** Poster and title, then each user's stars in `primary`.
`label-caps` header, 1px `surface` dividers, last row unruled. Star groups need
an `aria-label` of the numeric rating — the repeated glyph is noise to a screen
reader. External links carry `rel="noreferrer"`.

**States.** Loading renders three `surface` skeletons at the dial, bar and table
positions so nothing jumps on arrival. Errors are `tertiary` text with
`role="alert"`. Empty is one `on-surface-variant` sentence.

## Do's and Don'ts

- Do put `on-primary` ink on every accent fill — white on #00e054 is 1.7:1 and
  fails AA at any size.
- Do declare these tokens once in `@theme` in `src/index.css`: no literal hex in
  JSX, and no second palette (`--primary: #2e294e` belongs to nothing here).
- Do keep the 70/30 weighting in the explainer dialog in sync with
  `calculate_similarity` in `backend/main.py` — one fact, two copies.
- Don't let colour be the only carrier of meaning; the numeral always shows.
- Don't reach for `slate-*`, `gray-*` or `red-*` utilities — all off-palette.
- Don't add shadows, a light theme, or a third font weight.
