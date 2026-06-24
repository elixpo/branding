#!/usr/bin/env python3
"""
Cozy doodle photo editor — Pollinations image-to-image.

Reads raw photos from editing/raw/, applies the doodle-aesthetic edit prompt
(prompt.md, in this folder) with an image-editing model, and writes results to
editing/edited/. Each raw image is first uploaded to media.pollinations.ai to
get a reference URL, then passed to the generation endpoint as ?image=<url>.

  Pipeline:  raw/photo.jpg  --upload-->  media URL  --gptimage-->  edited/photo.<model>.jpg

Free image-editing models (paid_only models are intentionally omitted — see
image_models.md). All accept text+image input:

  gptimage        GPT Image 1 Mini   fast & affordable           (default)
  gptimage-large  GPT Image 1.5      higher fidelity edits
  kontext         FLUX.1 Kontext     in-context editing
  klein           FLUX.2 Klein 4B    fast editing
  nova-canvas     Nova Canvas        editing & inpainting

Usage:
  python edit.py                       # edit every raw/ image with gptimage
  python edit.py --model gptimage-large
  python edit.py --only myphoto.jpg    # one file (repeatable)
  python edit.py --model kontext --only a.jpg --only b.png   # compare a model
  python edit.py --force               # re-edit even if output exists
  python edit.py --seed 7              # fix the seed for reproducibility

Auth: reads the key from $POLLINATIONS_KEY / $POLLINATIONS_API_KEY, falling back
to the POLLINATIONS_KEY line in ../.env.local. Get a key at enter.pollinations.ai.
"""

import argparse
import json
import mimetypes
import os
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "raw"
OUT_DIR = HERE / "edited"
PROMPT_FILE = HERE / "prompt.md"

GEN_BASE = "https://gen.pollinations.ai"
MEDIA_BASE = "https://media.pollinations.ai"

# The endpoints reject urllib's default UA (403); send an explicit one.
USER_AGENT = "elixpo-editing/1.0 (+pollinations img2img)"

# Free (non paid_only) models that accept image input, per image_models.md.
FREE_EDIT_MODELS = {"gptimage", "gptimage-large", "kontext", "klein", "nova-canvas"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def load_key() -> str:
    for var in ("POLLINATIONS_KEY", "POLLINATIONS_API_KEY"):
        v = os.environ.get(var)
        if v:
            return v.strip()
    env_local = HERE.parent / ".env.local"
    if env_local.exists():
        for line in env_local.read_text().splitlines():
            line = line.strip()
            if line.startswith("POLLINATIONS_KEY"):
                val = line.split("=", 1)[1].strip().strip("\"'")
                if val:
                    return val
    sys.exit("No API key. Set POLLINATIONS_KEY or add it to ../.env.local "
             "(get one at https://enter.pollinations.ai).")


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


def edit(image_url: str, prompt: str, model: str, key: str, seed, width, height):
    """Run image-to-image edit, return (bytes, content_type)."""
    params = {
        "model": model,
        "image": image_url,
        "nologo": "true",
        "key": key,
    }
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


def out_path(stem: str, model: str, ctype: str) -> Path:
    ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(ctype, ".png")
    return OUT_DIR / f"{stem}.{model}{ext}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Cozy doodle photo editor (Pollinations img2img).")
    ap.add_argument("--model", default="gptimage", help="edit model (default: gptimage)")
    ap.add_argument("--only", action="append", default=[], metavar="FILE",
                    help="edit only this raw/ filename (repeatable)")
    ap.add_argument("--seed", type=int, default=None, help="fix seed for reproducibility")
    ap.add_argument("--width", type=int, default=None, help="output width (model permitting)")
    ap.add_argument("--height", type=int, default=None, help="output height (model permitting)")
    ap.add_argument("--force", action="store_true", help="re-edit even if output exists")
    args = ap.parse_args()

    if args.model not in FREE_EDIT_MODELS:
        print(f"warning: '{args.model}' is not in the free edit-model set "
              f"({', '.join(sorted(FREE_EDIT_MODELS))}); proceeding anyway.", file=sys.stderr)

    key = load_key()
    prompt = PROMPT_FILE.read_text().strip()
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
        dest = out_path(src.stem, args.model, "image/jpeg")
        existing = next((OUT_DIR.glob(f"{src.stem}.{args.model}.*")), None)
        if existing and not args.force:
            print(f"skip {src.name}: {existing.name} exists (use --force to redo)")
            continue
        try:
            print(f"[{src.name}] uploading…", flush=True)
            url = upload(src, key)
            print(f"[{src.name}] editing with {args.model}…", flush=True)
            data, ctype = edit(url, prompt, args.model, key, args.seed, args.width, args.height)
            dest = out_path(src.stem, args.model, ctype)
            dest.write_bytes(data)
            print(f"[{src.name}] -> {dest.relative_to(HERE)} ({len(data)//1024} KB)")
        except Exception as e:  # noqa: BLE001 — surface any per-file failure, keep going
            print(f"[{src.name}] FAILED: {e}", file=sys.stderr)
            failures += 1

    if failures:
        print(f"\nDone with {failures} failure(s).", file=sys.stderr)
        return 1
    print("\nAll edits complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
