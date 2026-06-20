"""Compose every generated sticker in stickers/ into one printable sheet.

Reads PNGs from `stickers/` (skipping anything starting with `.` or
named `sheet.png`), arranges them on a grid in filename order, and
writes the result to `stickers/sheet.png`. Useful for:

  - Previewing the full set after generation.
  - Sending one file to a print shop instead of a dozen.
  - Posting a single image to social.

You drive the layout by **how many stickers per row/column** and a
**fixed per-sticker cell size** — the sheet dimensions are then computed
to fit. Output goes to `stickers/sheet.png`.

Usage:
    python tools/compile_sticker_sheet.py
    python tools/compile_sticker_sheet.py --cols 5            # 5 per row
    python tools/compile_sticker_sheet.py --cols 5 --rows 4   # fixed 5x4 grid
    python tools/compile_sticker_sheet.py --cell-w 400 --cell-h 400
    python tools/compile_sticker_sheet.py --gap 24 --margin 40

Requires: Pillow (already in oreoOS/requirements.txt for the optimiser).
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("error: Pillow not installed — pip install pillow", file=sys.stderr)
    sys.exit(1)


STICKER_DIR = Path("stickers")
OUT_PATH    = STICKER_DIR / "sheet.png"
# Never composite a previously-generated sheet back into a new one.
SKIP_NAMES  = {"sheet.png", "oreoOS_gummy_sheet.png"}


def parse_args():
    p = argparse.ArgumentParser(
        description="Composite stickers/*.png into a single sheet "
                    "(grid + cell size drive the output dimensions).",
    )
    p.add_argument("--cols", type=int, default=4,
                   help="stickers per row (default 4)")
    p.add_argument("--rows", type=int, default=None,
                   help="stickers per column; default = enough to fit all")
    p.add_argument("--cell-w", dest="cell_w", type=int, default=512,
                   help="fixed sticker cell width in px (default 512)")
    p.add_argument("--cell-h", dest="cell_h", type=int, default=512,
                   help="fixed sticker cell height in px (default 512)")
    p.add_argument("--gap",  type=int, default=30,
                   help="gap between stickers in px (default 30)")
    p.add_argument("--margin", type=int, default=20,
                   help="outer page margin in px (default 20)")
    p.add_argument("--bg",   default="#FFF8EB",
                   help="sheet background colour (default warm ivory)")
    return p.parse_args()


def collect_stickers():
    """Every .png in stickers/ except the output itself. Sorted by name
    so the numeric prefixes (01_, 02_, ...) drive the grid order."""
    if not STICKER_DIR.is_dir():
        print(f"error: {STICKER_DIR}/ not found (run from repo root)",
              file=sys.stderr)
        sys.exit(1)
    files = sorted(
        p for p in STICKER_DIR.glob("*.png")
        if p.name not in SKIP_NAMES and not p.name.startswith(".")
    )
    if not files:
        print(f"error: no PNGs found in {STICKER_DIR}/", file=sys.stderr)
        print("       generate them first via Pollinations using the prompts",
              file=sys.stderr)
        print("       in prompts/stickers/, then re-run this script.",
              file=sys.stderr)
        sys.exit(1)
    return files


def main():
    args = parse_args()
    files = collect_stickers()

    cols   = max(1, args.cols)
    cell_w = max(1, args.cell_w)
    cell_h = max(1, args.cell_h)
    gap    = max(0, args.gap)
    margin = max(0, args.margin)

    # Rows: use the requested count, else just enough to hold every sticker.
    auto_rows = (len(files) + cols - 1) // cols
    rows = max(1, args.rows) if args.rows else auto_rows

    # A fixed grid (--rows given) has a capacity; warn if some don't fit.
    capacity = cols * rows
    if len(files) > capacity:
        print(f"warning: {len(files)} stickers but grid holds {capacity} "
              f"({cols}x{rows}) — placing the first {capacity}, "
              f"dropping {len(files) - capacity}")
        files = files[:capacity]

    # Sheet size follows from the fixed cell size + grid + gaps + margins.
    sheet_w = 2 * margin + cols * cell_w + (cols - 1) * gap
    sheet_h = 2 * margin + rows * cell_h + (rows - 1) * gap

    print(f"compiling {len(files)} stickers into a {cols}x{rows} grid "
          f"({cell_w}x{cell_h} cells) -> {sheet_w}x{sheet_h} sheet")

    sheet = Image.new("RGB", (sheet_w, sheet_h), args.bg)

    for i, fp in enumerate(files):
        r, c = divmod(i, cols)
        x = margin + c * (cell_w + gap)
        y = margin + r * (cell_h + gap)
        try:
            im = Image.open(fp).convert("RGBA")
        except Exception as e:
            print(f"  ! skipped {fp.name}: {e}")
            continue
        # Fit within the cell without stretching, then centre it.
        im.thumbnail((cell_w, cell_h), Image.LANCZOS)
        ox = x + (cell_w - im.width)  // 2
        oy = y + (cell_h - im.height) // 2
        # Use the alpha channel as the paste mask so the warm-cream
        # sheet background shows through any transparent edges.
        sheet.paste(im, (ox, oy), im)
        print(f"  + {fp.name} -> cell ({r}, {c})")

    sheet.save(OUT_PATH, optimize=True)
    print(f"wrote {OUT_PATH} ({sheet_w}x{sheet_h}, {len(files)} stickers)")


if __name__ == "__main__":
    main()
