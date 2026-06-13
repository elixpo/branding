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

The video Oreo must look **exactly like the Elixpo stickers** — cute
kawaii **2D pixel art**, thick dark outlines, big sparkly eyes, pink
cheeks, red E-badge, vibrant warm colours ([MASCOT.md](../../MASCOT.md)).
**Not** 3D, not voxel, not Minecraft, not realism.

These are **aesthetic, meaningful** little loops — a calm, cozy lo-fi
mood: Oreo resting in warm weather, a cool breeze moving the world around
him. Short (5s) and seamless so they can repeat.

The clips must **actually animate** (an early attempt just slow-zoomed a
still frame), so the style is **motion-first**: the breeze ruffles Oreo's
fur, grass and flowers sway, petals and sparkles drift, clouds crawl. The
camera is locked off — **no zoom, no pan**.

Write the `## Prompt` block to describe **the mood and what gently moves**
— the setting, the light, and which elements sway, drift, or float. The
generator appends the canonical sticker-matching mascot clause and the
2D pixel-art style suffix automatically.

## Generate

```bash
python tools/generate_videos.py             # every prompt here → videos/<stem>.mp4
python tools/generate_videos.py 01_breeze   # just one
python tools/generate_videos.py --duration 8 --aspect 16:9
```

Output MP4s land in [`videos/`](../../videos/). Model: `ltx-2`, default
5-second square clips.
