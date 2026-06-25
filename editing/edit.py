#!/usr/bin/env python3
"""
Cozy doodle photo editor — context-aware Pollinations image-to-image.

Reads raw photos from raw/ (repo root), and for each one:
  1. uploads it to media.pollinations.ai            -> reference URL
  2. runs a vision pass (chat completions w/ image)  -> scene + themed doodles + face?
  3. composes a context-aware prompt = action-forward doodle asks + prompt.md style
     (+ a hard face/subject lock when a person/face is detected)
  4. edits with an image model (default klein)       -> edited/<name>.<model>.<ext>
     then snaps the result to the original aspect ratio (no white padding)

The vision step is what makes the doodles match THIS image (bookstore -> books &
bookmarks, café -> mugs & steam, beach -> waves & shells) instead of generic decor.

Free image-editing models (paid_only excluded — see image_models.md), all text+image:
  klein           FLUX.2 Klein 4B    preserves subject + adds doodles   (default)
  kontext         FLUX.1 Kontext     max preservation, few doodles
  gptimage-large  GPT Image 1.5      rich doodles but redraws the face
  gptimage        GPT Image 1 Mini   faster/cheaper, also redraws
  nova-canvas     Nova Canvas        editing & inpainting

Usage:
  python editing/edit.py                       # edit every raw/ image (klein)
  python editing/edit.py --only raw_6.jpeg     # one file (repeatable)
  python editing/edit.py --model gptimage-large
  python editing/edit.py --aspect 9:16         # force a ratio (default: original)
  python editing/edit.py --no-vision           # skip analysis, send template verbatim
  python editing/edit.py --force --seed 7      # overwrite, reproducible seed

Auth: $POLLINATIONS_KEY / $POLLINATIONS_API_KEY, falling back to the POLLINATIONS_KEY
line in .env.local at the repo root. Get a key at enter.pollinations.ai.
"""

import argparse
import io
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent      # editing/
ROOT = HERE.parent                          # repo root
RAW_DIR = ROOT / "raw"
OUT_DIR = ROOT / "edited"
PROMPT_FILE = HERE / "prompt.md"

GEN_BASE = "https://gen.pollinations.ai"
MEDIA_BASE = "https://media.pollinations.ai"
USER_AGENT = "elixpo-editing/1.0 (+pollinations img2img)"  # endpoints 403 the default urllib UA

FREE_EDIT_MODELS = {"gptimage", "gptimage-large", "kontext", "klein", "nova-canvas"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# Always prepended — models weight leading instructions most. Action-forward so
# edit models (esp. kontext) actually ADD the doodles, while scoping preservation to
# the existing subject. Terse: the whole prompt rides in the GET URL (long -> 414).
# Short neutral lead — prompt.md governs the decoration style/density. We only pin the
# core overlay rule: edit the real photo, don't regenerate it; decorate around the subject.
OVERLAY_GUARD = (
    "EDIT the real photo, do NOT regenerate it: keep the original pixels and subject "
    "exactly as-is, and ADD the scrapbook decoration described below in the areas "
    "AROUND the subject — never drawn on or over the subject, and add no new person. "
)

# Prepended (after the overlay guard) when a person is detected — leading weight.
FACE_FREEZE_LEAD = (
    "CRITICAL: a real person is present. The face is a FROZEN, DO-NOT-TOUCH zone — "
    "reproduce every facial pixel exactly from the input (eyes, nose, mouth, brows, "
    "skin, glasses, expression). Make ZERO pixel changes on or near the face, and keep "
    "all doodles/text far from it. "
)

# Appended whenever the vision pass detects a human in the photo — trailing weight.
SUBJECT_LOCK = (
    " SUBJECT LOCK (highest priority): keep the person 100% intact and identical to the "
    "input. Do NOT redraw, shift, recolor, smooth, beautify, age, reshape or regenerate "
    "the person — above all the FACE: make NO pixel change on or within a wide margin "
    "around the face. Copy face, expression, skin, hair, glasses, clothing and pose "
    "pixel-for-pixel. Every doodle, caption and overlay stays OFF the subject, in the "
    "surrounding empty space only. If you cannot place a doodle without touching the "
    "subject, omit it. The subject — especially the face — must look pixel-identical to "
    "the original photo."
)


def load_key() -> str:
    for var in ("POLLINATIONS_KEY", "POLLINATIONS_API_KEY"):
        v = os.environ.get(var)
        if v:
            return v.strip()
    env_local = ROOT / ".env.local"
    if env_local.exists():
        for line in env_local.read_text().splitlines():
            line = line.strip()
            if line.startswith("POLLINATIONS_KEY"):
                val = line.split("=", 1)[1].strip().strip("\"'")
                if val:
                    return val
    sys.exit("No API key. Set POLLINATIONS_KEY or add it to .env.local "
             "(get one at https://enter.pollinations.ai).")


def _post_json(url: str, payload: dict, key: str, timeout: int):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def upload(path: Path, key: str) -> str:
    """Upload a local image, return its content-addressed media URL."""
    boundary = uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = b"".join([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode(),
        f"Content-Type: {mime}\r\n\r\n".encode(),
        path.read_bytes(),
        f"\r\n--{boundary}--\r\n".encode(),
    ])
    req = urllib.request.Request(f"{MEDIA_BASE}/upload", data=body, method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())
    url = resp.get("url")
    if not url:
        raise RuntimeError(f"upload returned no url: {resp}")
    return url


def describe_scene(image_url: str, key: str, model: str) -> dict:
    """Vision pass: return {scene, theme, motifs[], has_person}."""
    instruction = (
        "You are art-directing a cozy doodle overlay for this photo. Respond with ONLY a "
        "JSON object, no prose, with keys: "
        '"theme" (2-4 words), '
        '"scene" (one vivid sentence describing setting, key objects, mood, palette), '
        '"motifs" (array of 6-7 short, cute hand-drawn doodle ideas that match this '
        "scene — e.g. flowers, leaves, books, stars, sparkles, hearts, scene icons — "
        "just a small tasteful set, not a dense sheet), "
        '"has_person" (true if any human face/person is visible, else false).'
    )
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": instruction},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    }
    data = _post_json(f"{GEN_BASE}/v1/chat/completions", payload, key, timeout=120)
    content = data["choices"][0]["message"]["content"]
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m:
        raise RuntimeError(f"vision returned no JSON: {content[:200]}")
    info = json.loads(m.group(0))
    info.setdefault("motifs", [])
    info.setdefault("has_person", False)
    return info


def compose_prompt(template: str, info: dict | None, place_hint: str = "") -> str:
    """Build a compact prompt: hard guard + style + this-image scene context.

    place_hint biases doodle placement into the area that survives an aspect crop
    (e.g. for 9:16 the left/right edges get cut, so keep doodles central/top/bottom).

    Kept short on purpose — the entire prompt travels in the GET URL, and overly
    long prompts both trip HTTP 414 and dilute the model's focus.
    """
    lead = OVERLAY_GUARD
    if info is not None and info.get("has_person"):
        lead += FACE_FREEZE_LEAD

    # Concrete asks go HIGH (right after the guard) so conservative edit models
    # like kontext actually render them instead of dropping them at the tail.
    asks = []
    if place_hint:
        asks.append(place_hint)
    if info is not None:
        if info.get("theme"):
            asks.append(f"Scene theme: {info['theme']}.")
        motifs = info.get("motifs") or []
        if motifs:
            asks.append("Scene-matched doodles to include: " + ", ".join(motifs[:7]) + ".")
    ask_block = (" " + " ".join(asks)) if asks else ""

    composed = lead + ask_block + " " + template
    if info is not None and info.get("has_person"):
        composed += SUBJECT_LOCK
    return composed


def edit(image_url, prompt, model, key, seed, width, height):
    """Run image-to-image edit, return (bytes, content_type)."""
    params = {"model": model, "image": image_url, "nologo": "true", "key": key}
    if seed is not None:
        params["seed"] = str(seed)
    if width:
        params["width"] = str(width)
    if height:
        params["height"] = str(height)
    url = f"{GEN_BASE}/image/{urllib.parse.quote(prompt)}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("User-Agent", USER_AGENT)
    with urllib.request.urlopen(req, timeout=600) as r:
        ctype = r.headers.get("Content-Type", "")
        data = r.read()
    if not ctype.startswith("image/"):
        raise RuntimeError(f"expected an image, got {ctype}: {data[:300]!r}")
    return data, ctype


# Canonical output canvases (no white padding — strict aspect via a tiny center-crop).
ASPECTS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "4:5": (1080, 1350),
    "1:1": (1080, 1080),
    "3:4": (1080, 1440),
}


def fit_to_size(data: bytes, tw: int, th: int):
    """Snap the edit to an EXACT tw×th canvas. No padding: center-crop the (small)
    aspect mismatch, then resize. We already ask the model for this aspect, so the
    crop is minimal and no white bars are ever introduced. Returns (bytes, ctype)."""
    edit = Image.open(io.BytesIO(data)).convert("RGB")
    ew, eh = edit.size
    target = tw / th
    if abs(ew / eh - target) > 0.005:
        if ew / eh > target:               # too wide -> trim sides
            nw = round(eh * target)
            x = (ew - nw) // 2
            edit = edit.crop((x, 0, x + nw, eh))
        else:                              # too tall -> trim top/bottom
            nh = round(ew / target)
            y = (eh - nh) // 2
            edit = edit.crop((0, y, ew, y + nh))
    if edit.size != (tw, th):
        edit = edit.resize((tw, th), Image.LANCZOS)
    buf = io.BytesIO()
    edit.save(buf, format="JPEG", quality=95)
    return buf.getvalue(), "image/jpeg"


def gen_dims(src: Path):
    """The canvas we ask the MODEL to render — always the input's own aspect ratio
    (scaled to a sane long edge). Generating at the source aspect means the model
    never has to stretch the subject to fill a different shape (no 'fat' distortion)."""
    ow, oh = Image.open(src).size
    long_edge = 1536
    if ow >= oh:
        gw = min(ow, long_edge); gh = round(gw * oh / ow)
    else:
        gh = min(oh, long_edge); gw = round(gh * ow / oh)
    return gw, gh


def out_dims(src: Path, aspect: str, width, height):
    """The final saved canvas. 'original' = same aspect as input; a named aspect
    (e.g. 9:16) is reached later by center-cropping the model's original-aspect output
    (proportions preserved — never stretched). Explicit --width/--height override."""
    if aspect == "original":
        ow, oh = gen_dims(src)
    else:
        ow, oh = ASPECTS[aspect]
    return (width or ow), (height or oh)


def out_path(stem: str, model: str, ctype: str) -> Path:
    ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(ctype, ".png")
    return OUT_DIR / f"{stem}.{model}{ext}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Context-aware cozy doodle photo editor.")
    ap.add_argument("--model", default="klein",
                    help="edit model (default: klein — FLUX.2, preserves the subject & "
                         "framing while adding doodles; kontext = max preservation but "
                         "few doodles; gptimage-large = rich doodles but redraws the face)")
    ap.add_argument("--only", action="append", default=[], metavar="FILE",
                    help="edit only this raw/ filename (repeatable)")
    ap.add_argument("--seed", type=int, default=None, help="fix seed for reproducibility")
    ap.add_argument("--aspect", default="original", choices=["original", *ASPECTS],
                    help="output aspect ratio (default: original = same as input); "
                         "pass e.g. 9:16 to force a different one")
    ap.add_argument("--width", type=int, default=None, help="override output width")
    ap.add_argument("--height", type=int, default=None, help="override output height")
    ap.add_argument("--no-vision", action="store_true",
                    help="skip the scene-analysis pass; send prompt.md verbatim")
    ap.add_argument("--describe-model", default="openai",
                    help="vision model for the analysis pass (default: openai)")
    ap.add_argument("--no-fit", action="store_true",
                    help="skip snapping the output to the exact target size")
    ap.add_argument("--force", action="store_true", help="re-edit even if output exists")
    args = ap.parse_args()

    if args.model not in FREE_EDIT_MODELS:
        print(f"warning: '{args.model}' is not in the free edit-model set "
              f"({', '.join(sorted(FREE_EDIT_MODELS))}); proceeding anyway.", file=sys.stderr)

    key = load_key()
    template = PROMPT_FILE.read_text().strip()
    OUT_DIR.mkdir(exist_ok=True)

    if args.only:
        targets = [RAW_DIR / name for name in args.only]
    else:
        targets = sorted(p for p in RAW_DIR.iterdir()
                         if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    if not targets:
        print(f"No images in {RAW_DIR}. Drop photos there (png/jpg/webp) and rerun.")
        return 1

    failures = 0
    for src in targets:
        if not src.exists():
            print(f"skip {src.name}: not found", file=sys.stderr)
            failures += 1
            continue
        existing = next((OUT_DIR.glob(f"{src.stem}.{args.model}.*")), None)
        if existing and not args.force:
            print(f"skip {src.name}: {existing.name} exists (use --force to redo)")
            continue
        try:
            print(f"[{src.name}] uploading…", flush=True)
            url = upload(src, key)

            info = None
            if not args.no_vision:
                print(f"[{src.name}] analyzing scene…", flush=True)
                info = describe_scene(url, key, args.describe_model)
                tag = "person/face detected — face lock ON" if info.get("has_person") else "no person"
                print(f"[{src.name}] theme: {info.get('theme','?')} ({tag})")

            gw, gh = gen_dims(src)                                 # generate at source aspect
            ow, oh = out_dims(src, args.aspect, args.width, args.height)

            # If the output aspect crops the generated frame, keep doodles in the kept zone.
            place_hint = ""
            if abs(gw / gh - ow / oh) > 0.01:
                if ow / oh < gw / gh:   # taller/narrower output -> sides get cropped
                    place_hint = ("PLACEMENT: the final image is cropped to a TALLER, "
                                  "narrower frame, so put EVERY doodle and caption note in "
                                  "the central column and the TOP and BOTTOM bands — keep "
                                  "them well away from the far LEFT and RIGHT edges, which "
                                  "are cut off. ")
                else:                   # wider/shorter output -> top/bottom get cropped
                    place_hint = ("PLACEMENT: the final image is cropped to a WIDER, "
                                  "shorter frame, so put EVERY doodle and caption note along "
                                  "the LEFT and RIGHT sides and center — keep them well away "
                                  "from the very TOP and BOTTOM edges, which are cut off. ")
            prompt = compose_prompt(template, info, place_hint)
            print(f"[{src.name}] editing with {args.model} @ {gw}x{gh} -> out {ow}x{oh}…",
                  flush=True)
            data, ctype = edit(url, prompt, args.model, key, args.seed, gw, gh)
            if not args.no_fit:
                data, ctype = fit_to_size(data, ow, oh)            # crop to target aspect, no stretch
            dest = out_path(src.stem, args.model, ctype)
            dest.write_bytes(data)
            print(f"[{src.name}] -> {dest.relative_to(ROOT)} ({len(data)//1024} KB)")
        except Exception as e:  # noqa: BLE001 — surface per-file failure, keep going
            print(f"[{src.name}] FAILED: {e}", file=sys.stderr)
            failures += 1

    if failures:
        print(f"\nDone with {failures} failure(s).", file=sys.stderr)
        return 1
    print("\nAll edits complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
