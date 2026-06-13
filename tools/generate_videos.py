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
  python tools/generate_videos.py --duration 8    # longer clips (default 5s)
  python tools/generate_videos.py --aspect 16:9   # widescreen (default 1:1)
  python tools/generate_videos.py --model veo     # A/B a different video model
                                                  # (non-default → videos/<stem>__<model>.mp4)

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
# patches, big sparkly eyes, pink cheeks, thick outline). The chest badge must
# read as ONE clean capital E: left vague ("E-badge") the model scribbles
# fake glyphs, so we describe the single letter explicitly and, in the style
# suffix, carve out the badge as the only place text is allowed.
MASCOT_CLAUSE = (
    "the main subject is Oreo: a cute kawaii pixel-art panda exactly like the "
    "Elixpo stickers — warm cream-white body rgb(240,238,232), dark rounded "
    "ear and eye patches rgb(38,38,48), big sparkly black eyes with white "
    "catchlights, rosy pink cheeks rgb(255,93,104), thick dark outline, and a "
    "round red chest badge rgb(220,60,50) bearing a single bold clean capital "
    "letter E in cream-white and nothing else"
)

# HD-2D look: the cute kawaii pixel character lives inside a deep, atmospheric
# diorama (think Octopath Traveler / Sea of Stars / Eastward). Depth and
# atmosphere are pushed via POSITIVE cues (depth of field, volumetric light,
# drifting particles). NOTE: these GET-endpoint models read the whole prompt
# as positive, so noun-negatives backfire — "no captions/text/watermark"
# literally summoned garbled subtitles. So we name NO text/3D/voxel nouns and
# instead state the look positively (flat hand-drawn 2D, static camera).
VIDEO_STYLE = (
    "cinematic HD-2D kawaii pixel-art diorama in the Elixpo sticker style, "
    "Oreo as a crisp cute pixel-art character with thick dark outline placed "
    "in a deep, layered world with real atmospheric depth; shallow tilt-shift "
    "depth of field with a soft bokeh blurred background and detailed "
    "foreground, warm golden volumetric light and god rays, glowing dust motes "
    "and floating particles drifting at different depths, rich painterly "
    "background shading; Oreo sits calmly in a gentle cool breeze that ruffles "
    "his fur while grass, flowers and petals sway and leaves drift through the "
    "air; lush, dreamy, alive and cozy; smooth seamless animated loop with "
    "gentle continuous lifelike motion, static locked-off camera that holds "
    "perfectly still, flat hand-drawn 2D pixel-art rendering, clean empty frame"
)

# Compact variants for models with tight prompt budgets (e.g. nova-reel caps
# the prompt at 512 chars). Same intent — kawaii pixel Oreo, single-E badge,
# HD-2D depth, ambient motion — squeezed so raw scene + clause + style fits.
MASCOT_CLAUSE_COMPACT = (
    "Oreo, a cute kawaii pixel-art panda: cream body, dark patches, pink "
    "cheeks, thick outline, red chest badge with a single capital letter E"
)

VIDEO_STYLE_COMPACT = (
    "HD-2D kawaii pixel-art diorama, deep bokeh background, depth of field, "
    "warm god rays, drifting petals, gentle breeze, seamless loop, static "
    "camera, flat 2D pixel art"
)

# Per-model caps. prompt = max prompt characters; duration = max seconds.
# Only the limits the API actually enforces are listed; absent → no cap.
MODEL_MAX_PROMPT   = {"nova-reel": 512}
MODEL_MAX_DURATION = {"veo": 8}


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


def _build_prompt(raw, compact=False):
    """Append the mascot clause and video style suffix to a raw prompt.

    `compact=True` uses the shorter clause/style so the whole prompt fits a
    tight per-model budget (e.g. nova-reel's 512-char cap).
    """
    clause = MASCOT_CLAUSE_COMPACT if compact else MASCOT_CLAUSE
    style  = VIDEO_STYLE_COMPACT if compact else VIDEO_STYLE
    return ", ".join(p for p in (raw, clause, style) if p)


def _fit_prompt(raw, model):
    """Build the prompt for `model`, respecting its prompt-length cap.

    Order of fallback: full prompt → compact clause/style → compact with the
    SCENE trimmed (the brand clause + style stay intact, since they carry the
    Oreo identity and the negatives). Always logs what it did so a quietly
    shrunk prompt never looks like the full one.
    """
    budget = MODEL_MAX_PROMPT.get(model)
    full = _build_prompt(raw)
    if not budget or len(full) <= budget:
        return full

    compact = _build_prompt(raw, compact=True)
    if len(compact) <= budget:
        print("  note: prompt > %d chars for %s — using compact style"
              % (budget, model))
        return compact

    # Still over: keep the full compact clause+style, trim only the scene.
    fixed = _build_prompt("", compact=True)   # clause + style, no scene
    room  = budget - len(fixed) - 2           # 2 for the ", " before the scene
    if room <= 0:
        print("  WARN: compact clause+style alone exceed %d for %s — "
              "truncating hard" % (budget, model))
        return compact[:budget]
    trimmed = raw[:room].rstrip(" ,")
    print("  WARN: prompt > %d for %s — trimming the scene to fit "
          "(shorten the .md for cleaner results)" % (budget, model))
    return _build_prompt(trimmed, compact=True)


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

    # Clamp duration to the model's cap (e.g. veo maxes out at 8s).
    max_d = MODEL_MAX_DURATION.get(model)
    if max_d and duration > max_d:
        print("  note: %s caps duration at %ds — clamping from %ds"
              % (model, max_d, duration))
        duration = max_d

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
        download_to(_fit_prompt(raw, model), out, seed=seed,
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
    args, model    = _pop_str(args, "--model", MODEL)

    # Any remaining positional args are stems to filter on (e.g. "01_breeze").
    only = args or None
    generate_videos(only_names=only, seed=seed, duration=duration,
                    aspect=aspect, model=model)


if __name__ == "__main__":
    main()
