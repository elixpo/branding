# Cozy Doodle Photo Editing

Image-to-image editing pipeline on top of the [Pollinations API](../pollinations_asset_generate.md).
Drop raw photos in `raw/`, run the script, get doodle-aesthetic edits in `edited/`.

## Layout

```
editing/
├── edit.py           # the pipeline (stdlib only, no pip deps)
├── prompt.md         # the cozy-doodle edit instruction sent to the model
├── image_models.md   # full Pollinations image/video model registry (reference)
├── raw/              # INPUT photos — gitignored
└── edited/           # OUTPUT edits — gitignored
```

## How it works

For each image in `raw/`:

1. Upload it to `media.pollinations.ai` → content-addressed reference URL.
2. `GET gen.pollinations.ai/image/<prompt.md>?model=<model>&image=<url>` → edited image.
3. Save to `edited/<name>.<model>.<ext>` (model in the filename so you can A/B models).

## Models

Default is **`gptimage`** (GPT Image 1 Mini — fast & affordable). Paid-only models
are deliberately excluded. Free image-editing models (text+image input):

| model            | notes                       |
| ---------------- | --------------------------- |
| `gptimage`       | fast & affordable (default) |
| `gptimage-large` | higher-fidelity edits       |
| `kontext`        | FLUX.1 in-context editing   |
| `klein`          | FLUX.2 Klein 4B, fast       |
| `nova-canvas`    | editing & inpainting        |

## Auth

The script reads the key from `$POLLINATIONS_KEY` / `$POLLINATIONS_API_KEY`, else the
`POLLINATIONS_KEY` line in [`../.env.local`](../.env.local) (gitignored). Get a key at
[enter.pollinations.ai](https://enter.pollinations.ai).

## Usage

```bash
cd editing

python edit.py                          # edit all raw/ images with gptimage
python edit.py --model gptimage-large   # higher fidelity
python edit.py --only myphoto.jpg       # just one file (repeatable)
python edit.py --model kontext --force  # try another model, overwrite outputs
python edit.py --seed 7                 # reproducible seed
```

Outputs never collide across models, so to compare quality run the same photo
through several models and diff the `edited/<name>.<model>.jpg` results.

> **Note on `gptimage`:** it returns square (1024×1024). For non-square photos
> where framing matters, try `kontext` or `gptimage-large`, or pass
> `--width/--height`.
