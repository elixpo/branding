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
> **Mascot — Oreo as ONE continuous line:** a single, unbroken, **confident
> thin line** — a clean, recognisable **continuous-line / one-line drawing**
> in the style of a premium minimalist logo — depicting a **resting panda in
> profile / three-quarter view**. One smooth stroke traces the head curve,
> one rounded ear, a single small spiral eye, a soft snout, and then glides
> out into a long **horizontal horizon line** that ties into the grid. It
> must read **clearly and immediately as a panda** — elegant, balanced and
> deliberate, **not abstract, not scribbled**; the line should not tangle or
> cross itself messily. Strictly flat 2D, same weight as the blueprint
> lines, no shading, no closed detailed face.
>
> Exactly **ONE small coral `#ff7759` patch** marks a **single ear** — a
> small flat fill sitting **flush inside the silhouette**, NOT a separate
> ball/disc floating on top of the line. It is the only colour on the
> mascot and stands in for Oreo's badge. No second colour.
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
