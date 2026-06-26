# prompts/og-image — Elixpo Mails OG / social cards

Open-graph (social share) cards for **Elixpo Mails** and the wider suite.
A deliberately different aesthetic from the pixel-art stickers: **editorial
tech minimalism** — crisp blueprint geometry, a **one-line** take on Oreo the
panda, generous whitespace, and a bold high-contrast serif headline. Think
high-end design-system wireframe, not glowing 3D tech.

## Structure — one folder per site

Each site gets its own folder of prompts plus an `output/` folder that holds
the rendered PNGs:

```
prompts/og-image/<site>/<name>.md  →  prompts/og-image/<site>/output/<name>.png   (1200 × 630)

prompts/og-image/
└── mails.elixpo/          ← the first site
    ├── STYLE.md           ← shared style preamble
    ├── palette.json       ← palette + type tokens
    ├── default.md  features.md  workspace.md  docs.md  pricing.md
    └── output/            ← generated cards land here
```

Each site expects its default card at `public/og-image.png` (1200×630), so
the canonical render is `<site>/default.md` → `<site>/output/default.png` →
copied to that app's `public/og-image.png`.

To **add a site**, copy `mails.elixpo/` to `prompts/og-image/<newsite>/`,
adjust the headlines/URLs in its prompts, and run `--og <newsite>`.

## Palette — the "oreo" (Cohere/coral) system

These are the exact tokens from `mail.elixpo/app/globals.css`. OG cards use
the **light** theme only. See [`mails.elixpo/palette.json`](mails.elixpo/palette.json).

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

The cards are **AI-generated from these prompts** by the repo generator
(`tools/generate_assets.py`, Pollinations `gptimage`, 1200×630, no
transparency pass):

```bash
python tools/generate_assets.py --og                       # every site, every card
python tools/generate_assets.py --og mails.elixpo          # one site, all cards
python tools/generate_assets.py --og mails.elixpo default  # one card
python tools/generate_assets.py --og --seed 7              # try a different seed
```

Output lands in each site's `output/` folder. Copy
`mails.elixpo/output/default.png` → that app's `public/og-image.png`.

## Files (per site, e.g. `mails.elixpo/`)

| File | What |
|---|---|
| [`mails.elixpo/STYLE.md`](mails.elixpo/STYLE.md) | The shared style preamble reused by every prompt |
| [`mails.elixpo/palette.json`](mails.elixpo/palette.json) | Machine-readable palette + type tokens |
| [`mails.elixpo/default.md`](mails.elixpo/default.md) | Default / home card (→ `public/og-image.png`) |
| [`mails.elixpo/features.md`](mails.elixpo/features.md) | Capabilities / product card |
| [`mails.elixpo/workspace.md`](mails.elixpo/workspace.md) | Team workspaces card |
| [`mails.elixpo/docs.md`](mails.elixpo/docs.md) | Documentation card |
| [`mails.elixpo/pricing.md`](mails.elixpo/pricing.md) | Pricing card |
| `mails.elixpo/output/` | Generated 1200×630 PNGs |
