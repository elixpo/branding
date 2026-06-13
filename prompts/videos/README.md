# prompts/videos

Prompts for short Oreo mascot video clips. One `.md` per clip, named
`NN_slug.md` (e.g. `01_coral_field.md`), each with a `## Prompt` block:

```markdown
# Oreo in a coral flower field

## Prompt
A fixed side-angle shot of Oreo the panda lying completely still in a dense bed
of vibrant orange, pink, and purple coral-like flowers that gently sway and
ripple in a soft breeze
```

## The look

These clips are **not** the pixel-art sticker style. They're a
**vectorized aesthetic anime** look: clean vector shapes, soft gradients,
lush saturated colour.

The signature motion is a **fixed, static shot** — the panda holds
**completely still** while only the surrounding environment drifts (flowers
sway, water ripples, petals drift, clouds crawl) as if blown by a soft
invisible breeze. A calm ambient loop, not an action clip.

So write the `## Prompt` block to describe **the scene and what gently
moves around the still panda** — not what the panda does. The generator
appends the canonical mascot clause and the vectorized-anime style suffix
automatically; Oreo's colours live in [MASCOT.md](../../MASCOT.md).

## Generate

```bash
python tools/generate_videos.py                 # every prompt here → videos/<stem>.mp4
python tools/generate_videos.py 01_coral_field  # just one
python tools/generate_videos.py --duration 8 --aspect 16:9
```

Output MP4s land in [`videos/`](../../videos/). Model: `ltx-2`, default
4-second square clips.
