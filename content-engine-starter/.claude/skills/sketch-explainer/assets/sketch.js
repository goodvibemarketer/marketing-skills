/* Sketch explainer: draws hand-made lines around real HTML text with rough.js.
   Markup it understands (all optional):
     .hl                      highlighter behind the words (marker colour)
     .ul / .ul2               wobbly underline / double underline (data-color="pen|ink|blue|marker")
     [data-box]               rough box around the element (data-box="pen" for the red pen, data-fill="hachure" to shade it)
     [data-circle]            rough circle around the element
     .num                     circled number
     .check                   ticked checkbox (data-checked="false" for an empty one)
     [data-brace=right|down]  curly brace to the right of / below the element
     [data-arrow="#id"]       arrow from this element to #id; "#a,#b,#c" fans out to several (data-color as above)
     .divider-v / .divider-h  hand-drawn rule through the element (data-dash for dashed)
     .axes                    two hand-drawn axis arrows on the element's left and bottom edges
     .matrix[data-lines]      outer box and centre cross for a 2x2 grid
     .icon[data-icon=name]    doodle icon (see ICONS)
     .page.frame              double hand-drawn border round the page
     .title, .punch, [data-tilt]  a slight random tilt, like real handwriting
   Set data-seed on .page to get the same wobble every render. */
(function () {
  const ICONS = {
    robot: "M25 35 h50 a6 6 0 0 1 6 6 v34 a6 6 0 0 1 -6 6 h-50 a6 6 0 0 1 -6 -6 v-34 a6 6 0 0 1 6 -6 z M50 35 v-12 M46 19 a4 4 0 1 0 8 0 a4 4 0 1 0 -8 0 M38 52 v6 M62 52 v6 M40 68 q10 6 20 0 M19 52 h-6 v12 h6 M81 52 h6 v12 h-6",
    bubble: "M15 22 h70 a8 8 0 0 1 8 8 v32 a8 8 0 0 1 -8 8 h-42 l-16 15 v-15 h-12 a8 8 0 0 1 -8 -8 v-32 a8 8 0 0 1 8 -8 z M33 46 a2.5 2.5 0 1 0 5 0 a2.5 2.5 0 1 0 -5 0 M48 46 a2.5 2.5 0 1 0 5 0 a2.5 2.5 0 1 0 -5 0 M63 46 a2.5 2.5 0 1 0 5 0 a2.5 2.5 0 1 0 -5 0",
    box: "M18 36 L50 22 L82 36 L82 72 L50 86 L18 72 Z M18 36 L50 50 L82 36 M50 50 V86 M30 58 h12",
    bars: "M12 86 H90 M22 86 V62 h13 V86 M43 86 V44 h13 V86 M64 86 V24 h13 V86",
    trend: "M10 82 L34 56 L50 68 L84 28 M68 28 H84 V44",
    doc: "M24 10 H60 L76 26 V86 H24 Z M60 10 V26 H76 M33 38 H67 M33 50 H67 M33 62 H50 M58 76 a14 14 0 1 0 28 0 a14 14 0 1 0 -28 0 M65 76 l5 5 l9 -10",
    bulb: "M50 10 a24 24 0 0 1 14 44 v12 h-28 v-12 a24 24 0 0 1 14 -44 z M38 74 h24 M41 82 h18 M46 90 h8",
    target: "M16 54 a34 34 0 1 0 68 0 a34 34 0 1 0 -68 0 M30 54 a20 20 0 1 0 40 0 a20 20 0 1 0 -40 0 M44 54 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0 M50 54 L84 16 M74 16 H84 V26",
    person: "M37 24 a13 13 0 1 0 26 0 a13 13 0 1 0 -26 0 M20 88 q0 -34 30 -34 q30 0 30 34",
    people: "M18 30 a11 11 0 1 0 22 0 a11 11 0 1 0 -22 0 M6 86 q0 -30 23 -30 q23 0 23 30 M60 30 a11 11 0 1 0 22 0 a11 11 0 1 0 -22 0 M48 86 q0 -30 23 -30 q23 0 23 30",
    clock: "M16 50 a34 34 0 1 0 68 0 a34 34 0 1 0 -68 0 M50 50 V26 M50 50 L66 60",
    magnet: "M22 18 v36 a28 28 0 0 0 56 0 v-36 h-16 v36 a12 12 0 0 1 -24 0 v-36 z M22 32 h16 M62 32 h16",
    warning: "M50 10 L90 84 H10 Z M50 36 V60 M50 70 v3",
    coin: "M16 50 a34 34 0 1 0 68 0 a34 34 0 1 0 -68 0 M50 28 v44 M60 38 q-10 -8 -20 0 q-5 8 10 12 q14 4 10 13 q-10 8 -21 0",
    gear: "M34 50 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0 M50 12 v12 M50 76 v12 M12 50 h12 M76 50 h12 M23 23 l9 9 M68 68 l9 9 M77 23 l-9 9 M23 77 l9 -9 M24 50 a26 26 0 1 0 52 0 a26 26 0 1 0 -52 0",
    mail: "M10 24 H90 V78 H10 Z M10 24 L50 56 L90 24",
    calendar: "M14 20 H86 V88 H14 Z M14 38 H86 M32 10 V28 M68 10 V28 M28 54 h10 M46 54 h10 M64 54 h10 M28 72 h10 M46 72 h10",
    search: "M18 42 a24 24 0 1 0 48 0 a24 24 0 1 0 -48 0 M60 60 L88 88",
    pencil: "M18 82 L26 62 L68 20 L80 32 L38 74 Z M60 28 L72 40 M18 82 L34 76",
    bolt: "M58 8 L24 56 H48 L40 92 L78 40 H54 Z",
    heart: "M50 84 C20 62 12 46 22 32 C32 20 46 24 50 36 C54 24 68 20 78 32 C88 46 80 62 50 84 Z",
    tick: "M16 52 L40 76 L86 24",
    cross: "M22 22 L78 78 M78 22 L22 78",
    funnel: "M10 16 H90 L58 54 V82 L42 90 V54 Z",
    layers: "M50 12 L90 32 L50 52 L10 32 Z M10 50 L50 70 L90 50 M10 68 L50 88 L90 68",
    cycle: "M80 50 a30 30 0 1 1 -9 -21 M72 14 V30 H56",
    star: "M50 10 L61 38 L90 40 L67 58 L75 88 L50 71 L25 88 L33 58 L10 40 L39 38 Z",
    flag: "M22 92 V10 M22 12 H78 L66 30 L78 48 H22",
    money: "M10 28 H90 V72 H10 Z M38 50 a12 12 0 1 0 24 0 a12 12 0 1 0 -24 0 M20 38 v24 M80 38 v24",
    chat: "M12 16 H66 V54 H34 L20 66 V54 H12 Z M40 62 V74 H70 L84 86 V74 H90 V36 H74",
    key: "M14 50 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0 M46 50 H88 M76 50 V64 M64 50 V60",
    lock: "M22 46 H78 V88 H22 Z M34 46 V32 a16 16 0 0 1 32 0 V46 M50 62 V72",
    globe: "M14 50 a36 36 0 1 0 72 0 a36 36 0 1 0 -72 0 M14 50 H86 M50 14 C30 34 30 66 50 86 M50 14 C70 34 70 66 50 86",
    rocket: "M50 8 C66 22 70 44 64 66 H36 C30 44 34 22 50 8 Z M44 36 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0 M36 56 L22 72 L36 70 M64 56 L78 72 L64 70 M44 74 L50 90 L56 74"
  };

  const page = document.querySelector('.page');
  const css = getComputedStyle(document.documentElement);
  const C = { ink: css.getPropertyValue('--ink').trim(), soft: css.getPropertyValue('--ink-soft').trim(),
              pen: css.getPropertyValue('--pen').trim(), marker: css.getPropertyValue('--marker').trim(), blue: '#2f5fb3' };
  const col = (el, d) => C[(el.dataset.color || d)] || el.dataset.color || C[d];
  let seed = +(page.dataset.seed || 7);
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const nextSeed = () => Math.floor(rnd() * 1e6) + 1;

  // 1. tilt first, so everything else measures the tilted text
  page.querySelectorAll('.title, .punch, [data-tilt]').forEach(el => {
    const max = el.dataset.tilt ? +el.dataset.tilt : 0.8;
    el.style.transform = `rotate(${((rnd() * 2 - 1) * max).toFixed(2)}deg)`;
  });
  if (page.dataset.sig !== 'off' && page.dataset.sigText && !page.querySelector('.sig')) {
    const s = document.createElement('div'); s.className = 'sig'; s.textContent = page.dataset.sigText;
    page.appendChild(s);
  }

  const P = page.getBoundingClientRect();
  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', P.width); svg.setAttribute('height', P.height);
  svg.style.cssText = 'position:absolute;left:0;top:0;z-index:0;pointer-events:none;overflow:visible';
  page.insertBefore(svg, page.firstChild);
  const rc = rough.svg(svg);
  const add = (node, extra) => { if (extra) Object.assign(node.style, extra); svg.appendChild(node); return node; };
  const base = o => Object.assign({ roughness: 1.3, bowing: 1.1, strokeWidth: 2.8, stroke: C.ink, seed: nextSeed() }, o);
  const box = el => { const r = el.getBoundingClientRect(); return { x: r.left - P.left, y: r.top - P.top, w: r.width, h: r.height }; };
  const lines = el => [...el.getClientRects()].map(r => ({ x: r.left - P.left, y: r.top - P.top, w: r.width, h: r.height }));
  const arrowHead = (x, y, ang, color, size = 16) => {
    const a1 = ang + Math.PI * 0.82, a2 = ang - Math.PI * 0.82;
    add(rc.linearPath([[x + Math.cos(a1) * size, y + Math.sin(a1) * size], [x, y], [x + Math.cos(a2) * size, y + Math.sin(a2) * size]], base({ stroke: color, roughness: 0.9 })));
  };

  // 2. highlighter: two thick, slightly crooked marker strokes behind the lower two-thirds of the words
  page.querySelectorAll('.hl').forEach(el => lines(el).forEach(r => {
    const th = r.h * 0.6, ym = r.y + r.h * 0.62, j = () => (rnd() - 0.5) * 5;
    for (let k = 0; k < 2; k++) {
      const g = add(rc.line(r.x - 6 + j(), ym + j(), r.x + r.w + 6 + j(), ym - 2 + j(),
        base({ stroke: col(el, 'marker'), strokeWidth: th * (k ? 0.7 : 1), roughness: 1.6, bowing: 0.6 })), { opacity: k ? 0.35 : 0.5, mixBlendMode: 'multiply' });
      g.querySelectorAll('path').forEach(q => q.setAttribute('stroke-linecap', 'butt'));
    }
  }));

  // 3. underlines
  page.querySelectorAll('.ul, .ul2').forEach(el => lines(el).forEach(r => {
    const c = col(el, 'pen'), y = r.y + r.h * 0.98;
    const pts = n => Array.from({ length: n }, (_, i) => [r.x - 6 + (r.w + 12) * i / (n - 1), y + (rnd() - 0.5) * 5]);
    add(rc.curve(pts(5), base({ stroke: c, strokeWidth: 3.4, roughness: 0.8 })));
    if (el.classList.contains('ul2')) add(rc.curve(pts(4).map(([x, yy]) => [x + 10, yy + 9]), base({ stroke: c, strokeWidth: 2.6, roughness: 0.8 })));
  }));

  // 4. boxes and circles
  page.querySelectorAll('[data-box]').forEach(el => {
    const b = box(el), p = +(el.dataset.pad || 0), c = col(el, el.dataset.box || 'ink');
    if (el.dataset.fill === 'hachure')   // light pen shading first, then the outline on top
      add(rc.rectangle(b.x - p, b.y - p, b.w + 2 * p, b.h + 2 * p, base({ stroke: 'none', fill: c, fillStyle: 'hachure', hachureGap: 12, fillWeight: 1.4, hachureAngle: -40 })), { opacity: 0.3 });
    add(rc.rectangle(b.x - p, b.y - p, b.w + 2 * p, b.h + 2 * p, base({ stroke: c, strokeWidth: el.dataset.box === 'pen' ? 4 : 2.8 })));
  });
  page.querySelectorAll('[data-circle], .num').forEach(el => {
    const b = box(el), p = +(el.dataset.pad || 8);
    add(rc.ellipse(b.x + b.w / 2, b.y + b.h / 2, b.w + 2 * p, b.h + 2 * p, base({ stroke: col(el, el.dataset.circle || 'ink'), roughness: 1.1 })));
  });
  page.querySelectorAll('.check').forEach(el => {
    const b = box(el), c = col(el, 'pen');
    add(rc.rectangle(b.x, b.y, b.w, b.h, base({ stroke: c, strokeWidth: 3 })));
    if (el.dataset.checked !== 'false') add(rc.linearPath([[b.x + b.w * 0.18, b.y + b.h * 0.5], [b.x + b.w * 0.42, b.y + b.h * 0.8], [b.x + b.w * 0.95, b.y - b.h * 0.12]], base({ stroke: c, strokeWidth: 3.6, roughness: 0.9 })));
  });

  // 5. braces
  page.querySelectorAll('[data-brace]').forEach(el => {
    const b = box(el), c = col(el, 'ink'), d = 18;
    if (el.dataset.brace === 'down') {
      const y = b.y + b.h + 8, x0 = b.x, x1 = b.x + b.w, m = (x0 + x1) / 2;
      add(rc.path(`M${x0} ${y} q0 ${d} ${d} ${d} H${m - d} q${d} 0 ${d} ${d} q0 ${-d} ${d} ${-d} H${x1 - d} q${d} 0 ${d} ${-d}`, base({ stroke: c })));
    } else {
      const x = b.x + b.w + 10, y0 = b.y, y1 = b.y + b.h, m = (y0 + y1) / 2;
      add(rc.path(`M${x} ${y0} q${d} 0 ${d} ${d} V${m - d} q0 ${d} ${d} ${d} q${-d} 0 ${-d} ${d} V${y1 - d} q0 ${d} ${-d} ${d}`, base({ stroke: c })));
    }
  });

  // 6. arrows between elements
  page.querySelectorAll('[data-arrow]').forEach(el => el.dataset.arrow.split(',').forEach(sel => {
    const t = page.querySelector(sel.trim()); if (!t) { console.warn('arrow target not found: ' + sel); return; }
    const a = box(el), b = box(t), c = col(el, 'ink');
    const ac = [a.x + a.w / 2, a.y + a.h / 2], bc = [b.x + b.w / 2, b.y + b.h / 2];
    const edge = (r, from, to) => { const dx = to[0] - from[0], dy = to[1] - from[1];
      const s = Math.min(Math.abs((r.w / 2 + 10) / (dx || 1e-6)), Math.abs((r.h / 2 + 10) / (dy || 1e-6))); return [from[0] + dx * s, from[1] + dy * s]; };
    const s = edge(a, ac, bc), e = edge(b, bc, ac), bend = (rnd() - 0.5) * 30;
    const mid = [(s[0] + e[0]) / 2 - (e[1] - s[1]) * 0.08 + bend * 0.2, (s[1] + e[1]) / 2 + (e[0] - s[0]) * 0.08];
    add(rc.curve([s, mid, e], base({ stroke: c, roughness: 0.9 })));
    arrowHead(e[0], e[1], Math.atan2(e[1] - mid[1], e[0] - mid[0]), c);
  }));

  // 7. dividers, axes, matrix lines, page frame
  const rule = (x0, y0, x1, y1, c, dash) => {
    if (!dash) return add(rc.line(x0, y0, x1, y1, base({ stroke: c })));
    const n = Math.max(2, Math.round(Math.hypot(x1 - x0, y1 - y0) / 26));
    for (let i = 0; i < n; i++) { const t0 = i / n, t1 = (i + 0.55) / n;
      add(rc.line(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0, x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1, base({ stroke: c, roughness: 0.6 }))); }
  };
  page.querySelectorAll('.divider-v').forEach(el => { const b = box(el); rule(b.x + b.w / 2, b.y, b.x + b.w / 2, b.y + b.h, col(el, 'ink'), el.hasAttribute('data-dash')); });
  page.querySelectorAll('.divider-h').forEach(el => { const b = box(el); rule(b.x, b.y + b.h / 2, b.x + b.w, b.y + b.h / 2, col(el, 'ink'), el.hasAttribute('data-dash')); });
  page.querySelectorAll('.axes').forEach(el => {
    const b = box(el), c = col(el, 'ink'), o = 22;
    add(rc.line(b.x - o, b.y + b.h + o, b.x - o, b.y - 10, base({ stroke: c }))); arrowHead(b.x - o, b.y - 10, -Math.PI / 2, c);
    add(rc.line(b.x - o, b.y + b.h + o, b.x + b.w + 10, b.y + b.h + o, base({ stroke: c }))); arrowHead(b.x + b.w + 10, b.y + b.h + o, 0, c);
  });
  page.querySelectorAll('.matrix[data-lines]').forEach(el => {
    const b = box(el);
    add(rc.rectangle(b.x, b.y, b.w, b.h, base({})));
    add(rc.line(b.x + b.w / 2, b.y, b.x + b.w / 2, b.y + b.h, base({})));
    add(rc.line(b.x, b.y + b.h / 2, b.x + b.w, b.y + b.h / 2, base({})));
  });
  if (page.classList.contains('frame')) {
    add(rc.rectangle(22, 22, P.width - 44, P.height - 44, base({ strokeWidth: 3.2, roughness: 1 })));
    add(rc.rectangle(32, 32, P.width - 64, P.height - 64, base({ strokeWidth: 1.6, roughness: 1.2 })));
  }

  // 8. doodle icons
  page.querySelectorAll('.icon[data-icon]').forEach(el => {
    const d = ICONS[el.dataset.icon]; if (!d) { console.warn('unknown icon ' + el.dataset.icon); return; }
    const b = box(el), s = Math.min(b.w, b.h) / 100;
    const g = add(rc.path(d, base({ stroke: col(el, 'ink'), strokeWidth: 2.6 / Math.max(s, 0.4), roughness: 0.9 })));
    g.setAttribute('transform', `translate(${b.x + (b.w - 100 * s) / 2} ${b.y + (b.h - 100 * s) / 2}) scale(${s})`);
  });

  window.__icons = Object.keys(ICONS);
  window.__sketchDone = true;
})();
