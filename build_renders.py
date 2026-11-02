#!/usr/bin/env python3
"""
build_renders.py
Scans images/renders/ and fills the grid in RENDERS.html with every image it
finds. Re-run it whenever you add, remove or rename images.

Put this file in your site root (next to index.html), then:
    python build_renders.py

Makes small thumbnail copies in images/renders/_thumbs/ (needs Pillow:
pip install pillow). Clicking a thumb still opens the original full-res file.
Skip thumbnails with:  python build_renders.py --no-thumbs

Images are shown in filename order (numbers sort naturally: 2 before 10).
To pin an order, put a number at the start of the filename.
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "images" / "renders"
HTML = ROOT / "RENDERS.html"
THUMB_DIR_NAME = "_thumbs"
THUMB_MAX = 800          # longest side in px
EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALT = "Render"


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def url(path):
    rel = path.relative_to(ROOT).as_posix()
    return "/".join(quote(part) for part in rel.split("/"))


def make_thumb(src, dst):
    from PIL import Image
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im.thumbnail((THUMB_MAX, THUMB_MAX))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (0, 0, 0))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        im.save(dst, "JPEG", quality=85, optimize=True)


def main():
    use_thumbs = "--no-thumbs" not in sys.argv
    if use_thumbs:
        try:
            import PIL  # noqa: F401
        except ImportError:
            print("Pillow not installed, skipping thumbnails (pip install pillow to enable).")
            use_thumbs = False

    if not IMG_DIR.is_dir():
        sys.exit(f"Can't find {IMG_DIR}")
    if not HTML.is_file():
        sys.exit(f"Can't find {HTML}")

    files = sorted(
        (f for f in IMG_DIR.iterdir() if f.is_file() and f.suffix.lower() in EXTS),
        key=natural_key,
    )
    if not files:
        sys.exit("No images found in images/renders")

    links = []
    for f in files:
        full = url(f)
        if use_thumbs:
            t = IMG_DIR / THUMB_DIR_NAME / (f.stem + "_" + f.suffix.lower().lstrip(".") + ".jpg")
            make_thumb(f, t)
            thumb = url(t)
        else:
            thumb = full
        links.append(
            f'            <a href="{full}" data-full><img src="{thumb}" alt="{ALT}" loading="lazy" decoding="async"></a>'
        )
    print(f"  {len(files)} images")

    html = HTML.read_text(encoding="utf-8")
    g = re.compile(r"(<!-- GALLERY:START[^>]*-->\n).*?(            <!-- GALLERY:END -->)", re.S)
    if not g.search(html):
        sys.exit("Markers GALLERY:START/END missing from RENDERS.html")
    html = g.sub(lambda m: m.group(1) + "\n".join(links) + "\n" + m.group(2), html)
    HTML.write_text(html, encoding="utf-8")
    print("RENDERS.html updated.")


if __name__ == "__main__":
    main()
