"""Build per-product PWA icon + manifest bundles from the web icons.

Source:  assets/icons/web/<domain>.png   (the transparent sticker-style icon)
Output:  assets/pwa/<domain>/
           icon-192.png            (any-purpose, transparent)
           icon-512.png            (any-purpose, transparent)
           icon-maskable-512.png   (maskable: cream bg, icon in safe zone)
           apple-touch-icon.png    (180×180, cream bg — iOS dislikes alpha)
           favicon.ico             (16/32/48 multi-size)
           manifest.webmanifest    (name, icons, theme/background colours)

Usage:
  python tools/make_pwa.py                 # every icon in assets/icons/web/
  python tools/make_pwa.py sketch.elixpo   # one product

Each product app just serves its assets/pwa/<domain>/ folder and links the
manifest:  <link rel="manifest" href="manifest.webmanifest">

Requires Pillow (in requirements.txt). Generate the web icons first:
  python tools/generate_assets.py --web
"""

import json
import sys
from pathlib import Path

# Brand colours from MASCOT.md.
BG_COLOUR    = "#FFF8EB"   # warm ivory canvas
THEME_COLOUR = "#FF5D68"   # primary pink/red

SRC_DIR = Path("assets") / "icons" / "web"
OUT_DIR = Path("assets") / "pwa"


def _names(domain):
    """(name, short_name) for the manifest, derived from the domain."""
    special = {
        "elixpo.com": ("Elixpo", "Elixpo"),
        "oreo.elixpo": ("OreoOS", "OreoOS"),
        "url.elixpo": ("Elixpo URL", "URL"),
    }
    if domain in special:
        return special[domain]
    sub = domain.split(".")[0]
    pretty = sub.capitalize()
    return ("Elixpo " + pretty, pretty)


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _on_canvas(img, size, scale, bg_rgb):
    """Centre `img` on a `size`×`size` solid-bg canvas, scaled to `scale`."""
    from PIL import Image
    canvas = Image.new("RGBA", (size, size), bg_rgb + (255,))
    target = int(size * scale)
    icon = img.resize((target, target), Image.LANCZOS)
    off = (size - target) // 2
    canvas.alpha_composite(icon, (off, off))
    return canvas


def build(domain):
    """Build the PWA bundle for one domain. Returns True on success."""
    src = SRC_DIR / ("%s.png" % domain)
    if not src.exists():
        print("  SKIP %s — no source icon at %s" % (domain, src))
        return False

    from PIL import Image

    out = OUT_DIR / domain
    out.mkdir(parents=True, exist_ok=True)
    icon = Image.open(src).convert("RGBA")
    bg = _hex_to_rgb(BG_COLOUR)

    # Any-purpose icons keep the transparent background.
    icon.resize((192, 192), Image.LANCZOS).save(out / "icon-192.png")
    icon.resize((512, 512), Image.LANCZOS).save(out / "icon-512.png")

    # Maskable: launchers crop to circles/squircles, so fill the canvas with
    # the brand colour and keep the art inside the ~80% safe zone.
    _on_canvas(icon, 512, 0.80, bg).save(out / "icon-maskable-512.png")

    # Apple touch icon: iOS composites alpha over black, so give it the cream
    # background and a little padding.
    _on_canvas(icon, 180, 0.88, bg).convert("RGB").save(out / "apple-touch-icon.png")

    # Multi-size favicon.
    icon.save(out / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    name, short = _names(domain)
    manifest = {
        "name": name,
        "short_name": short,
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": BG_COLOUR,
        "theme_color": THEME_COLOUR,
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192",
             "type": "image/png", "purpose": "any"},
            {"src": "icon-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "any"},
            {"src": "icon-maskable-512.png", "sizes": "512x512",
             "type": "image/png", "purpose": "maskable"},
        ],
    }
    (out / "manifest.webmanifest").write_text(
        json.dumps(manifest, indent=2) + "\n")

    print("  ✓ %s → %s/  (%s)" % (domain, out, name))
    return True


def main():
    if not SRC_DIR.exists():
        print("No web icons at %s — run `python tools/generate_assets.py --web` first."
              % SRC_DIR)
        return 1

    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    if only:
        domains = only
    else:
        domains = sorted(p.stem for p in SRC_DIR.glob("*.png"))
    if not domains:
        print("No source icons found in %s" % SRC_DIR)
        return 1

    print("Building PWA bundles for %d product(s)...\n" % len(domains))
    built = sum(1 for d in domains if build(d))
    print("\nDone. %d/%d bundle(s) in %s/" % (built, len(domains), OUT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
