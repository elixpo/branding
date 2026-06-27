# OG style — design prompt + text block

> Derived from the LOCKED reference **`references/OREO-LINEART.md`**. Keep this in
> sync with it; that page wins on any conflict.

The AI generates the **design only** (no text); we composite the type with
Pillow. So each card `.md` has **two** blocks:

```
## Prompt   →  the text-free DESIGN (fed to the image model, gptlarge, 16:9)
## Text     →  eyebrow / headline / sub / url  (drawn by pipeline/og_compose.py)
```

## Design style preamble (shared)

Paste this first, then the card's own `## Prompt` body.

> A **16:9** social-card **background design** (1280×720), editorial tech-
> minimalism — clean corporate design meets a modern web-architecture
> portfolio. Structured, intellectual, airy, with generous whitespace. Flat
> 2D vector only: NO 3D, NO gradients, NO glow, NO neon, NO drop shadows.
>
> **CRITICAL — NO TEXT.** Absolutely no words, letters, numbers, captions or
> typography anywhere in the image — EXCEPT the single letter "E" inside the
> panda's small chest badge. Leave the **entire left ~55%** as clean,
> almost-empty negative space (the headline is added later); place the
> artwork in the **right ~40%**, pushed to the right edge with a clear gap
> before the text zone.
>
> **Background:** white (`#ffffff`) covered edge-to-edge by a **faint dotted
> matrix** — a precise, evenly-spaced grid of tiny `#d9d9dd` dots (a halftone/
> pegboard dot field), very subtle, receding behind everything.
>
> **Mascot — Oreo as a TRUE single-line drawing:** ONE unbroken, flowing,
> hand-drawn **very thin** `#212121` line (a single pen stroke that never lifts)
> with only a few gentle loops — loose, minimal, elegant. This is **LINE ART**,
> **not** a polished, accurately-rendered or filled illustration: no solid
> fills, no detailed/shaded face, no smooth cartoon. The line forms a **cute,
> friendly** panda, round and plump in shape, its face **suggested minimally**
> (cute **gleamy, sparkling eyes** with a tiny white catch-light glint + a little smile), head turned **slightly left** toward the
> text. Make it **fairly large** and prominent, filling the
> **right ~40–42%**, pushed to the right edge and clear of the text zone. Confident and calligraphic, not a messy scribble: the
> tangles are deliberate and balanced, and the panda still reads instantly.
> Same crisp weight as the dot matrix. Both **ears** and **one leg** are filled flat coral `#ff7759`. Centred on its
> chest sits a **small, compact** round **red `#DC3C32` badge** (only a fraction
> of the chest) carrying a clean,
> bold, **stylish letter "E"** (Oreo's signature chest badge), crisp and
> aligned. The rest of the panda is the `#212121` line.
>
> **Geometry:** add **2–3 understated geometric shapes** — thin single-weight
> outlines in `#d9d9dd` hairline (no coral — coral stays on the panda): e.g. a large
> open circle, a triangle, a small square or a thin arc — placed with
> intent, partly overlapping the panda/dots, perfectly aligned like a design-
> system wireframe. They frame the mascot; they never fill or clutter.
>
> **Colour:** coral `#ff7759` (ears + one leg) and the red `#DC3C32` "E" badge are the only
> saturated colours, and appear **only on the panda**. Everything else — dots,
> shapes, line — is `#d9d9dd` hairline and `#212121` ink on white.

## Composition (the Pillow text lands here)

```
┌──────────────────────────────────────────────────────────┐ 16:9
│  EYEBROW (mono)                         ╱◯  entangled      │
│                                        │    one-line       │
│  Big Serif Headline                     ╲   Oreo + 2–3     │
│  ▆▆▆▆▆▆ (coral underline)                   geo shapes     │
│  sub copy (sans, slate)                                    │
│                                                            │
│  url (mono)                                                │
└──────────────────────────────────────────────────────────┘
   ← left ~55%: keep EMPTY in the AI design →   right ~45%: art
```

## `## Text` block format

```
## Text
eyebrow: ELIXPO · ACCOUNTS
headline: One sign-in for the whole Elixpo suite
sub: Single sign-on for every Elixpo app and your own SaaS.
url: accounts.elixpo.com
```

`og_compose.py` draws: eyebrow (Space Mono, tracked, muted slate) → bold
high-contrast **serif** headline (auto-fit, wrapped, ink) → heavy coral
underline → sub (Inter, slate) → url (mono, bottom-left). Drop
`Fraunces-Bold.ttf` / `SpaceMono-Regular.ttf` / `Inter-Regular.ttf` into
`pipeline/fonts/` to upgrade from the DejaVu fallbacks.
