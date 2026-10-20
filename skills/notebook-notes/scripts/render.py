#!/usr/bin/env python3
"""Render a notebook-notes page to PNG.

  python3 render.py BODY.html OUT.png [--size portrait|square] [--paper ruled|dots|grid|plain] [--margin]
        [--binding spiral|gutter|none] [--surface desk|wood|slate|none] [--hand indie|shadows|architect|nanum]
        [--head SAME_CHOICES|caps] [--pen green|blue|red|ink] [--marker yellow|orange|green|pink] [--seed N]

BODY.html holds the inside of the page only. The page is drawn flat, then (unless --surface none)
placed slightly rotated on a desk with a soft shadow, like a photo of a real notebook.
Output is 2x: portrait 2160x2700, square 2160x2160. No signature or footer.
"""
import html as H, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")
SHARED = ASSETS   # rough.js + sketch.js ship inside this Skill, so it works on its own
CANVAS = {"portrait": (1080, 1350), "square": (1080, 1080)}
SCALE = {"indie": 1.0, "shadows": 1.0, "architect": 0.92, "nanum": 1.42, "caps": 1.12}  # equal-looking text across hands
HANDS = {"indie": "'Indie Flower'", "shadows": "'Shadows Into Light'", "architect": "'Architects Daughter'",
         "nanum": "'Nanum Pen Script'", "caps": "'Just Another Hand'"}
PENS = {"green": "#3f9b3a", "blue": "#2f62b5", "red": "#cc3b2b", "ink": "#1d1d1f"}
MARKERS = {"yellow": "#e4f53b", "orange": "#ffb35c", "green": "#9be37a", "pink": "#ff7eb6"}
SURFACES = {"desk": ((198, 186, 168), (176, 162, 142)), "wood": ((150, 108, 72), (118, 80, 52)), "slate": ((96, 100, 106), (70, 74, 80))}
CHROMIUM = "/opt/pw-browsers/chromium"


def surface(size, kind, rng):
    """A plain textured surface: soft vertical gradient plus grain."""
    w, h = size
    c0, c1 = SURFACES[kind]
    img = Image.new("RGB", size, c0)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    if kind == "wood":
        for _ in range(140):
            y = rng.uniform(0, h); amp = rng.uniform(2, 9)
            d.line([(x, y + amp * ((x / w * 7 + rng.random()) % 1 - .5)) for x in range(0, w + 40, 40)], fill=tuple(max(0, c - 18) for c in c1), width=2)
    noise = Image.effect_noise(size, 18).convert("RGB")
    return Image.blend(img, Image.composite(noise, img, Image.new("L", size, 40)), 0.25)


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    body_path, out = os.path.abspath(a[0]), os.path.abspath(a[1])
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    size, paper, binding, surf = opt("--size", "portrait"), opt("--paper", "ruled"), opt("--binding", "spiral"), opt("--surface", "desk")
    hk, hd = opt("--hand", "indie"), opt("--head", opt("--hand", "indie"))
    hand, head = HANDS[hk], HANDS[hd]
    pen, marker, seed = PENS.get(opt("--pen", "green"), opt("--pen", "green")), MARKERS.get(opt("--marker", "yellow"), opt("--marker", "yellow")), int(opt("--seed", "7"))
    cw, ch = CANVAS[size]
    pw, ph = (cw, ch) if surf == "none" else (cw - 90, ch - 100)
    classes = " ".join(c for c in ["page", paper if paper != "plain" else "", "margin" if "--margin" in a else "",
                                    binding if binding != "none" else ""] if c)
    page = f"""<!doctype html><html><head><meta charset="utf-8"><base href="file://{ASSETS}/">
<link rel="stylesheet" href="notebook.css"><style>:root{{--pen:{pen};--marker:{marker};--hand:{hand},cursive;--head:{head},cursive;--scale:{SCALE[hk]};--hscale:{SCALE[hd]}}}
.page{{width:{pw}px;height:{ph}px}}</style></head>
<body><div class="{classes}" data-seed="{seed}" data-sig="off">
{open(body_path, encoding="utf-8").read()}
</div><script src="file://{SHARED}/rough.js"></script></body></html>"""
    page_path = os.path.splitext(out)[0] + ".page.html"
    open(page_path, "w", encoding="utf-8").write(page)
    flat = os.path.splitext(out)[0] + ".flat.png"
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": CHROMIUM} if os.path.exists(CHROMIUM) else {}))
        pg = b.new_page(viewport={"width": pw, "height": ph}, device_scale_factor=2)
        warns = []
        pg.on("console", lambda m: warns.append(m.text) if m.type in ("warning", "error") else None)
        pg.goto("file://" + page_path)
        pg.evaluate("document.fonts.ready")
        pg.add_script_tag(path=os.path.join(ASSETS, "notebook.js"))
        pg.add_script_tag(path=os.path.join(SHARED, "sketch.js"))
        pg.wait_for_function("window.__sketchDone === true && window.__notebookDone === true", timeout=10000)
        over = pg.evaluate("""() => { const p = document.querySelector('.page').getBoundingClientRect(); const out = [];
          document.querySelectorAll('.page *:not(svg):not(svg *):not(.gutter-shade)').forEach(e => { const r = e.getBoundingClientRect();
            if (r.width && (r.right > p.right - 30 || r.bottom > p.bottom - 10)) out.push((e.className || e.tagName) + ' ' + Math.round(r.right) + 'x' + Math.round(r.bottom)); });
          return out.slice(0, 8); }""")
        pg.locator(".page").screenshot(path=flat)
        b.close()
    for m in warns:
        print("WARN", m)
    if over:
        print("WARN close to or past the page edge:", "; ".join(over))
    img = Image.open(flat).convert("RGBA")
    if surf != "none":
        rng = random.Random(seed)
        W, Hh = cw * 2, ch * 2
        bg = surface((W, Hh), surf, rng).convert("RGBA")
        ang = rng.uniform(-1.2, 1.2)
        rot = img.rotate(ang, resample=Image.BICUBIC, expand=True)
        x, y = (W - rot.width) // 2 + rng.randint(-10, 10), (Hh - rot.height) // 2 + rng.randint(-6, 6)
        shadow = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 110), (x + 14, y + 22), rot.split()[3])
        bg = Image.alpha_composite(bg, shadow.filter(ImageFilter.GaussianBlur(22)))
        bg.alpha_composite(rot, (x, y))
        img = bg
    img.convert("RGB").save(out)
    os.remove(flat)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
