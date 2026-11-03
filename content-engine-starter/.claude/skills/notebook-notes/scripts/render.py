#!/usr/bin/env python3
"""Render a notebook-notes page to PNG.

  python3 render.py BODY.html OUT.png [--size portrait|square] [--paper ruled|dots|grid|plain] [--margin]
        [--binding spiral|gutter|none] [--surface desk|wood|slate|none|PHOTO.jpg] [--hand indie|shadows|architect|nanum]
        [--head SAME_CHOICES|caps] [--pen green|blue|red|ink] [--marker yellow|orange|green|pink] [--seed N]

BODY.html holds the inside of the page only. The page is drawn flat, then (unless --surface none)
placed slightly rotated on a desk with a soft shadow, like a photo of a real notebook.
Output is 2x: portrait 2160x2700, square 2160x2160. No signature or footer.
"""
import html as H, os, random, sys
import numpy as np
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


def noise(h, w, sy, sx, rng):
    """Smooth value noise, stretched sx wide and sy tall."""
    gh, gw = max(2, int(h / sy) + 2), max(2, int(w / sx) + 2)
    g = rng.random((gh, gw)).astype(np.float32)
    return np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255

def oak(size, seed=7):
    """Photo-like oak planks: cathedral grain, soft streaks, seams and daylight from the top left."""
    w, h = size
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    n_pl = int(rng.integers(3, 5)); plank_h = h / n_pl
    pi = np.floor(ys / plank_h).astype(int)
    off = rng.uniform(0, 6.28, n_pl + 1); tone = rng.uniform(-0.08, 0.08, n_pl + 1); xc = rng.uniform(-0.2, 1.2, n_pl + 1) * w
    warp = noise(h, w, 260, 900, rng) * 70 + noise(h, w, 60, 400, rng) * 12
    yc = (pi + 0.5) * plank_h
    # broad cathedral figure
    arch = (ys - yc + warp) / plank_h * 70 + ((xs - xc[pi]) / w) ** 2 * 14 * np.where(pi % 2, 1, -1)
    fig = 0.5 + 0.5 * np.sin(arch + off[pi])
    fig = fig ** 7 + 0.25 * (0.5 + 0.5 * np.sin(arch * 0.25 + off[pi]))
    # soft streaks along the grain (stretched in x)
    streak = noise(h, w, 6, 260, rng) * 0.6 + noise(h, w, 2.5, 120, rng) * 0.4
    t = np.clip(0.5 * fig + 0.4 * streak + tone[pi] + 0.05, 0, 1)
    light = np.array([205, 160, 112], np.float32); mid = np.array([166, 118, 74], np.float32); dark = np.array([110, 70, 40], np.float32)
    img = np.where(t[..., None] < 0.5, light + (mid - light) * (t[..., None] / 0.5), mid + (dark - mid) * ((t[..., None] - 0.5) / 0.5))
    # plank seams: dark groove plus a faint highlight
    m = ys % plank_h
    img[(m < 3) & (ys > 5)] *= 0.5
    img[(m >= 3) & (m < 5)] *= 1.07
    img *= 0.96 + 0.06 * rng.random((h, w, 1)).astype(np.float32)
    # daylight from the top left, darker corners
    d = np.sqrt(((xs - w * 0.25) / w) ** 2 + ((ys - h * 0.15) / h) ** 2)
    img *= (1.14 - 0.42 * d)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))


def surface(size, kind, rng):
    """A textured surface: oak planks for wood, otherwise a soft gradient plus grain."""
    if os.path.isfile(kind):  # a photo of a real desk: scaled to cover the canvas and centre-cropped
        im = Image.open(kind).convert("RGB")
        sc = max(size[0] / im.width, size[1] / im.height)
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        l, t = (im.width - size[0]) // 2, (im.height - size[1]) // 2
        return im.crop((l, t, l + size[0], t + size[1]))
    if kind == "wood":
        return oak(size, rng.randrange(1 << 30))
    w, h = size
    c0, c1 = SURFACES[kind]
    img = Image.new("RGB", size, c0)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
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
        contact = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        contact.paste((0, 0, 0, 90), (x + 3, y + 5), rot.split()[3])
        bg = Image.alpha_composite(bg, contact.filter(ImageFilter.GaussianBlur(4)))
        bg.alpha_composite(rot, (x, y))
        img = bg
    img.convert("RGB").save(out)
    os.remove(flat)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
