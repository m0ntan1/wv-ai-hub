// Small SVG charts, drawn at the container's real width so the text stays readable on phones.
// Usage: put chartBox(spec) in the page, then call mountCharts(root) once the HTML is in place.
// spec = { type: 'line' | 'bar', title, fmt: 'usd' | 'usd2' | 'pct', xs: [labels], series: [{ label, color, v: [numbers or null] }],
//          zero: true (start the y-axis at 0), height, note, table: true }
// Follows the dataviz method: one axis, 2px lines, rounded bar ends, recessive grid, a legend for 2+ series
// plus direct end labels, a hover tooltip on every chart, and a table view.
import { esc } from './lib.js';

const MINUS = '−';
export function fmtVal(v, f) {
  if (v === null || v === undefined || !isFinite(v)) return 'n/a';
  const s = v < 0 ? MINUS : '', a = Math.abs(v);
  if (f === 'pct') return s + a.toFixed(2) + '%';
  if (f === 'usd2') return s + '$' + a.toFixed(2);
  if (a >= 1e12) return s + '$' + (a / 1e12).toFixed(2) + 'T';
  if (a >= 1e9) return s + '$' + (a / 1e9).toFixed(a >= 1e11 ? 0 : 1) + 'B';
  if (a >= 1e6) return s + '$' + (a / 1e6).toFixed(a >= 1e8 ? 0 : 1) + 'M';
  if (a >= 1e3) return s + '$' + (a / 1e3).toFixed(0) + 'K';
  return s + '$' + a.toFixed(0);
}
const short = (v, f) => fmtVal(v, f).replace(/\.0(?=[BMTK%])/, '');

export function chartBox(spec) {
  const multi = spec.series.length > 1;
  const legend = multi ? `<div class="viz-legend">${spec.series.map(s => `<span><i style="background:${s.color}"></i>${esc(s.label)}</span>`).join('')}</div>` : '';
  const table = spec.table === false ? '' : `<details class="viz-table"><summary>Show as a table</summary><div style="overflow-x:auto"><table><thead><tr><th>${esc(spec.xName || 'Period')}</th>${spec.series.map(s => `<th>${esc(s.label)}</th>`).join('')}</tr></thead>
    <tbody>${spec.xs.map((x, i) => `<tr><td>${esc(x)}</td>${spec.series.map(s => `<td>${fmtVal(s.v[i], spec.fmt)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></details>`;
  return `<figure class="viz-fig">${spec.title ? `<figcaption class="viz-title">${esc(spec.title)}</figcaption>` : ''}${legend}
    <div class="viz" data-viz="${esc(JSON.stringify(spec))}"><div class="viz-tip" hidden></div></div>
    ${spec.note ? `<p class="viz-note">${esc(spec.note)}</p>` : ''}${table}</figure>`;
}

function niceTicks(lo, hi, n = 4) {
  if (lo === hi) { hi = lo + 1; }
  const raw = (hi - lo) / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), r = raw / mag;
  const step = (r >= 5 ? 10 : r >= 2 ? 5 : r >= 1 ? 2 : 1) * mag;
  const t = []; for (let v = Math.floor(lo / step) * step; v <= hi + step * 0.001; v += step) t.push(+v.toFixed(10));
  if (t[0] > lo) t.unshift(t[0] - step);
  if (t[t.length - 1] < hi) t.push(t[t.length - 1] + step);
  return t;
}

function draw(el) {
  const spec = JSON.parse(el.dataset.viz);
  const W = Math.max(260, el.clientWidth), H = spec.height || 200;
  const multi = spec.series.length > 1;
  const all = spec.series.flatMap(s => s.v).filter(v => v !== null && isFinite(v));
  if (!all.length) { el.innerHTML = '<p class="empty">No data yet.</p>'; return; }
  let lo = Math.min(...all), hi = Math.max(...all);
  if (spec.zero || spec.type === 'bar') { lo = Math.min(0, lo); hi = Math.max(0, hi); }
  else { const pad = (hi - lo) * 0.12 || Math.abs(hi) * 0.1 || 1; lo -= pad; hi += pad; }
  const ticks = niceTicks(lo, hi, H < 150 ? 2 : 4);
  lo = ticks[0]; hi = ticks[ticks.length - 1];
  const labW = multi ? Math.min(118, 14 + Math.max(...spec.series.map(s => s.label.length)) * 6.6) : 10;
  const m = { l: 8 + Math.max(...ticks.map(t => short(t, spec.fmt).length)) * 6.4, r: labW, t: 10, b: 22 };
  const iw = W - m.l - m.r, ih = H - m.t - m.b, n = spec.xs.length;
  const band = iw / n;
  const X = i => spec.type === 'bar' ? m.l + band * (i + 0.5) : m.l + (n === 1 ? iw / 2 : (iw * i) / (n - 1));
  const Y = v => m.t + ih - ((v - lo) / (hi - lo)) * ih;
  const every = Math.max(1, Math.ceil(n / Math.max(2, Math.floor(iw / 58))));
  let svg = `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(spec.title || 'Chart')}">`;
  ticks.forEach(t => {
    svg += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(t)}" y2="${Y(t)}" class="${t === 0 ? 'viz-zero' : 'viz-grid'}"/>`;
    svg += `<text x="${m.l - 6}" y="${Y(t) + 3.5}" text-anchor="end" class="viz-axis">${esc(short(t, spec.fmt))}</text>`;
  });
  // X labels: first and last always; others only where they fit without touching a neighbor.
  const lw = t => String(t).length * 6.4 + 10;
  const span = i => { const w = lw(spec.xs[i]), anc = spec.type === 'bar' ? 'middle' : i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle';
    const x = X(i); return { anc, l: anc === 'start' ? x : anc === 'end' ? x - w : x - w / 2, r: anc === 'start' ? x + w : anc === 'end' ? x : x + w / 2 }; };
  const placed = [];
  const order = [0, n - 1, ...Array.from({ length: n }, (_, i) => i).filter(i => i && i !== n - 1 && i % every === 0)];
  order.forEach(i => { if (i < 0 || i >= n || placed.some(p => p.i === i)) return; const sp = span(i); if (placed.some(p => sp.l < p.r && sp.r > p.l)) return; placed.push({ i, ...sp }); });
  placed.forEach(p => { svg += `<text x="${X(p.i)}" y="${H - 6}" text-anchor="${p.anc}" class="viz-axis">${esc(spec.xs[p.i])}</text>`; });
  if (spec.type === 'bar') {
    const s = spec.series[0], bw = Math.max(4, Math.min(34, band - 2 - band * 0.28)), r = Math.min(4, bw / 2), z = Y(Math.max(lo, Math.min(0, hi)));
    s.v.forEach((v, i) => {
      if (v === null || !isFinite(v)) return;
      const x0 = X(i) - bw / 2, y = Y(v), h = Math.abs(z - y);
      if (h < 0.5) return;
      const rr = Math.min(r, h);
      const d = v >= 0
        ? `M${x0},${z}V${y + rr}Q${x0},${y} ${x0 + rr},${y}H${x0 + bw - rr}Q${x0 + bw},${y} ${x0 + bw},${y + rr}V${z}Z`
        : `M${x0},${z}V${y - rr}Q${x0},${y} ${x0 + rr},${y}H${x0 + bw - rr}Q${x0 + bw},${y} ${x0 + bw},${y - rr}V${z}Z`;
      svg += `<path d="${d}" style="fill:${(s.colors && s.colors[i]) || s.color}" class="viz-bar" data-i="${i}"/>`;
    });
  } else {
    spec.series.forEach(s => {
      let d = '', pen = false;
      s.v.forEach((v, i) => { if (v === null || !isFinite(v)) { pen = false; return; } d += (pen ? 'L' : 'M') + X(i).toFixed(1) + ',' + Y(v).toFixed(1); pen = true; });
      svg += `<path d="${d}" fill="none" style="stroke:${s.color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
    });
    // End markers and direct labels (pushed apart so they never overlap).
    const ends = spec.series.map(s => { let i = s.v.length - 1; while (i >= 0 && (s.v[i] === null || !isFinite(s.v[i]))) i--; return i < 0 ? null : { s, i, y: Y(s.v[i]) }; }).filter(Boolean);
    ends.forEach(e => { svg += `<circle cx="${X(e.i)}" cy="${e.y}" r="4" style="fill:${e.s.color}" class="viz-ring"/>`; });
    if (multi) {
      const lab = ends.map(e => ({ ...e, ly: e.y })).sort((a, b) => a.ly - b.ly);
      for (let k = 1; k < lab.length; k++) if (lab[k].ly - lab[k - 1].ly < 14) lab[k].ly = lab[k - 1].ly + 14;
      const over = lab.length ? lab[lab.length - 1].ly - (m.t + ih + 4) : 0;
      if (over > 0) lab.forEach(l => { l.ly -= over; });
      lab.forEach(l => { svg += `<text x="${X(l.i) + 9}" y="${l.ly + 3.5}" class="viz-label">${esc(l.s.label)}</text>`; });
    }
  }
  svg += `<line class="viz-cross" x1="0" x2="0" y1="${m.t}" y2="${m.t + ih}" visibility="hidden"/>`;
  svg += `<rect x="${m.l}" y="${m.t}" width="${iw}" height="${ih}" fill="transparent" class="viz-hit"/></svg>`;
  const tip = el.querySelector('.viz-tip');
  el.innerHTML = svg; el.appendChild(tip);
  const root = el.querySelector('svg'), cross = root.querySelector('.viz-cross');
  const show = i => {
    if (i < 0 || i >= n) return hide();
    const rows = spec.series.map(s => `<div><i style="background:${(s.colors && s.colors[i]) || s.color}"></i>${multi ? esc(s.label) + ' ' : ''}<b>${fmtVal(s.v[i], spec.fmt)}</b></div>`).join('');
    tip.innerHTML = `<div class="viz-tip-h">${esc(spec.tipX ? spec.tipX[i] : spec.xs[i])}</div>${rows}`;
    tip.hidden = false;
    const x = X(i), tw = tip.offsetWidth;
    tip.style.left = Math.max(0, Math.min(W - tw, x + (x > W / 2 ? -tw - 12 : 12))) + 'px';
    tip.style.top = m.t + 'px';
    if (spec.type !== 'bar') { cross.setAttribute('x1', x); cross.setAttribute('x2', x); cross.setAttribute('visibility', 'visible'); }
    root.querySelectorAll('.viz-bar').forEach(b => b.classList.toggle('dim', +b.dataset.i !== i));
  };
  const hide = () => { tip.hidden = true; cross.setAttribute('visibility', 'hidden'); root.querySelectorAll('.viz-bar').forEach(b => b.classList.remove('dim')); };
  const at = ev => {
    const r = root.getBoundingClientRect(), px = ev.clientX - r.left;
    return spec.type === 'bar' ? Math.floor((px - m.l) / band) : Math.round(((px - m.l) / iw) * (n - 1));
  };
  root.addEventListener('pointermove', ev => show(at(ev)));
  root.addEventListener('pointerdown', ev => show(at(ev)));
  root.addEventListener('pointerleave', hide);
}

let RO = null;
export function mountCharts(root) {
  const els = [...root.querySelectorAll('.viz')];
  els.forEach(draw);
  if (RO) RO.disconnect();
  if ('ResizeObserver' in window) {
    const seen = new WeakMap();
    RO = new ResizeObserver(entries => entries.forEach(e => {
      const w = Math.round(e.contentRect.width);
      if (seen.get(e.target) !== w) { const first = !seen.has(e.target); seen.set(e.target, w); if (!first) draw(e.target); }
    }));
    els.forEach(el => RO.observe(el));
  }
}
