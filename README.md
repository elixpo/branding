# elixpo/assets

Shared visual assets for the **Elixpo project series** — the brand logo,
stickers, icons, banners, splash art and short mascot clips. Everything
orbits around **Oreo**, the pixel-art panda mascot.

> Want to use these assets? Browse [`assets/brand/`](assets/brand/),
> [`stickers/`](stickers/) and [`prompts/icons/`](prompts/icons/). Want a
> new one made? **Open an issue.** A maintainer reviews, applies the
> `approved` label, and a bot generates the image straight into the repo.

---

## Repository layout

```
ref/        Brand source-of-truth — MASCOT.md (identity, palette, rules)
            and image_models.md (Pollinations model registry).
docs/       Guides — pollinations-api.md (the generation API reference).
prompts/    Prompt sources, by class:
              brand/      logo · wordmark · lockup
              stickers/   the printable sticker set
              icons/      per-domain web/app service icons
              videos/     per-domain mascot clips
assets/     Generated brand marks (brand/), web icons (icons/web/), PWA
            bundles (pwa/) and licences.
stickers/   Generated 1024² sticker PNGs (transparent, optimised).
videos/     Generated mascot MP4s.
editing/    The Elixpo "scrapbook" photo effect (klein) — see below.
tools/      The generation pipeline (Python + Pillow).
```

---

## Requesting an asset (community workflow)

1. **Open an issue** using the **"Sticker / Icon Request"** template.
   Describe the vibe in one or two lines. Optionally attach a doodle
   for reference.
2. A maintainer reviews the prompt against [ref/MASCOT.md](ref/MASCOT.md). If
   it fits the brand, they apply the **`approved`** label.
3. The label fires a GitHub Action that:
   - Reads the prompt from the issue body,
   - Appends the canonical Mascot Clause and Style Suffix,
   - Calls Pollinations.ai to render a 1024×1024 image,
   - Runs the transparency pass for stickers,
   - Commits the result to [`requested/<issue-number>-<slug>.png`](requested/),
   - Posts a comment on the issue with a link to the file + a permalink.
4. If the result misses the mark, add the **`regenerate`** label to
   retry with a different seed. Repeat as needed.

The maintainer review step is intentional — it stops drift, slop, and
abuse of the generator.

---

## Local generation

```bash
# Brand marks — logo, wordmark, lockup → assets/brand/:
python tools/generate_assets.py --brand
python tools/generate_assets.py --brand lockup        # one variant

# Generate every sticker that has a prompt:
python tools/generate_assets.py --stickers

# Generate one sticker:
python tools/generate_assets.py --stickers 01_hello

# Strip the cream background to transparent + save optimised PNG
# (both auto-run by the generators above):
python tools/sticker_transparency.py 01_hello

# Losslessly re-compress the committed stickers (no re-render, same pixels):
python tools/sticker_transparency.py --optimize-only

# Compile all stickers into a printable A4 sheet:
python tools/compile_sticker_sheet.py
```

Generated stickers and marks are saved as **optimised** PNGs — lossless
`optimize + compress_level=9`, so the art is pixel-identical but markedly
smaller on disk. The Pollinations endpoint backs every generator.

---

## Scrapbook photo effect (`editing/`)

The Elixpo **scrapbook** look — a warm torn-paper journal effect, the
go-to treatment used by the [me.elixpo](https://me.elixpo) site. Drop
photos in `editing/raw/`, run the pipeline (default model **`klein`**),
and get doodle-decorated edits in `editing/edited/` with the subject kept
100% intact. See [`editing/README.md`](editing/README.md).

```bash
python editing/edit.py                  # edit every editing/raw/ photo
```

---

## Icon sync

Icon prompts (`prompts/icons/`) are **mirrored** from the OreoOS
firmware repository (`elixpo/oreo`), where the icons live
alongside the apps that use them. The upstream repo is the source of
truth for icon prompts.

A scheduled GitHub Action on the upstream repo pushes any changes under
`prompts/icons/` to this repo every night. **Do not edit
`prompts/icons/` here directly** — your edits will be overwritten.
Open a PR upstream instead.

---

## Branding & legal

- The **Oreo mascot character**, the **chest E-badge**, and the **brand
  palette** in [ref/MASCOT.md](ref/MASCOT.md) are © 2026 Ayushman Bhattacharya
  and form part of the OreoOS copyright registration (Indian Copyright
  Office Diary `LD-26455/2026-CO`).
- Assets in this repository are licensed for community use under the
  repository's open licence (see [LICENSE](LICENSE)). The licence
  covers the **assets**; it does **not** transfer rights to the **Oreo
  character** for use outside Elixpo-aligned projects.
- The name "Oreo" is used here as an internal codename. The public
  brand for this project is **Elixpo Badge** — see
  [`ref/MASCOT.md`](ref/MASCOT.md) §Versioning.
