"""Composite OG card text onto an AI-generated design.

The AI generates the DESIGN ONLY (text-free: dotted matrix, entangled one-line
Oreo, a couple of geometric shapes) at 16:9. This script overlays the typography
ourselves with Pillow — so the model never fumbles letters — at fixed, correct
proportions in the card's left negative space.

  prompts/og/<site>/prompts/<name>.md     (## Text block: eyebrow/headline/sub/url)
  prompts/og/<site>/output/<name>.bg.png  (AI design)
        → prompts/og/<site>/output/<name>.png   (final card)

Usage:
  python pipeline/og_compose.py                      # every site, every card
  python pipeline/og_compose.py mails.elixpo         # one site
  python pipeline/og_compose.py mails.elixpo default # one card
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Canvas (16:9) ─────────────────────────────────────────────────────────────
W, H = 1280, 720
MARGIN = 84
COL_W = 660          # left text column; the design/panda lives to the right

# ── Palette (the light "oreo" system) ────────────────────────────────────────
INK    = (33, 33, 33)
SLATE  = (117, 117, 138)
MUTED  = (147, 147, 159)
CORAL  = (255, 119, 89)

# ── Fonts ─────────────────────────────────────────────────────────────────────
# Drop Fraunces / Space Mono / Inter .ttf into pipeline/fonts/ to upgrade from the
# DejaVu fallbacks. First existing path in each list wins.
_FONT_DIR = Path(__file__).resolve().parent / "fonts"
_SYS = "/usr/share/fonts/truetype"
FONT_CANDIDATES = {
    "serif": [  # bold, high-contrast headline
        _FONT_DIR / "Fraunces-Bold.ttf",
        _FONT_DIR / "PlayfairDisplay-Bold.ttf",
        Path("%s/dejavu/DejaVuSerif-Bold.ttf" % _SYS),
    ],
    "mono": [  # eyebrow / url
        _FONT_DIR / "SpaceMono-Regular.ttf",
        Path("%s/dejavu/DejaVuSansMono.ttf" % _SYS),
    ],
    "sans": [  # body / sub copy
        _FONT_DIR / "Inter-Regular.ttf",
        Path("%s/dejavu/DejaVuSans.ttf" % _SYS),
    ],
}


def _font(kind, size):
    for p in FONT_CANDIDATES[kind]:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


# ── Text helpers ──────────────────────────────────────────────────────────────
def _read_text_block(md_path):
    """Parse the `## Text` block of a card .md into a dict of key: value."""
    text = Path(md_path).read_text()
    if "## Text" not in text:
        return {}
    after = text.split("## Text", 1)[1]
    out = {}
    for line in after.splitlines():
        if line.startswith("##"):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def _text_w(draw, s, font, tracking=0):
    if not s:
        return 0
    w = sum(draw.textlength(c, font=font) for c in s)
    return int(w + tracking * (len(s) - 1))


def _draw_tracked(draw, pos, s, font, fill, tracking=0):
    """draw.text with manual letter-spacing (Pillow has none)."""
    x, y = pos
    for c in s:
        draw.text((x, y), c, font=font, fill=fill)
        x += draw.textlength(c, font=font) + tracking
    return x


def _wrap(draw, words, font, max_w):
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_headline(draw, text, max_w, max_lines=3, hi=78, lo=40):
    """Largest serif size whose wrapped headline fits the column in ≤max_lines."""
    words = text.split()
    for size in range(hi, lo - 1, -2):
        font = _font("serif", size)
        lines = _wrap(draw, words, font, max_w)
        if len(lines) <= max_lines and all(draw.textlength(l, font=font) <= max_w for l in lines):
            return font, lines, size
    font = _font("serif", lo)
    return font, _wrap(draw, words, font, max_w), lo


# ── Compose one card ──────────────────────────────────────────────────────────
def compose_card(card_md, bg_path, out_path):
    """Overlay the card's `## Text` onto its AI design → out_path (1280×720)."""
    txt = _read_text_block(card_md)
    eyebrow  = txt.get("eyebrow", "")
    headline = txt.get("headline", "")
    sub      = txt.get("sub", "")
    url      = txt.get("url", "")

    img = Image.open(bg_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    draw = ImageDraw.Draw(img)

    # Eyebrow (mono, uppercase, wide tracking)
    y = 128
    if eyebrow:
        ef = _font("mono", 22)
        _draw_tracked(draw, (MARGIN, y), eyebrow.upper(), ef, MUTED, tracking=6)
        y += 54

    # Headline (bold serif, auto-fit, wrapped)
    hf, lines, hsize = _fit_headline(draw, headline, COL_W)
    line_h = int(hsize * 1.12)
    y += 8
    head_top = y
    for ln in lines:
        draw.text((MARGIN, y), ln, font=hf, fill=INK)
        y += line_h
    head_bottom = y

    # Heavy coral underline
    ul_w = min(COL_W * 0.55, 360)
    ul_y = head_bottom + 14
    draw.rounded_rectangle([MARGIN, ul_y, MARGIN + ul_w, ul_y + 10], radius=5, fill=CORAL)

    # Sub copy (sans, slate, wrapped)
    if sub:
        sf = _font("sans", 23)
        sy = ul_y + 40
        for ln in _wrap(draw, sub.split(), sf, COL_W):
            draw.text((MARGIN, sy), ln, font=sf, fill=SLATE)
            sy += int(23 * 1.4)

    # URL (mono, bottom-left, tracked)
    if url:
        uf = _font("mono", 19)
        _draw_tracked(draw, (MARGIN, H - MARGIN - 18), url, uf, MUTED, tracking=2)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


# ── CLI: re-composite existing designs ────────────────────────────────────────
def main(argv):
    base = Path("prompts") / "og"
    if not base.exists():
        print("No %s" % base)
        return
    sites = [d for d in sorted(base.iterdir()) if d.is_dir() and not d.name.startswith(".")]

    site_filter, card_filter = None, None
    if argv:
        names = [s.name for s in sites]
        if argv[0] in names:
            site_filter, card_filter = argv[0], (argv[1:] or None)
        else:
            card_filter = argv

    n = 0
    for site in sites:
        if site_filter and site.name != site_filter:
            continue
        out_dir = site / "output"
        for md in sorted((site / "prompts").glob("*.md")):
            if md.stem.lower() in {"readme", "style", "palette"}:
                continue
            if card_filter and md.stem not in card_filter:
                continue
            bg = out_dir / ("%s.bg.png" % md.stem)
            if not bg.exists():
                print("  skip %s/%s — no design (%s); run --og first"
                      % (site.name, md.stem, bg.name))
                continue
            out = compose_card(md, bg, out_dir / ("%s.png" % md.stem))
            print("  composited → %s" % out)
            n += 1
    print("Done. Composited %d card(s)." % n)


if __name__ == "__main__":
    main(sys.argv[1:])
