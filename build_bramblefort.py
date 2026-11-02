#!/usr/bin/env python3
"""
build_bramblefort.py
Scans images/bramblefort/<Folder>/ and fills the gallery sections of
BRAMBLEFORT.html. Re-run it whenever you add, remove or rename images.

Put this file in your site root (next to index.html), then:
    python build_bramblefort.py

Optional: makes small thumbnail copies (needs Pillow: pip install pillow)
so the page doesn't load every huge PNG. Clicking a thumb still opens the
original full-res file. Skip thumbnails with:  python build_bramblefort.py --no-thumbs
"""
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "images" / "bramblefort"
HTML = ROOT / "BRAMBLEFORT.html"
THUMB_DIR_NAME = "_thumbs"
THUMB_MAX = 800          # longest side in px
EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# folder name -> (box title, thumb shape)
# Order here is the order on the page. Folders not listed go just before Characters.
CATEGORIES = [
    ("Watermill",      "WATERMILL",       "natural"),
    ("Bathhouse",      "BATHHOUSE",       "natural"),
    ("Cellar",         "CELLAR",          "natural"),
    ("FishingVillage", "FISHING VILLAGE", "natural"),
    ("Characters",     "CHARACTERS",      "natural"),
    ("Assets",         "ASSETS",          "natural"),
]
ALT = {"Assets": "BRAMBLEFORT asset", "Characters": "BRAMBLEFORT character"}

SHAPE_CLASS = {"natural": " natural"}


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def pretty(name):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name).upper()


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

    found = {d.name: d for d in IMG_DIR.iterdir() if d.is_dir() and not d.name.startswith("_")}
    order = [c for c in CATEGORIES if c[0] in found]
    listed = {c[0] for c in CATEGORIES}
    extra = [(n, pretty(n), "natural") for n in sorted(found) if n not in listed]
    at = next((i for i, c in enumerate(order) if c[0] == "Characters"), len(order))
    order[at:at] = extra
    for name, _, _ in CATEGORIES:
        if name not in found:
            print(f"  (no folder for {name}, skipped)")

    sections, nav = [], []
    for folder, title, shape in order:
        files = sorted(
            (f for f in found[folder].iterdir() if f.is_file() and f.suffix.lower() in EXTS),
            key=natural_key,
        )
        if not files:
            print(f"  {folder}: empty, skipped")
            continue
        alt = ALT.get(folder, f"BRAMBLEFORT {title.lower()} level")
        links = []
        for f in files:
            full = url(f)
            if use_thumbs:
                t = IMG_DIR / THUMB_DIR_NAME / folder / (f.stem + ".jpg")
                make_thumb(f, t)
                thumb = url(t)
            else:
                thumb = full
            links.append(
                f'            <a href="{full}" data-full><img src="{thumb}" alt="{alt}" loading="lazy" decoding="async"></a>'
            )
        sid = slug(folder)
        sections.append(
            f'        <section class="old-box work-box" id="{sid}">\n'
            f'          <h2 class="box-title">{title}</h2>\n'
            f'          <div class="thumb-grid cols-3{SHAPE_CLASS[shape]}">\n'
            + "\n".join(links)
            + "\n          </div>\n        </section>\n"
        )
        nav.append(f'            <li><a href="#{sid}">{title.title()}</a></li>')
        print(f"  {folder}: {len(files)} images")

    html = HTML.read_text(encoding="utf-8")
    g = re.compile(r"(<!-- GALLERY:START[^>]*-->\n).*?(        <!-- GALLERY:END -->)", re.S)
    n = re.compile(r"(<!-- NAV:START -->\n).*?(            <!-- NAV:END -->)", re.S)
    if not g.search(html) or not n.search(html):
        sys.exit("Markers GALLERY:START/END or NAV:START/END missing from BRAMBLEFORT.html")
    html = g.sub(lambda m: m.group(1) + "\n".join(sections) + "\n" + m.group(2), html)
    html = n.sub(lambda m: m.group(1) + "\n".join(nav) + "\n" + m.group(2), html)
    HTML.write_text(html, encoding="utf-8")
    print("BRAMBLEFORT.html updated.")


if __name__ == "__main__":
    main()
