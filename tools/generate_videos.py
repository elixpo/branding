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

load_dotenv()

KEY      = os.getenv("POLLINATIONS_KEY")
BASE     = "https://gen.pollinations.ai/video"
MODEL    = "ltx-2"
DURATION = 4         # seconds — short promo loops
ASPECT   = "1:1"     # square, matches the rest of the mascot assets

# ── Style snippets (kept in sync with MASCOT.md by hand) ─────────────────────
# Appended to every prompt so clips stay on-brand even when the .md only
# describes the scene. Oreo is always the subject, rendered in the
# vectorized-anime video look — NOT the pixel-art sticker look.

MASCOT_CLAUSE = (
    "the main subject is Oreo the panda: warm cream-white fur, dark patches, "
    "rosy pink cheeks, and a red E-badge on the chest"
)

# The signature motion: a fixed, static shot where the panda holds completely
# still while only the surrounding environment drifts — a calm ambient loop.
VIDEO_STYLE = (
    "vectorized aesthetic anime style, clean vector shapes, soft gradients, "
    "lush vibrant saturated colours, cinematic fixed static shot, the panda "
    "remains completely motionless while the surrounding environment gently "
    "sways and ripples with subtle natural motion as if blown by a soft "
    "invisible breeze, seamless loop, no text, no watermark"
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


def download_to(prompt, out_path, seed=42, duration=DURATION, aspect=ASPECT):
    """Render one clip and save the MP4 to out_path. Returns True on success."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print("→ %s  (%ss, %s)\n  %s..." % (out_path, duration, aspect, prompt[:90]))

    if not KEY:
        print("  ERROR: POLLINATIONS_KEY not set in .env — cannot authenticate")
        return False

    # NOTE: User-Agent is REQUIRED — the API returns 403 without it.
    headers = {
        "Authorization": "Bearer %s" % KEY,
        "User-Agent":    "OreoBadge/1.0",
    }
    enc = urllib.parse.quote(prompt)
    qs  = urllib.parse.urlencode({
        "model":       MODEL,
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
            print("  saved %d bytes  [model=%s]" % (len(data), MODEL))
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
                print("  FATAL HTTP %d %s   [model=%s]" % (e.code, e.reason, MODEL))
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


def generate_videos(only_names=None, seed=42, duration=DURATION, aspect=ASPECT):
    """Generate clips from prompts/videos/*.md → videos/<stem>.mp4."""
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
          (len(mds), duration, aspect, seed, MODEL))
    for md in mds:
        raw = _read_prompt(md)
        if not raw:
            print("  SKIP %s — no ## Prompt block" % md.name)
            continue
        out = out_dir / ("%s.mp4" % md.stem)
        download_to(_build_prompt(raw), out, seed=seed,
                    duration=duration, aspect=aspect)
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
