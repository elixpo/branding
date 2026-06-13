"""Generate short Oreo mascot video clips via the Pollinations AI video API.

Reads prompts/videos/<name>.md (the block after '## Prompt') and writes
videos/<name>.mp4. Mirrors tools/generate_assets.py: same POLLINATIONS_KEY
from .env, same '## Prompt' convention, same retry/backoff. The difference
is the endpoint (/video instead of /image), an MP4 payload, and the
duration/aspect-ratio knobs that only videos have.

Usage:
  python tools/generate_videos.py                 # all prompts in prompts/videos/
  python tools/generate_videos.py 01_wave         # single clip by stem
  python tools/generate_videos.py --seed 7        # different seed
  python tools/generate_videos.py --duration 8    # longer clips (default 4s)
  python tools/generate_videos.py --aspect 16:9   # widescreen (default 1:1)

Mascot reference: MASCOT.md
"""

import os
import sys
import urllib.request
import urllib.parse
import time
from pathlib import Path
from dotenv import load_dotenv

# Key lives in .env.local (gitignored). Load it first, then fall back to
# .env — load_dotenv() won't override a var that .env.local already set.
load_dotenv(".env.local")
load_dotenv()

KEY      = os.getenv("POLLINATIONS_KEY")
BASE     = "https://gen.pollinations.ai/video"
MODEL    = "ltx-2"
DURATION = 5         # seconds — short, cozy, looping
ASPECT   = "1:1"     # square, matches the rest of the mascot assets

# ── Style snippets (kept in sync with MASCOT.md by hand) ─────────────────────
# Appended to every prompt so clips stay on-brand even when the .md only
# describes the scene. The video Oreo must look EXACTLY like the Elixpo
# stickers — cute kawaii 2D pixel art, NOT 3D / voxel / Minecraft.

# Canonical Oreo identity — matches the sticker art (cream body, dark rounded
# patches, big sparkly eyes, pink cheeks, thick outline, red E-badge).
MASCOT_CLAUSE = (
    "the main subject is Oreo: a cute kawaii pixel-art panda exactly like the "
    "Elixpo stickers — warm cream-white body rgb(240,238,232), dark rounded "
    "ear and eye patches rgb(38,38,48), big sparkly black eyes with white "
    "catchlights, rosy pink cheeks rgb(255,93,104), thick dark outline, and a "
    "red E-badge rgb(220,60,50) on the chest"
)

# 2D pixel-art look matching the stickers + aesthetic ambient MOTION. The trap:
# a flat "static" prompt makes the model Ken-Burns-zoom a still frame. So name
# the things that gently move (breeze, grass, petals, fur) for a cozy lo-fi
# loop, and explicitly forbid both the zoom AND any 3D/voxel drift.
VIDEO_STYLE = (
    "2D animated pixel-art illustration in the Elixpo sticker style, thick "
    "dark outlines, vibrant warm celebration colours, cozy lo-fi aesthetic, "
    "soft golden warm sunlight; Oreo sits calmly and content in a gentle cool "
    "breeze that ruffles his fur and ears while grass, flowers and petals sway "
    "and drift, soft leaves and little sparkles float past, slow drifting "
    "clouds; smooth hand-animated seamless loop with subtle parallax, gentle "
    "continuous motion NOT a static image, no camera zoom, no pan, locked-off "
    "framing, no 3D, no voxel, no realism, no text, no watermark"
)


def _read_prompt(path):
    """Read prompt text from a .md file (the block after '## Prompt')."""
    md = Path(path)
    if not md.exists():
        return None
    text = md.read_text()
    marker = "## Prompt"
    if marker in text:
        after = text.split(marker, 1)[1]
        lines = []
        for line in after.splitlines():
            if line.startswith("##"):
                break
            lines.append(line)
        return " ".join(l.strip() for l in lines if l.strip())
    return None


def _build_prompt(raw):
    """Append the mascot clause and video style suffix to a raw prompt."""
    return ", ".join(p for p in (raw, MASCOT_CLAUSE, VIDEO_STYLE) if p)


def download_to(prompt, out_path, seed=42, duration=DURATION, aspect=ASPECT,
                model=MODEL):
    """Render one clip and save the MP4 to out_path. Returns True on success."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print("→ %s  (%ss, %s, %s)\n  %s..." %
          (out_path, duration, aspect, model, prompt[:90]))

    if not KEY:
        print("  ERROR: POLLINATIONS_KEY not set in .env.local — cannot authenticate")
        return False

    # NOTE: User-Agent is REQUIRED — the API returns 403 without it.
    headers = {
        "Authorization": "Bearer %s" % KEY,
        "User-Agent":    "OreoBadge/1.0",
    }
    enc = urllib.parse.quote(prompt)
    qs  = urllib.parse.urlencode({
        "model":       model,
        "duration":    duration,
        "aspectRatio": aspect,
        "seed":        seed,
        "nologo":      "true",
    })
    url = "%s/%s?%s" % (BASE, enc, qs)

    for attempt in range(4):
        try:
            req  = urllib.request.Request(url, headers=headers)
            # Video renders are slow — give the server plenty of headroom.
            resp = urllib.request.urlopen(req, timeout=300)
            data = resp.read()
            # A real MP4 is tens of KB minimum; anything tiny is an error
            # page or a truncated response, so retry rather than save it.
            if len(data) < 10000:
                print("  WARN small (%d bytes), retry" % len(data))
                time.sleep(15 * (attempt + 1))
                continue
            out_path.write_bytes(data)
            print("  saved %d bytes  [model=%s]" % (len(data), model))
            return True
        except urllib.error.HTTPError as e:
            # Read the response body so we can show *why* the server refused.
            try:
                body = e.read().decode("utf-8", "replace").strip()
            except Exception:
                body = ""
            short = (body[:600] + "…") if len(body) > 600 else body

            # 4xx won't fix themselves — bail fast with the full message.
            if e.code in (400, 401, 403, 404, 422):
                print("  FATAL HTTP %d %s   [model=%s]" % (e.code, e.reason, model))
                if body:
                    print("  ── server response ──")
                    for line in short.splitlines():
                        print("    " + line)
                    print("  ──────────────────────")
                else:
                    print("  (empty response body)")
                return False

            wait = 20 * (attempt + 1)
            print("  attempt %d HTTP %d %s — retry in %ds" %
                  (attempt + 1, e.code, e.reason, wait))
            if body:
                print("    server: " + short.splitlines()[0][:200])
            time.sleep(wait)
        except Exception as e:
            wait = 20 * (attempt + 1)
            print("  attempt %d error: %s — retry in %ds" % (attempt + 1, e, wait))
            time.sleep(wait)
    return False


def generate_videos(only_names=None, seed=42, duration=DURATION, aspect=ASPECT,
                    model=MODEL):
    """Generate clips from prompts/videos/*.md → videos/<stem>.mp4.

    When `model` is not the default, the model name is appended to the
    filename (videos/<stem>__<model>.mp4) so several models can be A/B'd
    against the same prompt without clobbering each other's output.
    """
    prompts_dir = Path("prompts") / "videos"
    out_dir     = Path("videos")

    if not prompts_dir.exists():
        print("No prompts directory at %s" % prompts_dir)
        print("Add prompts/videos/<name>.md with a '## Prompt' block first.")
        return

    mds = sorted(prompts_dir.glob("*.md"))
    # Drop README.md — only named clip prompts should be generated.
    mds = [m for m in mds if m.stem.lower() != "readme"]
    if only_names:
        mds = [m for m in mds if m.stem in only_names]
    if not mds:
        print("No video .md prompt files in %s (after filtering)" % prompts_dir)
        return

    print("Generating %d clip(s)  [%ss, %s, seed=%d, model=%s]...\n" %
          (len(mds), duration, aspect, seed, model))
    # Tag the filename with the model only when it's not the default, so the
    # canonical output stays videos/<stem>.mp4 while A/B runs sit beside it.
    tag = "" if model == MODEL else "__%s" % model.replace("/", "-")
    for md in mds:
        raw = _read_prompt(md)
        if not raw:
            print("  SKIP %s — no ## Prompt block" % md.name)
            continue
        out = out_dir / ("%s%s.mp4" % (md.stem, tag))
        download_to(_build_prompt(raw), out, seed=seed,
                    duration=duration, aspect=aspect, model=model)
        # Videos are expensive and slow — pace the requests generously.
        time.sleep(10)
    print("\nDone. Clips in %s/" % out_dir)


def _pop_int(args, flag, default):
    """Strip a `--flag N` pair from args. Returns (remaining_args, value)."""
    value = default
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            try:
                value = int(args[i + 1])
            except ValueError:
                print("WARN: %s expects an integer; using %s" % (flag, default))
            args = args[:i] + args[i + 2:]
    return args, value


def _pop_str(args, flag, default):
    """Strip a `--flag VALUE` pair from args. Returns (remaining_args, value)."""
    value = default
    if flag in args:
        i = args.index(flag)
        if i + 1 < len(args):
            value = args[i + 1]
            args = args[:i] + args[i + 2:]
    return args, value


def main():
    args = sys.argv[1:]
    args, seed     = _pop_int(args, "--seed", 42)
    args, duration = _pop_int(args, "--duration", DURATION)
    args, aspect   = _pop_str(args, "--aspect", ASPECT)

    # Any remaining positional args are stems to filter on (e.g. "01_wave").
    only = args or None
    generate_videos(only_names=only, seed=seed, duration=duration, aspect=aspect)


if __name__ == "__main__":
    main()
