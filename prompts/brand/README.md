# prompts/brand — Elixpo logo & wordmark

The **brand-mark prompts**: the Elixpo logo, the wordmark, and their
lockup. These are the top-of-funnel identity assets — what goes on the
site header, the GitHub org avatar, the app splash, the favicon.

Everything here obeys [`ref/MASCOT.md`](../../ref/MASCOT.md) — same panda
(**Oreo**), same palette, same thick-outline pixel-art look. The one
deliberate exception: the brand marks **may contain the word "Elixpo"**,
because a wordmark is text by definition. (Stickers/icons stay text-free;
brand marks don't.)

## Variants

| File | Variant | Has text | Has mascot | Use |
|---|---|---|---|---|
| [`mascot-mark.md`](mascot-mark.md) | Mascot mark | no | yes | avatar, favicon, app icon, loading mark |
| [`wordmark.md`](wordmark.md) | Wordmark | **yes** | no | inline text logo, footer, letterhead |
| [`lockup.md`](lockup.md) | Mark + wordmark lockup | **yes** | yes | primary horizontal logo — site header, README hero |

```
prompts/brand/<variant>.md   →   assets/brand/<variant>.png
```

## Generate

```bash
python tools/generate_assets.py --brand                 # all three variants
python tools/generate_assets.py --brand lockup          # one variant
python tools/generate_assets.py --brand --seed 7        # different seed
```

Each variant renders on a wide **16:9** (1024×576) warm-cream canvas —
the lockup and wordmark are horizontal — and is run through the
transparency pass, so the marks land transparent-ready for the web. The
mascot mark sits centered with even margins (crop to its bounding box for
a square favicon/avatar). Output goes to
[`assets/brand/`](../../assets/brand/).

## A note on text fidelity

The free default model (`gptimage`) renders the short "Elixpo" wordmark
acceptably but isn't typography-perfect. For a crisp, production wordmark,
regenerate the text variants with a typography-strong model (e.g.
`seedream-pro` or `ideogram-v4-quality`, both paid — see
[`ref/image_models.md`](../../ref/image_models.md)), or set the wordmark
in a vector tool using the brand palette and treat these prompts as the
visual reference.

## Brand palette (from `ref/MASCOT.md`)

| Token | Hex | Role |
|---|---|---|
| `BG` | `#FFF8EB` | warm-ivory background |
| `PRIMARY` | `#FF5D68` | pink/red — cheeks, accents |
| `E-badge` | `#DC3C32` | red-gold chest badge |
| `GOLD` | `#FFBE1E` | celebration gold |
| `TEAL` | `#00B4A5` | cool accent |
| `TEXT_BRIGHT` | `#262630` | dark outline / text |
