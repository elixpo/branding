# prompts/videos

Prompts for short Oreo mascot video clips — **one per service domain**,
mirroring the icon layout. Each service folder holds a single
`video_prompt.md` with a `## Prompt` block:

```
prompts/videos/<domain>/video_prompt.md   →   videos/<domain>.mp4
```

e.g. `prompts/videos/sketch.elixpo/video_prompt.md`:

```markdown
# Oreo sketching (for Elixpo Sketch)

## Prompt
Oreo sits in a sunlit golden meadow sketching on a small paper pad in his lap,
pencil moving in soft repeating strokes, glancing down then up, starting and
ending on the same pose for a seamless loop
```

## The look

Oreo himself stays **exactly like the Elixpo stickers** — cute kawaii
pixel art, thick dark outline, big sparkly eyes, pink cheeks, red E-badge
([ref/MASCOT.md](../../ref/MASCOT.md)). **Not** 3D, not voxel, not Minecraft.

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
python tools/generate_videos.py                  # every domain → videos/<domain>.mp4
python tools/generate_videos.py sketch.elixpo    # just one domain
python tools/generate_videos.py --duration 8 --aspect 9:16

# A/B different models on the same prompt+seed (output gets a __<model> suffix
# so they don't overwrite each other):
python tools/generate_videos.py sketch.elixpo --model veo
python tools/generate_videos.py sketch.elixpo --model seedance-pro
```

Output MP4s land in [`videos/`](../../videos/). Default model `nova-reel`
(holds the HD-2D depth + kawaii-pixel look without garbled captions;
renders landscape ~6s). For A/B try `veo`, `seedance-pro` (paid), or the
1080p variants (`wan-pro-1080p`, `p-video-1080p`).

**Prompt budget:** nova-reel caps the prompt at 512 chars, so the
generator auto-switches to a compact clause/style; keep each
`video_prompt.md` scene under ~200 chars so the loop instruction at the
end survives intact (the tool warns if it has to trim).

## Custom direction (`## Style`)

By default every clip gets the ambient-loop style — depth, gentle motion,
**static locked-off camera**. A clip that needs different direction (a
moving camera, a walking shot) can add an optional `## Style` block that
**replaces** the default style suffix just for that clip:

```markdown
## Prompt
Oreo walks along a path through a lush rice paddy at golden hour…

## Style
cinematic HD-2D kawaii pixel-art, … smooth cinematic side-tracking camera
panning to follow Oreo as he walks, flat 2D pixel art
```

The mascot identity clause is still appended, so Oreo stays on-brand —
only the style/camera direction changes. Keep `## Style` concise too; it
counts against the same nova-reel 512-char budget.

## Seamless loops

These clips repeat, so describe a **cyclical action that starts and ends
in the same pose** — e.g. "pencil moving in soft repeating strokes,
beginning and ending on the exact same pose so it loops". The style
suffix already asks for a seamless loop and a static camera; the scene
just needs to avoid a one-way action that wouldn't repeat cleanly.
