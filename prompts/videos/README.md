# prompts/videos

Prompts for short Oreo mascot video clips. One `.md` per clip, named
`NN_slug.md` (e.g. `01_breeze.md`), each with a `## Prompt` block:

```markdown
# Oreo in a warm afternoon breeze

## Prompt
Oreo sits peacefully on a small grassy hill in warm golden light, eyes gently
blinking, enjoying a cool breeze; tall grass and wildflowers sway around him and
soft leaves drift past while slow clouds cross the warm sky behind him
```

## The look

Oreo himself stays **exactly like the Elixpo stickers** — cute kawaii
pixel art, thick dark outline, big sparkly eyes, pink cheeks, red E-badge
([MASCOT.md](../../MASCOT.md)). **Not** 3D, not voxel, not Minecraft.

But the **world has depth**. The trap to avoid is flat paper-cutout
parallax — that reads like a PowerPoint slide, no atmosphere. Instead aim
for an **HD-2D diorama** (Octopath Traveler / Sea of Stars / Eastward
vibe): the pixel character sits inside a layered scene with real depth —
**tilt-shift depth of field, a soft bokeh background, a detailed
foreground, warm volumetric light and god rays, and dust/petals drifting
at different depths**.

These are **aesthetic, meaningful** little loops — calm, cozy, alive:
Oreo resting in warm weather, a cool breeze moving the world around him.
Short (5s) and seamless so they repeat. Motion-first (an early attempt
just slow-zoomed a still), camera locked off — **no zoom, no pan**.

Write the `## Prompt` block to describe **the mood, the depth, and what
moves** — the setting and light, what sits blurred in the fore/background,
and which elements sway or drift. The generator appends the canonical
sticker-matching mascot clause and the HD-2D style suffix automatically.

## Generate

```bash
python tools/generate_videos.py             # every prompt here → videos/<stem>.mp4
python tools/generate_videos.py 01_breeze   # just one
python tools/generate_videos.py --duration 8 --aspect 16:9

# A/B different models on the same prompt+seed (output gets a __<model> suffix
# so they don't overwrite each other):
python tools/generate_videos.py 01_breeze --model veo
python tools/generate_videos.py 01_breeze --model seedance-pro
```

Output MP4s land in [`videos/`](../../videos/). Default model `ltx-2`,
5-second square clips. For richer depth/quality try `veo`, `seedance-pro`,
or the 1080p variants (`wan-pro-1080p`, `p-video-1080p`).
