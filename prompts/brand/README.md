# prompts/brand — Elixpo logo & wordmark

The **brand-mark prompts**: the Elixpo mascot mark, the wordmark, and their
lockup. These are the top-of-funnel identity assets — what goes on the site
header, the GitHub org avatar, the app splash, the README hero.

The brand marks use the **line-art** register — a continuous one-line Oreo, fine
single-weight ink strokes, coral ears + one leg and the red "E" badge, on a clean
white dotted canvas. The locked spec is
[`references/OREO-LINEART.md`](../../references/OREO-LINEART.md) (the calm,
editorial counterpart to the pixel-art mascot in
[`references/MASCOT.md`](../../references/MASCOT.md)).

## They are generated EXACTLY like the OG cards

Same two-step pipeline as `prompts/og/`:

1. The AI renders the **text-free line-art DESIGN** (`## Prompt`) — the panda
   and/or the dotted-matrix wireframe, with NO typography.
2. **Pillow composites the type** (`## Text`) — the "Elixpo" headline in a fancy
   serif with a coral underline, and the "Built in the Open" tagline beneath.

There is **no alpha-removal / transparency pass** — the white-canvas card *is*
the asset, exactly like an OG share card. A prompt with **no `## Text` block**
(the mascot mark) keeps the AI design as the final, untouched.

```bash
python pipeline/generate_assets.py --brand            # mascot mark, wordmark, lockup
python pipeline/generate_assets.py --brand lockup     # one variant
python pipeline/generate_assets.py --brand --force    # reroll a locked mark
python pipeline/generate_assets.py --brand --seed 11  # explore a different seed
```

Each `<variant>.md` here is one prompt; the generator renders it (seed defaults
to `OG_SEED`, the proven line-art seed), composites any `## Text`, and writes the
result to [`branding/brand/<variant>.png`](../../branding/brand/).

## Locking a good generation

AI generation isn't reproducible run-to-run, so once a mark looks right and is
committed under `branding/brand/`, it is **LOCKED** — `--brand` keeps it and
prints `[locked] ...` instead of regenerating. To intentionally reroll, pass
`--force` (or delete the `.png`). This mirrors how the OG cards are frozen, so
the official identity never drifts by accident.

## Variants

| File | Variant | `## Text` | Mascot in design | Use |
|---|---|---|---|---|
| [`mascot-mark.md`](mascot-mark.md) | Mascot mark | — (design is final) | yes | avatar, app icon, loading mark |
| [`wordmark.md`](wordmark.md) | Wordmark + tagline | Elixpo + tagline | no | inline text logo, footer, letterhead |
| [`lockup.md`](lockup.md) | Mark + wordmark + tagline | Elixpo + tagline | yes | primary horizontal logo — site header, README hero |

The wordmark and lockup carry the headline **"Elixpo"** with a coral underline
and the small tagline **"Built in the Open"** beneath — both drawn by Pillow in
`pipeline/og_compose.py` (serif headline, coral underline, mono/sans sub), so the
type is crisp and correctly spelled every time (the AI never renders the letters).

```
prompts/brand/<variant>.md   →   branding/brand/<variant>.png
```

## Brand palette (line-art register)

| Token | Hex | Role |
|---|---|---|
| Ink | `#212121` | the single continuous line |
| Coral | `#ff7759` | ears + one leg, headline underline |
| E-badge | `#dc3c32` | round chest badge, the "E" |
| Dots / geometry | `#d9d9dd` | dotted matrix + hairline wireframe |
| Canvas | `#ffffff` | white background |
