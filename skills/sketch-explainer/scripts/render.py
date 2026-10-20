#!/usr/bin/env python3
"""Render a sketch explainer to PNG.

  python3 render.py BODY.html OUT.png [--size portrait|square|landscape] [--seed N]
                    [--pen red|coral|blue|ink] [--marker teal|yellow|green|pink] [--frame] [--sig "Your Name · yoursite.com"]

BODY.html holds only the inside of the page (title, layout, punchline) using the markup in
assets/sketch.js. The PNG is exported at 2x: portrait 2160x2700, square 2160x2160, landscape 2560x1920.
"""
import html as H, os, sys
from playwright.sync_api import sync_playwright

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
SIZES = {"portrait": (1080, 1350), "square": (1080, 1080), "landscape": (1280, 960)}
PENS = {"red": "#cc3b2b", "coral": "#cc785c", "blue": "#2f5fb3", "ink": "#1c1b19"}
MARKERS = {"teal": "#5db8a6", "yellow": "#f3e04a", "green": "#a6d96a", "pink": "#f4a3c0"}
CHROMIUM = "/opt/pw-browsers/chromium"


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    body_path, out = os.path.abspath(a[0]), os.path.abspath(a[1])
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    size, seed = opt("--size", "portrait"), opt("--seed", "7")
    pen, marker = PENS.get(opt("--pen", "red"), opt("--pen", "red")), MARKERS.get(opt("--marker", "teal"), opt("--marker", "teal"))
    w, h = SIZES[size]
    classes = " ".join(["page", size] + (["frame"] if "--frame" in a else []))
    # Signature: off unless --sig is given (the text comes from "Make it yours" in SKILL.md).
    sig_text = opt("--sig", "")
    sig = f' data-sig-text="{H.escape(sig_text)}"' if sig_text and "--no-sig" not in a else ' data-sig="off"'
    page = f"""<!doctype html><html><head><meta charset="utf-8"><base href="file://{ASSETS}/">
<link rel="stylesheet" href="sketch.css"><style>:root{{--pen:{pen};--marker:{marker}}}</style></head>
<body><div class="{classes}" data-seed="{H.escape(seed)}"{sig}>
{open(body_path, encoding="utf-8").read()}
</div><script src="rough.js"></script></body></html>"""
    page_path = os.path.splitext(out)[0] + ".page.html"
    open(page_path, "w", encoding="utf-8").write(page)
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": CHROMIUM} if os.path.exists(CHROMIUM) else {}))
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        warns = []
        pg.on("console", lambda m: warns.append(m.text) if m.type in ("warning", "error") else None)
        pg.goto("file://" + page_path)
        pg.evaluate("document.fonts.ready")
        pg.add_script_tag(path=os.path.join(ASSETS, "sketch.js"))
        pg.wait_for_function("window.__sketchDone === true", timeout=10000)
        over = pg.evaluate("""() => { const p = document.querySelector('.page').getBoundingClientRect(); const out = [];
          document.querySelectorAll('.page *:not(svg):not(svg *)').forEach(e => { const r = e.getBoundingClientRect();
            if (r.width && (r.right > p.right - 40 || r.bottom > p.bottom - 20 || r.left < p.left + 40)) out.push((e.className || e.tagName) + ' ' + Math.round(r.right) + 'x' + Math.round(r.bottom)); });
          return out.slice(0, 8); }""")
        pg.locator(".page").screenshot(path=out)
        b.close()
    for m in warns:
        print("WARN", m)
    if over:
        print("WARN close to or past the page edge:", "; ".join(over))
    print("wrote", out)


if __name__ == "__main__":
    main()
