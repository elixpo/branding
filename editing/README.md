# Cozy Doodle Photo Editing — the Elixpo scrapbook effect

The **go-to "scrapbook" effect** for the Elixpo brand — the warm torn-paper journal
look used by the [me.elixpo](https://me.elixpo) site. Context-aware image-to-image
editing on top of the [Pollinations API](../docs/pollinations-api.md), powered by the
**`klein`** model.

Drop raw photos in `editing/raw/`, run the script, get doodle-aesthetic edits in
`editing/edited/` that **keep the subject 100% intact** and add cozy scrapbook doodles
around it.

## Layout

```
editing/
├── edit.py           # the pipeline (Pillow only, no other deps)
├── prompt.md         # the cozy-doodle style prompt (sent to the model)
├── raw/              # INPUT photos   — gitignored
├── edited/           # OUTPUT edits   — gitignored
└── README.md
references/image_models.md   # Pollinations image/video model registry (reference)
```

## How it works

For each image in `editing/raw/`:

1. **Upload** it to `media.pollinations.ai` → reference URL.
2. **Analyze** it with a vision text model (`openai`) → scene theme, scene-specific
   doodle motifs, 2 short captions, and whether a **person/face** is present.
3. **Compose** a tight prompt: an action-forward "add doodles in the empty space" guard
   + the concrete draw/write asks + `prompt.md` style + (if a person is present) a
   hard **face/subject lock** at both ends.
4. **Edit** with an image model and **fit** the result back to the original's exact
   size (padding, never cropping, so no doodle is lost).

Output: `edited/<name>.<model>.jpg` — model is in the filename so you can A/B models.

## Models (free / non-paid only)

| model            | preserves subject | adds doodles | notes                              |
| ---------------- | ----------------- | ------------ | ---------------------------------- |
| **`klein`** ⭐    | yes (face/aspect) | yes          | FLUX.2 — **default**, best balance |
| `kontext`        | yes (strongest)   | minimal      | too conservative to add doodles    |
| `gptimage-large` | no (re-renders)   | rich         | great doodles but the face drifts  |
| `gptimage`       | no                | rich         | faster/cheaper version             |
| `nova-canvas`    | partial           | some         | editing & inpainting               |

**Why klein is the default:** `kontext` keeps the face perfectly but won't add the
scrapbook doodles; `gptimage*` adds rich doodles but repaints the whole frame so the
face/lighting/aspect drift. `klein` (FLUX.2) is the one free model that does both —
preserves the subject and framing while still drawing doodles.

> The look is **doodle/sticker-only — no text**. Diffusion models can't spell small
> handwriting reliably, so the pipeline draws flowers, books, stars, hearts and
> sparkles scattered around the subject like a sticker sheet, and explicitly forbids
> words/letters.

## Auth

The script reads the key from `$POLLINATIONS_KEY` / `$POLLINATIONS_API_KEY`, else the
`POLLINATIONS_KEY` line in [`../.env.local`](../.env.local) (gitignored). Get a key at
[enter.pollinations.ai](https://enter.pollinations.ai).

## Usage

```bash
python editing/edit.py                          # edit all raw/ images with klein
python editing/edit.py --only raw_6.jpeg        # one file (repeatable)
python editing/edit.py --model gptimage-large   # richer doodles, face drifts
python editing/edit.py --model kontext          # max subject preservation
python editing/edit.py --no-vision              # skip analysis, send prompt.md verbatim
python editing/edit.py --no-fit                 # don't snap back to original size
python editing/edit.py --seed 7 --force         # reproducible, overwrite outputs
```

To compare models on one photo, run it through several — outputs never collide
(`edited/<name>.<model>.jpg`).
