"""
Generate an asset from a GitHub issue and commit it to requested/.

Used by .github/workflows/generate-asset.yml — fired when a maintainer
labels an asset-request issue with `approved`.

Inputs (via env, set by the workflow):
  ISSUE_NUMBER     e.g. "42"
  ISSUE_TITLE      raw issue title
  ISSUE_BODY       raw issue body (the form's rendered markdown)
  ISSUE_AUTHOR     login of the issue creator

Outputs:
  requested/<issue-number>-<slug>.png
  Writes a summary to $GITHUB_OUTPUT as: file, slug, asset_type, prompt
"""
from __future__ import annotations
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# This script lives at .github/scripts/ — three levels deep from the repo root.
ROOT = Path(__file__).resolve().parent.parent.parent
REQUESTED = ROOT / "requested"
REQUESTED.mkdir(exist_ok=True)

# --- Style snippets from references/MASCOT.md (kept in sync by hand for now) -------

STYLE_SUFFIX_DEFAULT = (
    "pixel art cartoon style, thick dark outline, vibrant warm celebration "
    "colours, cute kawaii style, white or cream background, square crop, "
    "no text, no watermark"
)

STYLE_SUFFIX_STICKER = (
    "pixel art cartoon style, thick dark outline, vibrant warm celebration "
    "colours, cute kawaii style, sticker design with thick white border "
    "ready for die-cut, warm cream white background, square crop, "
    "no text, no watermark"
)

MASCOT_CLAUSE = (
    "featuring the Oreo panda mascot: warm cream-white fur rgb(240,238,232), "
    "dark patches rgb(38,38,48), rosy pink cheeks rgb(255,93,104), and a "
    "red E-badge rgb(220,60,50) on the chest"
)

ASSET_SIZE = {
    "sticker": (1024, 1024),
    "icon": (1024, 1024),
    "banner": (1024, 512),
    "other": (1024, 1024),
}

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"


# --- Issue body parsing -------------------------------------------------

def _section(body: str, header: str) -> str | None:
    """Extract one section from the rendered issue-form markdown.

    GitHub renders form fields as: '### <Label>\n\n<value>\n\n' — so we
    split on `###` and look for a section whose first line is the label.
    """
    blocks = re.split(r"^###\s+", body, flags=re.MULTILINE)
    for blk in blocks:
        lines = blk.strip().splitlines()
        if not lines:
            continue
        if lines[0].strip().lower() == header.strip().lower():
            return "\n".join(lines[1:]).strip()
    return None


def parse_issue(body: str) -> dict:
    asset_type_raw = (_section(body, "Asset type") or "").lower()
    if "sticker" in asset_type_raw:
        asset_type = "sticker"
    elif "icon" in asset_type_raw:
        asset_type = "icon"
    elif "banner" in asset_type_raw:
        asset_type = "banner"
    else:
        asset_type = "other"

    # Single freeform field now drives everything.
    vibe = (_section(body, "Describe it") or "").strip()
    if vibe.lower() in {"_no response_", "no response"}:
        vibe = ""

    # Slug is auto-derived from the description (no separate field anymore):
    # first few words, kebab-cased.
    desc_slug = re.sub(r"[^a-z0-9]+", "-", vibe.lower()).strip("-")
    slug = "-".join(desc_slug.split("-")[:5]) or "asset"

    # Oreo is included by default (keeps it on-brand); opt out with "no mascot".
    low = vibe.lower()
    has_mascot = not any(k in low for k in (
        "no mascot", "no panda", "without mascot", "without panda",
        "object only", "icon only", "no oreo",
    ))

    notes = ""

    return {
        "asset_type": asset_type,
        "slug": slug,
        "vibe": vibe,
        "has_mascot": has_mascot,
        "notes": notes,
    }


def build_prompt(parsed: dict) -> str:
    parts = [parsed["vibe"]]
    if parsed["has_mascot"]:
        parts.append(MASCOT_CLAUSE)
    # Stickers and icons both get the die-cut sticker suffix so they render
    # on a flat cream background that the transparency pass can strip clean.
    if parsed["asset_type"] in ("sticker", "icon"):
        parts.append(STYLE_SUFFIX_STICKER)
    else:
        parts.append(STYLE_SUFFIX_DEFAULT)
    return ", ".join(p for p in parts if p)


# --- Pollinations fetch -------------------------------------------------

def fetch_image(prompt: str, out_path: Path, width: int, height: int,
                seed: int = 42, retries: int = 3) -> None:
    encoded = urllib.parse.quote(prompt, safe="")
    qs = urllib.parse.urlencode({
        "width": width, "height": height, "seed": seed,
        "nologo": "true", "model": "flux",
    })
    url = f"{POLLINATIONS_URL}{encoded}?{qs}"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "elixpo-assets-bot/1.0",
            })
            with urllib.request.urlopen(req, timeout=180) as r:
                out_path.write_bytes(r.read())
            return
        except Exception as e:
            last_err = e
            print(f"[fetch attempt {attempt}/{retries}] {e}", file=sys.stderr)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Pollinations fetch failed after {retries} tries: {last_err}")


# --- Main --------------------------------------------------------------

def emit_gh_output(key: str, value: str) -> None:
    """Append KEY=VALUE to $GITHUB_OUTPUT if it's set."""
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    # Multi-line safe: use heredoc-style delimiter
    delim = f"EOF_{key}_{int(time.time())}"
    with open(out, "a", encoding="utf-8") as f:
        f.write(f"{key}<<{delim}\n{value}\n{delim}\n")


def main() -> int:
    issue_number = os.environ.get("ISSUE_NUMBER")
    issue_body = os.environ.get("ISSUE_BODY", "")
    if not issue_number:
        print("ISSUE_NUMBER missing", file=sys.stderr)
        return 1

    parsed = parse_issue(issue_body)
    if not parsed["vibe"]:
        print("Issue body missing the 'Describe it' section", file=sys.stderr)
        return 2

    prompt = build_prompt(parsed)
    width, height = ASSET_SIZE[parsed["asset_type"]]
    seed = int(os.environ.get("SEED", "42"))

    filename = f"{int(issue_number):04d}-{parsed['slug']}.png"
    out_path = REQUESTED / filename
    print(f"-> {out_path.relative_to(ROOT)}")
    print(f"   type:   {parsed['asset_type']} ({width}x{height})")
    print(f"   prompt: {prompt[:120]}{'...' if len(prompt) > 120 else ''}")

    fetch_image(prompt, out_path, width, height, seed=seed)

    # Transparency pass for stickers and icons (optional — imported lazily
    # so the script still works if Pillow isn't installed).
    if parsed["asset_type"] in ("sticker", "icon"):
        try:
            sys.path.insert(0, str(ROOT / "tools"))
            from sticker_transparency import make_transparent  # type: ignore
            make_transparent(out_path, out_path, tolerance=45)
            print(f"   transparency: applied")
        except Exception as e:
            print(f"   transparency: skipped ({e})", file=sys.stderr)

    emit_gh_output("file", str(out_path.relative_to(ROOT)))
    emit_gh_output("slug", parsed["slug"])
    emit_gh_output("asset_type", parsed["asset_type"])
    emit_gh_output("prompt", prompt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
