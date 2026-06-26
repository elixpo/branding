# OG style — design prompt + text block

The AI generates the **design only** (no text); we composite the type with
Pillow. So each card `.md` has **two** blocks:

```
## Prompt   →  the text-free DESIGN (fed to the image model, gptlarge, 16:9)
## Text     →  eyebrow / headline / sub / url  (drawn by tools/og_compose.py)
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
> artwork in the **right ~45%**.
>
> **Background:** white (`#ffffff`) covered edge-to-edge by a **faint dotted
> matrix** — a precise, evenly-spaced grid of tiny `#d9d9dd` dots (a halftone/
> pegboard dot field), very subtle, receding behind everything.
>
> **Mascot — Oreo as an ENTANGLED one-line drawing:** a single, unbroken,
> thin `#212121` line — one continuous-line / one-line drawing — that loops,
> overlaps and **entangles** elegantly to form a clearly recognisable panda
> on the right. Confident and calligraphic, not a messy scribble: the
> tangles are deliberate and balanced, and the panda still reads instantly.
> Same crisp weight as the dot matrix. Colour the panda with coral `#ff7759` **only**: both **ears** and **one leg**
> are filled flat coral, and a small round badge bearing a clean letter
> **"E"** sits on its chest (Oreo's signature badge). The rest of the panda
> is the `#212121` line.
>
> **Geometry:** add **2–3 understated geometric shapes** — thin single-weight
> outlines in `#d9d9dd` hairline (no coral — coral stays on the panda): e.g. a large
> open circle, a triangle, a small square or a thin arc — placed with
> intent, partly overlapping the panda/dots, perfectly aligned like a design-
> system wireframe. They frame the mascot; they never fill or clutter.
>
> **Colour:** coral `#ff7759` is the ONLY saturated colour and appears **only on the panda**
> (both ears, one leg, and the "E" chest badge). Everything else — dots,
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
eyebrow: ELIXPO · MAILS
headline: Event-based transactional email
sub: Bring your own sender · design · send one-time or by webhook.
url: mails.elixpo.com
```

`og_compose.py` draws: eyebrow (Space Mono, tracked, muted slate) → bold
high-contrast **serif** headline (auto-fit, wrapped, ink) → heavy coral
underline → sub (Inter, slate) → url (mono, bottom-left). Drop
`Fraunces-Bold.ttf` / `SpaceMono-Regular.ttf` / `Inter-Regular.ttf` into
`tools/fonts/` to upgrade from the DejaVu fallbacks.
