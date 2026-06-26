# prompts/og-image — Elixpo Mails OG / social cards

Open-graph (social share) cards for **Elixpo Mails** and the wider suite.
A deliberately different aesthetic from the pixel-art stickers: **editorial
tech minimalism** — crisp blueprint geometry, a single-weight **line-art**
take on Oreo the panda, generous whitespace, and a bold high-contrast serif
headline. Think high-end design-system wireframe, not glowing 3D tech.

```
prompts/og-image/<name>.md   →   og-image/<name>.png   (1200 × 630)
```

The site expects the default card at `public/og-image.png` (1200×630), so
the canonical render is [`default.md`](default.md) → `og-image/default.png`
→ copied to each app's `public/og-image.png`.

## Palette — the "oreo" (Cohere/coral) system

These are the exact tokens from `mail.elixpo/app/globals.css`. OG cards use
the **light** theme only. See [`palette.json`](palette.json).

| Token | Hex | Role on the card |
|---|---|---|
| Canvas | `#ffffff` | Background |
| Soft canvas | `#faf9f6` | Optional warm panel |
| Ink | `#212121` | Headline serif type |
| Slate | `#75758a` | Body / sub copy |
| Muted slate | `#93939f` | Eyebrow / mono labels |
| Hairline | `#d9d9dd` | Blueprint grid + structural lines |
| Card border | `#f2f2f2` | Faint inner grid |
| **Coral (accent)** | `#ff7759` | Underline, E-badge, key nodes |
| Soft coral | `#ffad9b` | Secondary accent / fills |
| Near-black | `#17171c` | Panda patches (eyes/ears) |
| Action blue | `#1863dc` | Optional secondary accent |

## Typography

- **Headline** — a bold, high-contrast **serif** (editorial): _Fraunces_,
  _Playfair Display_, or similar. This is the one intentional departure
  from the brand display font (Space Grotesk) — OG cards read as a
  magazine cover.
- **Eyebrow / labels / URL** — **Space Mono**, uppercase, wide tracking
  (matches the brand mono).
- **Body** — Inter (brand sans).

## Art direction (the rules)

1. **Editorial tech minimalism** — structured, intellectual, airy. Generous
   whitespace. NO 3D gradients, NO glow, NO neon.
2. **Blueprint geometry** — thin, crisp, single-weight `#d9d9dd` vector
   lines forming a precise background grid + a few structural / measurement
   lines (ticks, crop marks, alignment guides). Everything aligned to a
   wireframe.
3. **One-line Oreo** — **ONE continuous, unbroken thin line** (a true
   continuous-line / one-line drawing) that *suggests* the panda's facade —
   head curve, one folded ear, a single spiral eye, a hint of snout — then
   flows out into a long **horizon line** that ties into the grid. NOT a
   detailed full face, no closed shapes, no shading. Exactly **one small
   coral `#ff7759` patch** (a single filled ear) is the only colour on the
   mascot — it stands in for Oreo's badge (see `ref/MASCOT.md`).
4. **Type** — bold serif headline with a **heavy coral underline** or a
   structured text container for emphasis.
5. **Coral is the only saturated colour.** Use it sparingly — underline,
   badge, one or two grid nodes. The rest is ink / slate / hairline on
   white.

## Generate

```bash
# single card
python tools/generate_assets.py --og default
# all og cards
python tools/generate_assets.py --og
```

(If the `--og` flag isn't wired in `generate_assets.py` yet, the prompt
files still stand alone — paste the `## Prompt` block into any 1200×630
image model, or hand-render from [`og-default.svg`](og-default.svg).)

## Files

| File | What |
|---|---|
| [`STYLE.md`](STYLE.md) | The shared style preamble reused by every prompt |
| [`palette.json`](palette.json) | Machine-readable palette + type tokens |
| [`default.md`](default.md) | Default / home card (→ `public/og-image.png`) |
| [`features.md`](features.md) | Capabilities / product card |
| [`workspace.md`](workspace.md) | Team workspaces card |
| [`docs.md`](docs.md) | Documentation card |
| [`pricing.md`](pricing.md) | Pricing card |
| [`og-default.svg`](og-default.svg) | Hand-built reference render, fully editable |
