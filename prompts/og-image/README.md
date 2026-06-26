# prompts/og-image — Elixpo Mails OG / social cards

Open-graph (social share) cards for **Elixpo Mails** and the wider suite, in
**editorial tech minimalism**: a faint **dotted matrix** background, a
**continuous one-line** Oreo, 2–3 understated geometric shapes, and a bold
serif headline. High-end design-system wireframe, not glowing 3D tech.

> **LOCKED spec:** [`ref/OREO-LINEART.md`](../../ref/OREO-LINEART.md) is the
> single source of truth for the line-art Oreo + this card system. Everything
> here derives from it; the seed is pinned (`OG_SEED`) so the look reproduces.

## Pipeline — AI draws the design, we set the type

The model **only generates the text-free design** (so it never fumbles
letters); we composite the headline/eyebrow/sub/url ourselves with Pillow at
exact proportions:

```
1. AI design  (gptlarge, 16:9, NO text)  →  <site>/output/<name>.bg.png
2. Pillow text (## Text block)           →  <site>/output/<name>.png   (final, 1280×720)
```

`tools/generate_assets.py --og` runs step 1 then auto-runs step 2.
`tools/og_compose.py` re-runs step 2 alone (retext without regenerating).

## Structure — one folder per site

```
prompts/og-image/
├── palette.json              ← shared palette + type tokens (root)
├── README.md
└── mails.elixpo/              ← the first site
    ├── STYLE.md               ← shared design + text spec
    ├── prompts/               ← the card prompts
    │   └── default.md  features.md  workspace.md  docs.md  pricing.md
    └── output/
        ├── <name>.bg.png      ← AI design (text-free)
        └── <name>.png         ← final composited card (1280×720, 16:9)
```

Each card `.md` holds **two blocks**: `## Prompt` (the text-free design, fed to
the model) and `## Text` (`eyebrow` / `headline` / `sub` / `url`, drawn by
Pillow). Copy a site's `output/default.png` → that app's `public/og-image.png`.

To **add a site**, copy `mails.elixpo/` to `prompts/og-image/<newsite>/`,
edit each card's `## Text` (and any URLs), and run `--og <newsite>`.

## Palette — the "oreo" (Cohere/coral) system

Exact tokens from `mail.elixpo/app/globals.css`, light theme only. See
[`palette.json`](palette.json).

| Token | Hex | Role |
|---|---|---|
| Canvas | `#ffffff` | Background |
| Ink | `#212121` | Headline serif (Pillow) + the one-line panda |
| Slate | `#75758a` | Sub copy (Pillow) |
| Muted slate | `#93939f` | Eyebrow / url (Pillow) |
| Hairline | `#d9d9dd` | Dotted matrix + geometric shapes |
| **Coral (accent)** | `#ff7759` | Underline (Pillow) + the panda's ears & one leg |
| Badge red | `#dc3c32` | The panda's stylish "E" chest badge |

## Type (composited by `og_compose.py`, not the AI)

- **Headline** — bold high-contrast **serif** (Fraunces / Playfair), auto-fit
  + wrapped, ink. Drop `Fraunces-Bold.ttf` into `tools/fonts/` to upgrade
  from the DejaVu fallback.
- **Eyebrow / url** — **Space Mono**, uppercase, tracked, muted slate.
- **Sub** — Inter, slate.

## Art direction (the design rules)

1. **Editorial tech minimalism** — structured, airy, flat 2D. NO 3D, gradients,
   glow or neon. **16:9, no cropping.**
2. **Faint dotted matrix** — an even field of tiny `#d9d9dd` dots over white,
   subtle and receding.
3. **Continuous one-line Oreo** — ONE unbroken **very thin** `#212121` line with a
   few gentle loops (lightly tangled, NOT a dense scribble) forming a **cute,
   happy** kawaii panda (plump & healthy, smiling, head turned slightly left
   toward the text), kept **fairly large** in the **right ~40–42%**, clear of
   the text. Coral `#ff7759` fills **both
   ears and one leg**; a small, **compact** round **red `#DC3C32` "E" chest badge** (centred, stylish) is Oreo's signature — the only saturated colours, both on the mascot
   (see `ref/MASCOT.md`).
4. **2–3 geometric shapes** — thin `#d9d9dd` hairline outlines (circle / triangle
   / square / arc), framing the mascot, never filled. Coral stays on the panda.
5. **NO TEXT in the AI image** — the left ~55% is kept empty; the type is added
   by Pillow afterward.
6. **Saturated colour only on the panda** — coral `#ff7759` ears + one leg, and
   a red `#DC3C32` "E" chest badge. Everything else is ink line + hairline.

## Generate

```bash
python tools/generate_assets.py --og                       # every site, every card
python tools/generate_assets.py --og mails.elixpo          # one site
python tools/generate_assets.py --og mails.elixpo default  # one card
python tools/generate_assets.py --og --seed 11             # explore (seed is pinned otherwise)

python tools/og_compose.py mails.elixpo                    # re-draw text only
```

## Files (per site, e.g. `mails.elixpo/`)

| File | What |
|---|---|
| [`mails.elixpo/STYLE.md`](mails.elixpo/STYLE.md) | Shared design + text spec |
| [`mails.elixpo/prompts/default.md`](mails.elixpo/prompts/default.md) | Default / home card (→ `public/og-image.png`) |
| [`mails.elixpo/prompts/features.md`](mails.elixpo/prompts/features.md) | Capabilities card |
| [`mails.elixpo/prompts/workspace.md`](mails.elixpo/prompts/workspace.md) | Workspaces card |
| [`mails.elixpo/prompts/docs.md`](mails.elixpo/prompts/docs.md) | Documentation card |
| [`mails.elixpo/prompts/pricing.md`](mails.elixpo/prompts/pricing.md) | Pricing card |
| `mails.elixpo/output/` | `<name>.bg.png` (AI design) + `<name>.png` (final 16:9) |
