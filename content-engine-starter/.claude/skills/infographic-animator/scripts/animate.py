#!/usr/bin/env python3
"""Turn a static infographic HTML page into an animated GIF.

  python3 animate.py INFOGRAPHIC.html MOTION.json OUT.gif [--fps 20] [--max-mb 4.8] [--frames-dir DIR]
                    [--still T OUT.png] [--substack OUT-substack.gif]

MOTION.json describes the build-up as steps on one timeline (seconds):
  {"hold": 3.5,
   "steps": [
     {"sel": "h1 .hl-mark", "fx": "wipe",  "at": 0.3, "dur": 0.6},
     {"sel": ".big",        "fx": "count", "at": 0.6, "dur": 1.2},
     {"sel": "svg.hero",    "fx": "draw",  "at": 0.9, "dur": 1.6, "stagger": 0.05},
     {"sel": ".sites svg",  "fx": "pop",   "at": 2.0, "dur": 0.35, "stagger": 0.08}]}

Effects: fade (opacity + 16px rise), pop (scale up + fade), wipe (reveal left to right),
draw (SVG strokes draw themselves; dashed strokes fade instead), count (the first number in
the element counts up from 0). `stagger` applies the effect to each matched element in turn.
Every element named in a step starts hidden; everything else is visible from frame 0.

The page is stepped frame by frame (no real-time playback), so every render is identical.
The last frame is held for `hold` seconds as a single GIF frame, and the GIF loops forever.
If the file is over --max-mb it is re-encoded smaller (fewer colours, then smaller scale).
--substack OUT2.gif also writes a lighter copy from the same frames, under 2.4 MB (Substack's limit is about 2.5 MB).
Photos on the graphic (<img>: the headshot, logos) are weighted when the GIF's 256 colours are chosen, so they
stay in colour instead of turning grey next to large flat areas.

LOOP MODE ("mode": "loop") makes the parts of a finished graphic busy instead of revealing it:
frame 0 is the whole graphic, and the GIF is one seamless loop of `period` seconds.
  {"mode": "loop", "period": 6, "fps": 15,
   "loops": [
     {"sel": "#gear",      "fx": "spin",   "turns": 1},
     {"sel": "#word",      "fx": "cycle",  "words": ["ask", "refine", "copy", "paste"]},
     {"sel": ".pane",      "fx": "build",  "at": 0.1, "step": 0.15, "until": 0.95},
     {"sel": ".card",      "fx": "travel", "path": [[0, 0, 0, 0, 0], [0.1, 0, 0, 0, 1], [0.7, 118, 0, 0, 1], [1, 124, 300, 50, 0]]}]}
Loop effects (times are fractions of the loop, 0 to 1):
  spin   turns about its own centre; "turns" (whole number, negative = anticlockwise)
  bob    moves up and down; "amp" px, "cycles" per loop, "axis" "y" or "x"
  blink  flickers; "cycles" per loop, "low" opacity
  cycle  swaps its text through "words", equal time each, between "from" and "to" (default the whole
         loop); outside that it shows "rest"
  build  matched elements appear one after another ("at", "step", "fade") and clear at "until"
  show   visible only between "from" and "to" ("fade" for soft edges); from > to wraps round the loop
         (e.g. from 0.9 to 0.3), so two shows can swap one drawing for another (an open and a closed lid)
  flip   mirrors left-right between "from" and "to", wrapping the same way (a head looking away)
  travel moves along keyframes [u, dx, dy, rotate, opacity, scale] from where it's drawn; several matched
         elements are spaced evenly round the loop (a conveyor), unless "spread": false
Every effect can take "offset" (0 to 1) to shift it in the loop. Animate elements that have no
transform attribute of their own (wrap them in a <g> if needed): the effect replaces it.
--still T also saves the frame at T seconds at 2x as a PNG (the static version of the same loop).
"""
import json
import os
import shutil
import sys
import tempfile

from playwright.sync_api import sync_playwright

CHROMIUM = "/opt/pw-browsers/chromium"

JS = r"""
(steps) => {
  const ease = p => p < 0 ? 0 : p > 1 ? 1 : 1 - Math.pow(1 - p, 3);
  const items = [];
  for (const s of steps) {
    const els = [...document.querySelectorAll(s.sel)];
    if (!els.length) throw new Error('No element matches ' + s.sel);
    let k = 0;
    for (const el of els) {
      if (s.fx === 'draw') {
        const shapes = el.matches('path,line,polyline,polygon,rect,circle,ellipse') ? [el]
          : [...el.querySelectorAll('path,line,polyline,polygon,rect,circle,ellipse')];
        const texts = el.matches('text') ? [] : [...el.querySelectorAll('text')];
        for (const sh of shapes) {
          const cs = getComputedStyle(sh);
          const dashed = cs.strokeDasharray && cs.strokeDasharray !== 'none';
          const stroked = cs.stroke && cs.stroke !== 'none';
          let len = 0; try { len = sh.getTotalLength(); } catch (e) {}
          const at = s.at + (s.stagger || 0) * k++;
          if (stroked && !dashed && len > 0) items.push({el: sh, fx: 'draw', at, dur: s.dur, len, fill: cs.fillOpacity});
          else items.push({el: sh, fx: 'fadeonly', at, dur: s.dur});
        }
        for (const t of texts) items.push({el: t, fx: 'fadeonly', at: s.at + s.dur * 0.6, dur: s.dur * 0.5});
      } else if (s.fx === 'count') {
        const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let n; while ((n = w.nextNode())) { if (/\d/.test(n.nodeValue)) break; }
        if (!n) throw new Error('count: no number in ' + s.sel);
        const m = n.nodeValue.match(/(\d[\d,]*\.?\d*)/);
        const raw = m[1], dec = (raw.split('.')[1] || '').length, target = parseFloat(raw.replace(/,/g, ''));
        items.push({el, fx: 'count', at: s.at + (s.stagger || 0) * k++, dur: s.dur, node: n, orig: n.nodeValue, raw, dec, target});
      } else {
        items.push({el, fx: s.fx, at: s.at + (s.stagger || 0) * k++, dur: s.dur});
      }
    }
  }
  window.__end = Math.max(...items.map(i => i.at + i.dur));
  window.__render = (t) => {
    for (const i of items) {
      const p = ease((t - i.at) / i.dur), st = i.el.style;
      if (i.fx === 'fade') { st.opacity = p; st.transform = `translateY(${(1 - p) * 16}px)`; }
      else if (i.fx === 'fadeonly') { st.opacity = p; }
      else if (i.fx === 'pop') { st.opacity = Math.min(1, p * 2); st.transform = `scale(${0.6 + 0.4 * p})`; st.transformOrigin = 'center'; st.transformBox = 'fill-box'; }
      else if (i.fx === 'wipe') { st.clipPath = `inset(-20% ${(1 - p) * 100}% -20% 0)`; }
      else if (i.fx === 'draw') { st.strokeDasharray = i.len; st.strokeDashoffset = i.len * (1 - p); st.fillOpacity = p < 1 ? 0 : ''; st.opacity = p > 0 ? 1 : 0; }
      else if (i.fx === 'count') {
        const v = (i.target * p).toFixed(i.dec);
        i.node.nodeValue = p >= 1 ? i.orig : i.orig.replace(i.raw, v);
        st.opacity = p > 0 ? 1 : 0;
      } else throw new Error('Unknown effect ' + i.fx);
    }
  };
  return window.__end;
}
"""

LOOP_JS = r"""
(loops) => {
  const ease = p => p < 0 ? 0 : p > 1 ? 1 : p * p * (3 - 2 * p);
  const warn = [], items = [];
  for (const s of loops) {
    const els = [...document.querySelectorAll(s.sel)];
    if (!els.length) throw new Error('No element matches ' + s.sel);
    els.forEach((el, i) => {
      if (el.getAttribute && el.getAttribute('transform') && ['spin', 'bob', 'flip', 'travel'].includes(s.fx))
        warn.push(s.sel + ' has its own transform attribute; wrap it in a <g> so the effect does not replace it');
      if (s.fx === 'spin' || s.fx === 'flip' || s.fx === 'travel') { el.style.transformBox = 'fill-box'; el.style.transformOrigin = 'center'; }
      items.push({el, s, i, n: els.length, text: el.textContent});
    });
  }
  window.__loop = (t, period) => {
    const per = new Map();
    for (const it of items) per.set(it.el, {tf: [], op: 1});
    const add = (el, k, v) => { const o = per.get(el); if (k === 'tf') o.tf.push(v); else o.op *= v; };
    const win = (f, from, to, fade) => from <= to ? ease((f - from) / fade) * (1 - ease((f - to) / fade))
      : Math.max(ease((f - from) / fade), 1 - ease((f - to) / fade));
    const inside = (f, from, to) => from <= to ? (f >= from && f < to) : (f >= from || f < to);
    for (const {el, s, i, n, text} of items) {
      const spread = (s.fx === 'travel' && s.spread !== false) ? i / n : 0;
      const f = ((t / period + (s.offset || 0) + spread) % 1 + 1) % 1;
      if (s.fx === 'spin') add(el, 'tf', `rotate(${f * 360 * (s.turns || 1)}deg)`);
      else if (s.fx === 'bob') { const d = Math.sin(f * 2 * Math.PI * (s.cycles || 1)) * (s.amp || 2); add(el, 'tf', s.axis === 'x' ? `translate(${d}px,0)` : `translate(0,${d}px)`); }
      else if (s.fx === 'blink') add(el, 'op', (Math.floor(f * 2 * (s.cycles || 4)) % 2) ? 1 : (s.low ?? 0.15));
      else if (s.fx === 'cycle') {
        const w = s.words, a = s.from ?? 0, b = s.to ?? 1;
        el.textContent = (f >= a && f < b) ? w[Math.floor((f - a) / (b - a) * w.length) % w.length] : (s.rest ?? w[0]);
      }
      else if (s.fx === 'build') {
        const at = s.at ?? 0.1, step = s.step ?? 0.15, fade = s.fade ?? 0.06, until = s.until ?? 0.95;
        add(el, 'op', ease((f - at - i * step) / fade) * (1 - ease((f - until) / 0.04)));
      }
      else if (s.fx === 'show') add(el, 'op', win(f, s.from, s.to, s.fade ?? 0.02));
      else if (s.fx === 'flip') { if (inside(f, s.from, s.to)) add(el, 'tf', 'scaleX(-1)'); }
      else if (s.fx === 'travel') {
        const k = s.path; let a = k[0], b = k[k.length - 1];
        for (let j = 0; j < k.length - 1; j++) if (f >= k[j][0] && f <= k[j + 1][0]) { a = k[j]; b = k[j + 1]; break; }
        const u = b[0] === a[0] ? 0 : (f - a[0]) / (b[0] - a[0]), L = (x, y) => x + (y - x) * u;
        add(el, 'tf', `translate(${L(a[1], b[1])}px,${L(a[2], b[2])}px) rotate(${L(a[3] || 0, b[3] || 0)}deg) scale(${L(a[5] ?? 1, b[5] ?? 1)})`);
        add(el, 'op', L(a[4] ?? 1, b[4] ?? 1));
      }
      else throw new Error('Unknown loop effect ' + s.fx);
    }
    for (const [el, o] of per) { el.style.transform = o.tf.join(' '); el.style.opacity = o.op; }
    return document.body.offsetHeight;  // force layout before the screenshot
  };
  return warn;
}
"""


PHOTOS_JS = "() => [...document.querySelectorAll('img, svg image')].map(e => e.getBoundingClientRect()).filter(r => r.width > 8 && r.height > 8).map(r => [r.left, r.top, r.right, r.bottom])"


def png_wrapper(png, cfg, tmp):
    """PNG-only fallback: split the image into horizontal bands (cfg["bands"]: [[y0, y1], ...] in px)
    and expose them as .band-1, .band-2 ... for the steps to animate. Anything outside a band is
    visible from frame 0 (put the headline and sign-off strip outside the bands)."""
    from PIL import Image
    w, h = Image.open(png).size
    if (w, h) not in ((1080, 1350), (2160, 2700)):
        sys.exit(f"{png} is {w}x{h}; expected 1080x1350 or 2160x2700 (bands are given in 1080x1350 px)")
    src = "file://" + png
    bands = cfg.get("bands") or sys.exit("PNG input needs \"bands\" in the motion file")
    base = "".join(f"<div class='band-{i}' style='position:absolute;left:0;top:{y0}px;width:1080px;height:{y1 - y0}px;"
                   f"background:url({src}) 0 -{y0}px/1080px 1350px'></div>" for i, (y0, y1) in enumerate(bands, 1))
    # the page under the bands shows the canvas colour sampled from the image's top-left corner
    bg = "#%02x%02x%02x" % Image.open(png).convert("RGB").getpixel((4, 4))
    cover = "".join(f"<div style='position:absolute;left:0;top:{y0}px;width:1080px;height:{y1 - y0}px;background:{bg}'></div>"
                    for y0, y1 in bands)
    out = os.path.join(tmp, "wrapper.html")
    open(out, "w").write(f"<!doctype html><html><body style='margin:0;width:1080px;height:1350px;position:relative;"
                         f"background:url({src}) 0 0/1080px 1350px'>{cover}{base}</body></html>")
    return out


def encode(frames_dir, n, frame_s, hold, out, colors, scale, photos=None):
    """One shared palette (taken from the finished frame) for every frame, so nothing flickers.
    Photos (the headshot, a logo: boxes in 1080x1350 px) are weighted up when the palette is chosen,
    otherwise a small photo loses its colours to the large flat areas and comes out grey.
    Pillow writes exact per-frame delays and only the changed rectangle of each frame."""
    from PIL import Image
    load = lambda i: Image.open(os.path.join(frames_dir, f"f{i:04d}.png")).convert("RGB")
    size = (round(1080 * scale), round(1350 * scale))
    fit = lambda im: im if im.size == size else im.resize(size, Image.LANCZOS)
    last = fit(load(n - 1))
    src = last
    if photos:
        crops = [last.crop(tuple(round(v * scale) for v in b)) for b in photos]
        crops = [c for c in crops if c.width > 4 and c.height > 4]
        if crops:
            # one strip of all the photos, repeated until it covers about a third of the frame's area
            strip = Image.new("RGB", (sum(c.width for c in crops), max(c.height for c in crops)), last.getpixel((2, 2)))
            x = 0
            for c in crops:
                strip.paste(c, (x, 0)); x += c.width
            reps = max(1, int(size[0] * size[1] / 3 / (strip.width * strip.height)))
            cols = max(1, size[0] // strip.width)
            rows = -(-reps // cols)
            src = Image.new("RGB", (size[0], size[1] + rows * strip.height), last.getpixel((2, 2)))
            src.paste(last, (0, 0))
            for k in range(reps):
                src.paste(strip, ((k % cols) * strip.width, size[1] + (k // cols) * strip.height))
    pal = src.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    frames = [fit(load(i)).quantize(palette=pal, dither=Image.Dither.NONE) for i in range(n)]
    ms = round(frame_s * 1000 / 10) * 10
    frames[0].save(out, save_all=True, append_images=frames[1:], loop=0, disposal=1, optimize=False,
                   duration=[ms] * (n - 1) + [round(hold * 1000)])
    return os.path.getsize(out) / 1e6


LADDER = [(256, 1), (128, 1), (96, 1), (256, 0.8), (128, 0.8), (96, 0.8), (128, 0.7), (96, 0.6)]
SUBSTACK_MB = 2.4   # Substack Notes reject GIFs over about 2.5 MB


def encode_fit(frames_dir, n, frame_s, hold, out, max_mb, photos):
    """Encode, then step down colours and scale until the file is under max_mb."""
    for colors, scale in LADDER:
        mb = encode(frames_dir, n, frame_s, hold, out, colors, scale, photos)
        print(f"  {os.path.basename(out)}: {colors} colours at {int(1080 * scale)}px wide: {mb:.2f} MB")
        if mb <= max_mb:
            return
    print(f"WARN {os.path.basename(out)} still over {max_mb} MB; shorten the loop, lower --fps or animate fewer parts")


def main():
    a = sys.argv[1:]
    if len(a) < 3:
        sys.exit(__doc__)
    html, motion, out = (os.path.abspath(x) for x in a[:3])
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    fps, max_mb = opt("--fps", 20), opt("--max-mb", 4.8)
    cfg = json.load(open(motion))
    hold = float(cfg.get("hold", 3.5))
    keep = os.path.abspath(opt("--frames-dir", "")) if "--frames-dir" in a else ""
    tmp = keep or tempfile.mkdtemp(prefix="gifframes-")
    os.makedirs(tmp, exist_ok=True)
    if html.lower().endswith(".png"):
        html = png_wrapper(html, cfg, tmp)
    still = (float(a[a.index("--still") + 1]), os.path.abspath(a[a.index("--still") + 2])) if "--still" in a else None
    substack = os.path.abspath(a[a.index("--substack") + 1]) if "--substack" in a else None
    if cfg.get("mode") == "loop":
        return loop_main(html, cfg, out, opt("--fps", int(cfg.get("fps", 15))), max_mb, tmp, keep, still, substack)
    with sync_playwright() as p:
        kw = {"executable_path": CHROMIUM} if os.path.exists(CHROMIUM) else {}
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)  # 2x capture, scaled down: smoother text
        pg.goto("file://" + html)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        photos = pg.evaluate(PHOTOS_JS)
        end = pg.evaluate(JS, cfg["steps"])
        n = int(round(end * fps)) + 1
        if n > 240:
            fps = max(8, int(239 / end))
            n = int(round(end * fps)) + 1
            print(f"too many frames; dropped to {fps} fps")
        for i in range(n):
            pg.evaluate(f"window.__render({i / fps})")
            pg.screenshot(path=os.path.join(tmp, f"f{i:04d}.png"))
        b.close()
    print(f"{n} frames at {fps} fps, {end:.2f}s build + {hold}s hold")
    encode_fit(tmp, n, 1 / fps, hold, out, max_mb, photos)
    if substack:
        encode_fit(tmp, n, 1 / fps, hold, substack, SUBSTACK_MB, photos)
    if not keep:
        shutil.rmtree(tmp)
    print("wrote", out)


def loop_main(html, cfg, out, fps, max_mb, tmp, keep, still, substack):
    """Loop mode: step the loop once, frame by frame; the GIF repeats it seamlessly (no hold)."""
    period = float(cfg.get("period", 6))
    n = int(round(period * fps))
    if n > 240:
        fps = int(239 / period); n = int(round(period * fps))
        print(f"too many frames; dropped to {fps} fps")
    with sync_playwright() as p:
        kw = {"executable_path": CHROMIUM} if os.path.exists(CHROMIUM) else {}
        b = p.chromium.launch(**kw)
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto("file://" + html)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        photos = pg.evaluate(PHOTOS_JS)
        for w in pg.evaluate(LOOP_JS, cfg["loops"]):
            print("WARN", w)
        if still:
            pg.evaluate(f"window.__loop({still[0]}, {period})")
            pg.screenshot(path=still[1])
            print("wrote still", still[1])
        for i in range(n):
            pg.evaluate(f"window.__loop({i / fps}, {period})")
            pg.screenshot(path=os.path.join(tmp, f"f{i:04d}.png"))
        b.close()
    print(f"{n} frames at {fps} fps, one {period:g}s loop")
    encode_fit(tmp, n, 1 / fps, 1 / fps, out, max_mb, photos)
    if substack:
        encode_fit(tmp, n, 1 / fps, 1 / fps, substack, SUBSTACK_MB, photos)
    if not keep:
        shutil.rmtree(tmp)
    print("wrote", out)


if __name__ == "__main__":
    main()
