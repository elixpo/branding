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
> **Mascot — Oreo the panda, as line art:** a minimalist, **continuous
> single-weight** line drawing of a friendly panda, strictly flat 2D,
> elegant and simplified, its outline the same crisp weight as the blueprint
> lines so it reads as part of the geometry. Small near-black (`#17171c`)
> fills for the eye-patches and ears; a small **coral `#ff7759` "E" badge**
> on the chest (this is what makes the panda *Oreo*). No fur texture, no
> shading — pure line.
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
