# prompts/og-image — Elixpo Mails OG / social cards

Open-graph (social share) cards for **Elixpo Mails** and the wider suite, in
**editorial tech minimalism**: a faint **dotted matrix** background, an
**entangled one-line** Oreo, 2–3 understated geometric shapes, and a bold
serif headline. High-end design-system wireframe, not glowing 3D tech.

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
└── mails.elixpo/              ← the first site
    ├── STYLE.md               ← shared design + text spec
    ├── palette.json           ← palette + type tokens
    ├── default.md  features.md  workspace.md  docs.md  pricing.md
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
[`mails.elixpo/palette.json`](mails.elixpo/palette.json).

| Token | Hex | Role |
|---|---|---|
| Canvas | `#ffffff` | Background |
| Ink | `#212121` | Headline serif (Pillow) + the one-line panda |
| Slate | `#75758a` | Sub copy (Pillow) |
| Muted slate | `#93939f` | Eyebrow / url (Pillow) |
| Hairline | `#d9d9dd` | Dotted matrix + geometric shapes |
| **Coral (accent)** | `#ff7759` | Underline + the panda's ears / one leg / "E" badge |

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
3. **Entangled one-line Oreo** — ONE unbroken thin `#212121` line that loops,
   overlaps and **entangles** into a clearly recognisable panda (deliberate,
   balanced tangles — not a scribble). Coral `#ff7759` fills **both ears and one
   leg** and forms a small round **"E" chest badge** — the only colour on the
   mascot (Oreo's accents; see `ref/MASCOT.md`).
4. **2–3 geometric shapes** — thin `#d9d9dd` hairline outlines (circle / triangle
   / square / arc), framing the mascot, never filled. Coral stays on the panda.
5. **NO TEXT in the AI image** — the left ~55% is kept empty; the type is added
   by Pillow afterward.
6. **Coral is the only saturated colour** — it appears only on the panda (ears,
   one leg, the "E" badge).

## Generate

```bash
python tools/generate_assets.py --og                       # every site, every card
python tools/generate_assets.py --og mails.elixpo          # one site
python tools/generate_assets.py --og mails.elixpo default  # one card
python tools/generate_assets.py --og --seed 7              # different seed (better panda)

python tools/og_compose.py mails.elixpo                    # re-draw text only
```

## Files (per site, e.g. `mails.elixpo/`)

| File | What |
|---|---|
| [`mails.elixpo/STYLE.md`](mails.elixpo/STYLE.md) | Shared design + text spec |
| [`mails.elixpo/palette.json`](mails.elixpo/palette.json) | Palette + type tokens |
| [`mails.elixpo/default.md`](mails.elixpo/default.md) | Default / home card (→ `public/og-image.png`) |
| [`mails.elixpo/features.md`](mails.elixpo/features.md) | Capabilities card |
| [`mails.elixpo/workspace.md`](mails.elixpo/workspace.md) | Workspaces card |
| [`mails.elixpo/docs.md`](mails.elixpo/docs.md) | Documentation card |
| [`mails.elixpo/pricing.md`](mails.elixpo/pricing.md) | Pricing card |
| `mails.elixpo/output/` | `<name>.bg.png` (AI design) + `<name>.png` (final 16:9) |
