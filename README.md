# elixpo/brand

The originating home of the **Elixpo** brand - the brand source of truth, the
asset-generation pipeline, the prompt sources, and the generated sticker, icon
and mascot sets. Everything orbits around **Oreo**, the pixel-art panda mascot.

> Want to use these assets? Browse [`assets/brand/`](assets/brand/),
> [`stickers/`](stickers/) and [`prompts/icons/`](prompts/icons/). Want a new
> one made? **Open an issue.** A maintainer reviews, applies the `approved`
> label, and a bot generates the image straight into the repo.

A browsable, downloadable brand kit also lives at
**[elixpo.com/assets](https://elixpo.com/assets)**.

---

## Repository layout

```
ref/        Brand source-of-truth - MASCOT.md (identity, palette, rules)
            and image_models.md (Pollinations model registry).
docs/       Guides - pollinations-api.md (the generation API reference).
prompts/    Prompt sources, by class:
              brand/      logo · wordmark · lockup
              stickers/   the printable sticker set
              icons/      per-domain web/app service icons
              og-image/   per-domain Open Graph / social images
              videos/     per-domain mascot clips
assets/     Generated brand marks (brand/), web icons (icons/web/) and PWA
            bundles (pwa/).
stickers/   Generated 1024² sticker PNGs (transparent, optimised).
videos/     Generated mascot MP4s.
editing/    The Elixpo "scrapbook" photo effect (klein) - see below.
tools/      The generation pipeline (Python + Pillow).
scripts/    Optimisation / transparency helpers.
```

> **Where assets go:** stickers, marks, and mascot clips live here. Per-product
> **Open Graph / social images** are generated here (`prompts/og-image`,
> `tools/og_compose.py`) and **distributed to the individual product repos** -
> the originating prompts and code stay in this repository.

---

## Requesting an asset (community workflow)

1. **Open an issue** using the **"Sticker / Icon Request"** template. Describe
   the vibe in one or two lines. Optionally attach a doodle for reference.
2. A maintainer reviews the prompt against [ref/MASCOT.md](ref/MASCOT.md). If it
   fits the brand, they apply the **`approved`** label.
3. The label fires a GitHub Action that reads the prompt, appends the canonical
   Mascot Clause and Style Suffix, calls Pollinations.ai to render a 1024×1024
   image, runs the transparency pass for stickers, commits the result to
   [`requested/`](requested/), and comments on the issue with a link.
4. If the result misses the mark, add the **`regenerate`** label to retry with a
   different seed.

The maintainer review step is intentional - it stops drift, slop, and abuse of
the generator.

---

## Local generation

```bash
# Brand marks - logo, wordmark, lockup -> assets/brand/:
python tools/generate_assets.py --brand
python tools/generate_assets.py --brand lockup        # one variant

# Generate every sticker that has a prompt:
python tools/generate_assets.py --stickers
python tools/generate_assets.py --stickers 01_hello   # one sticker

# Strip the cream background to transparent + save optimised PNG:
python tools/sticker_transparency.py 01_hello
python tools/sticker_transparency.py --optimize-only  # re-compress only

# Compile all stickers into a printable A4 sheet:
python tools/compile_sticker_sheet.py

# Per-product Open Graph images (then distribute to the product repos):
python tools/og_compose.py
```

Generated stickers and marks are saved as **optimised** PNGs - lossless
`optimize + compress_level=9`, so the art is pixel-identical but smaller on disk.
The Pollinations endpoint backs every generator.

---

## Scrapbook photo effect (`editing/`)

The Elixpo **scrapbook** look - a warm torn-paper journal effect, the go-to
treatment used by the [me.elixpo](https://me.elixpo.com) site. Drop photos in
`editing/raw/`, run the pipeline (default model **`klein`**), and get
doodle-decorated edits in `editing/edited/` with the subject kept 100% intact.
See [`editing/README.md`](editing/README.md).

```bash
python editing/edit.py                  # edit every editing/raw/ photo
```

---

## Icon sync

Icon prompts (`prompts/icons/`) are **mirrored** from the OreoOS firmware
repository (`elixpo/oreo`), where the icons live alongside the apps that use
them. The upstream repo is the source of truth for icon prompts. A scheduled
GitHub Action pushes any changes under `prompts/icons/` here every night.
**Do not edit `prompts/icons/` here directly** - open a PR upstream instead.

---

## Standards

This repository follows the **Elixpo standard**, shared by every Elixpo repo:

- [`LICENSE`](LICENSE) - the Elixpo License (MIT for code, CC-BY-4.0 for assets).
- [`LICENSES/`](LICENSES/) - canonical texts + the
  [Oreo-trademarks exception](LICENSES/exceptions/Oreo-trademarks).
- [`LICENSES/NOTICE`](LICENSES/NOTICE) - the notice board (per-repo reservations).
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Branding & legal

- The **Oreo mascot character**, the **chest E-badge**, and the **brand palette**
  in [ref/MASCOT.md](ref/MASCOT.md) are © 2026 Ayushman Bhattacharya and form part
  of the copyright registration (Indian Copyright Office Diary `LD-26455/2026-CO`).
- The licence covers the **assets as files** (CC-BY-4.0); it does **not** transfer
  rights to the **Oreo character / Elixpo brand** for use outside Elixpo-aligned
  projects. See [`LICENSES/exceptions/Oreo-trademarks`](LICENSES/exceptions/Oreo-trademarks).
- "Oreo" is an internal codename; the public brand is **Elixpo Badge** - see
  [`ref/MASCOT.md`](ref/MASCOT.md) §Versioning.

<p align="center">
  <sub>Made in the open, together. © 2023-2026 Elixpo.</sub>
</p>
