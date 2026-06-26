# OG style preamble (shared)

Every `og-image/*.md` prompt is built as:

```
<STYLE PREAMBLE>  +  <card-specific HEADLINE / SUBJECT>
```

Paste this block first, then the card's own `## Prompt` body.

## Style preamble

> A 1200×630 open-graph social card in an **editorial tech-minimalism**
> style — clean corporate design meets a modern web-architecture portfolio.
> The mood is structured, intellectual and airy, with **generous
> whitespace**. Flat 2D vector art only: absolutely **no 3D, no gradients,
> no glow, no neon, no drop shadows**.
>
> **Background:** pure white (`#ffffff`). Behind everything, a subtle,
> precise **blueprint grid** of thin, crisp, single-weight `#d9d9dd` lines —
> evenly spaced, perfectly aligned, like a high-end design-system wireframe.
> Add a few understated structural details in the same hairline weight:
> alignment guides, small measurement ticks, and corner crop-marks. The grid
> must stay faint and recede behind the content.
>
> **Accent:** a single saturated **coral `#ff7759`**, used sparingly — one
> heavy underline, a small badge, and one or two grid node dots. Everything
> else is `#212121` ink, `#75758a` slate, and `#d9d9dd` hairline on white.
>
> **Mascot — Oreo as ONE continuous line:** a single, unbroken, thin
> single-weight line — a true **continuous-line / one-line drawing** — that
> *suggests* the facade of a panda rather than rendering a full detailed
> face. With one calligraphic stroke: the curve of the head, one folded
> ear, a single spiral for the eye, the hint of a snout/cheek, and then the
> same line flowing out into a long **horizontal horizon line** that ties
> into the grid. Elegant, minimal, calligraphic, strictly flat 2D, no
> shading, no closed pixel-art face. Its weight matches the blueprint lines.
> Add exactly **ONE small coral `#ff7759` patch** — a single filled ear or a
> small soft blob — the only colour on the mascot, standing in for Oreo's
> badge. No second colour.
>
> **Typography:** the headline is set in a **bold, high-contrast serif**
> (editorial, magazine-cover feel) in ink `#212121`, with a **thick coral
> underline** or a crisp outlined container for emphasis. Eyebrow labels and
> any URL are **Space Mono**, uppercase, wide letter-spacing, in muted slate
> `#93939f`. Layout is balanced and grid-aligned: text block on the left,
> the line-art panda anchored on the right, breathing room around both.

## Composition grid

```
┌─────────────────────────────────────────────────────────┐  ← crop marks
│  • mark   ELIXPO · MAILS              ┌───────────────┐  │  eyebrow (mono)
│                                       │  line-art     │  │
│  Big Serif Headline                   │   Oreo panda  │  │  headline + panda
│  ═══════════════  (coral underline)   │  (single wt)  │  │
│  sub copy in slate                    └───────────────┘  │
│                                                           │
│  mails.elixpo.com           · · ·   (coral grid nodes)    │  footer (mono)
└─────────────────────────────────────────────────────────┘
```

- Safe margin: keep all type ≥ 60px from every edge.
- Headline cap-height ≈ 96–120px. One or two lines max.
- Panda occupies the right ~32% of the width, vertically centered.
