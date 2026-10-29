/* Notebook notes: the notebook-only drawing. Runs before ../sketch-explainer/assets/sketch.js,
   which then adds highlights, underlines, boxes, circles, arrows, braces and icons.
     .page.spiral              spiral binding holes and rings down the left edge
     .page.gutter              shadow of the notebook's centre fold on the left
     .blob                     neon highlighter blob behind a word (data-blob="outline" adds an ink ring)
     .pyramid > .layer         layered pyramid; each layer data-fill="yellow|green|pink|blue|orange|marker|pen" */
(function () {
  const FILLS = { yellow: '#f2ef3d', green: '#7fd06a', pink: '#f2569a', blue: '#3f8fd0', orange: '#ffb35c' };
  const page = document.querySelector('.page');
  const css = getComputedStyle(document.documentElement);
  const v = n => css.getPropertyValue(n).trim();
  const fillOf = k => FILLS[k] || (k === 'marker' ? v('--marker') : k === 'pen' ? v('--pen') : k) || v('--marker');
  let seed = +(page.dataset.seed || 7) * 31 + 5;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const nextSeed = () => Math.floor(rnd() * 1e6) + 1;
  const NS = 'http://www.w3.org/2000/svg';
  const P = page.getBoundingClientRect();
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', P.width); svg.setAttribute('height', P.height);
  svg.style.cssText = 'position:absolute;left:0;top:0;z-index:0;pointer-events:none;overflow:visible';
  page.insertBefore(svg, page.firstChild);
  const rc = rough.svg(svg);
  const add = (n, st) => { if (st) Object.assign(n.style, st); svg.appendChild(n); return n; };
  const base = o => Object.assign({ roughness: 1.2, bowing: 1, strokeWidth: 2.6, stroke: v('--ink'), seed: nextSeed() }, o);
  const box = el => { const r = el.getBoundingClientRect(); return { x: r.left - P.left, y: r.top - P.top, w: r.width, h: r.height }; };

  // binding
  if (page.classList.contains('spiral')) {
    const step = 54, n = Math.floor((P.height - 40) / step);
    for (let i = 0; i < n; i++) {
      const y = 34 + i * step;
      const hole = document.createElementNS(NS, 'ellipse');
      Object.entries({ cx: 40, cy: y, rx: 9, ry: 8, fill: '#2b2b2e' }).forEach(([k, val]) => hole.setAttribute(k, val));
      add(hole, { opacity: 0.85 });
      add(rc.path(`M40 ${y} C 20 ${y - 6}, 4 ${y - 14}, -6 ${y - 20}`, base({ stroke: '#3a3a3f', strokeWidth: 5, roughness: 0.4 })));
    }
  }
  if (page.classList.contains('gutter')) {
    const g = document.createElement('div'); g.className = 'gutter-shade';
    g.style.cssText = 'position:absolute;left:0;top:0;bottom:0;width:70px;z-index:0;background:linear-gradient(to right,rgba(0,0,0,.22),rgba(0,0,0,.05) 55%,transparent)';
    page.appendChild(g);
  }

  // highlighter blobs
  page.querySelectorAll('.blob').forEach(el => {
    const b = box(el), px = 26, py = 12;
    add(rc.ellipse(b.x + b.w / 2, b.y + b.h / 2, b.w + 2 * px, b.h + 2 * py,
      base({ stroke: 'none', fill: fillOf(el.dataset.fill || 'marker'), fillStyle: 'solid', roughness: 1.6 })), { opacity: 0.9, mixBlendMode: 'multiply' });
    if (el.dataset.blob === 'outline') add(rc.ellipse(b.x + b.w / 2, b.y + b.h / 2, b.w + 2 * px + 4, b.h + 2 * py + 4, base({ roughness: 1 })));
  });

  // pyramids: equal bands from apex to base; layers listed top first
  page.querySelectorAll('.pyramid').forEach(el => {
    const b = box(el), layers = [...el.querySelectorAll(':scope > .layer')], n = layers.length;
    const ax = b.x + b.w / 2, top = b.y, bot = b.y + b.h, half = b.w / 2;
    const xAt = y => half * (y - top) / (bot - top);
    layers.forEach((L, i) => {
      const y0 = top + (bot - top) * i / n, y1 = top + (bot - top) * (i + 1) / n;
      const pts = i === 0 ? [[ax, y0], [ax + xAt(y1), y1], [ax - xAt(y1), y1]]
        : [[ax - xAt(y0), y0], [ax + xAt(y0), y0], [ax + xAt(y1), y1], [ax - xAt(y1), y1]];
      add(rc.polygon(pts, base({ stroke: 'none', fill: fillOf(L.dataset.fill || 'marker'), fillStyle: 'solid', roughness: 1.4 })), { opacity: 0.82, mixBlendMode: 'multiply' });
      add(rc.polygon(pts, base({ stroke: 'none', fill: fillOf(L.dataset.fill || 'marker'), fillStyle: 'zigzag', hachureGap: 7, fillWeight: 2, roughness: 2 })), { opacity: 0.25 });
      add(rc.polygon(pts, base({ strokeWidth: 3 })));
      const w = 2 * xAt((y0 + y1) / 2) * 0.86;
      Object.assign(L.style, { left: (ax - b.x - w / 2) + 'px', width: w + 'px', top: (y0 - b.y) + 'px', height: (y1 - y0) + 'px',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: i === 0 ? 'flex-end' : 'center', paddingBottom: i === 0 ? '10px' : '0' });
    });
  });
  window.__notebookDone = true;
})();
