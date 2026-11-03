// SVG map of West Virginia: counties, border, projects, lines, upcoming dates, and the time slider.
import { D } from './data.js';
import { esc, toDate, ymd, fmtDate, STATUS, statusColor } from './lib.js';

const NS = 'http://www.w3.org/2000/svg';
const W = 1000;
let PROJ = null; // cached projection

function projection() {
  if (PROJ) return PROJ;
  let minX = 180, maxX = -180, minY = 90, maxY = -90;
  D.geo.border.forEach(seg => seg.forEach(([x, y]) => { minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }));
  const kx = Math.cos(((minY + maxY) / 2) * Math.PI / 180);
  const pad = 14, S = (W - pad * 2) / ((maxX - minX) * kx);
  const H = Math.ceil((maxY - minY) * S + pad * 2);
  const p = ([lng, lat]) => [+(pad + (lng - minX) * kx * S).toFixed(1), +(pad + (maxY - lat) * S).toFixed(1)];
  PROJ = { p, H };
  return PROJ;
}
const ringPath = ring => { const { p } = projection(); return 'M' + ring.map(pt => p(pt).join(',')).join('L') + 'Z'; };

// Label placement (direction and offset in label-size units), tuned to keep the clusters readable.
const LBL = {
  monarch: [1.1, .5, 'start'], tamarack: [1.1, -.55, 'start'], google: [1.1, .45, 'start'], 'adams-h': [1.1, -.2, 'start'], 'adams-tg': [1.1, .55, 'start'],
  penzance: [-1.1, .1, 'end'], qts: [-1.1, .45, 'end'], summit: [-1.1, .75, 'end'], hoglick: [-1.1, .4, 'end'], ridgeline: [.9, -1, 'start'],
  warwood: [1.1, .4, 'start'], monroe: [1.1, .4, 'start'], fortmartin: [-1, -.8, 'end'],
};
const SHORT = { 'adams-tg': 'Adams Fork · Twisted Gun', 'adams-h': 'Adams Fork · Harless', monroe: 'Monroe Co. (rumored)' };

/** First date a project is on the record, and its status on a given date. */
const firstDate = p => p.history[0].d;
function statusOn(p, day) {
  let st = null;
  for (const h of p.history) if (ymd(toDate(h.d)) <= day) st = h.status;
  return st;
}

/** Milestones for the slider caption: everything dated, past and scheduled. */
function milestones() {
  const m = [];
  D.projects.forEach(p => {
    p.history.forEach(h => m.push({ d: h.d, t: `${p.short}: ${h.t}.`, pid: p.id }));
    p.timeline.forEach(t => { if (t.d && t.d.length >= 7 && ['certified', 'court', 'violation', 'hearing', 'protest', 'redaction'].includes(t.kind)) m.push({ d: t.d, t: `${p.short}: ${t.t}`, pid: p.id }); });
  });
  D.lines.forEach(l => m.push({ d: l.appears, t: l.appears_note, pid: l.id }));
  D.desk.forEach(x => m.push({ d: x.d, t: x.t, pid: x.project }));
  D.docket.forEach(k => { if (k.next && k.next.d && k.next.d.length >= 7) m.push({ d: k.next.d, t: `Scheduled: ${k.next.t} (${k.title.split(':')[0]}).`, future: true, verify: k.next.verify }); });
  m.push({ d: '2025-04-30', t: 'Gov. Patrick Morrisey signs HB 2014, the Power Generation and Consumption Act. Certified data centers can now skip county zoning.' });
  const seen = new Set();
  return m.filter(x => { const k = x.d + x.t; if (seen.has(k)) return false; seen.add(k); return true; })
    .map(x => ({ ...x, day: ymd(toDate(x.d)) })).sort((a, b) => a.day < b.day ? -1 : 1);
}

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

/**
 * Mount a map.
 * opts.mode: 'front' | 'full' | 'locator' | 'counties'
 * opts.focus: project id to highlight (locator); opts.county: county name to highlight
 * opts.scrubber: show the time slider; opts.autoplay: play once per session
 */
export function mountMap(host, opts = {}) {
  const mode = opts.mode || 'front';
  const { p, H } = projection();
  const state = { day: D.today, layers: new Set(opts.layers || ['projects', 'lines', 'dates']), raf: 0, playing: false };
  const M = milestones();
  const START = '2025-01-01', END = (() => { const e = toDate(D.today); e.setDate(e.getDate() + 150); const f = ymd(e); return f > '2027-04-01' ? f : '2027-04-01'; })();
  const span = (toDate(END) - toDate(START)) / 86400000;
  const dayAt = v => { const d = toDate(START); d.setDate(d.getDate() + Math.round(v)); return ymd(d); };
  const valOf = day => (toDate(day) - toDate(START)) / 86400000;

  host.classList.add('mapcard');
  host.innerHTML = `
    ${opts.layerPills ? `<div class="map-top" role="group" aria-label="Map layers">
      ${[['projects', 'Projects'], ['lines', 'Transmission lines'], ['dates', 'Upcoming dates'], ['names', 'County names']].map(([k, l]) => `<button type="button" class="pill" data-layer="${k}" aria-pressed="${state.layers.has(k)}">${l}</button>`).join('')}
    </div>` : ''}
    <svg class="map-svg" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(opts.label || 'Map of West Virginia data center and power projects')}"></svg>
    <div class="map-tip" hidden></div>
    ${opts.scrubber ? `<div class="scrub">
      <div class="scrub-row">
        <button type="button" class="play" aria-label="Play the timeline">▶</button>
        <div class="track">
          <div class="base"></div><div class="fill"></div>
          <input type="range" min="0" max="${span}" step="1" value="${valOf(D.today)}" aria-label="Map date">
          <div class="handle"></div>
        </div>
      </div>
      <div class="scrub-cap" aria-live="polite"></div>
    </div>` : ''}
    ${opts.note ? `<p class="map-note">${opts.note}</p>` : ''}`;
  const svg = host.querySelector('svg'), tip = host.querySelector('.map-tip');

  // ---- static layers
  const gC = el('g', { class: 'g-counties' }, svg);
  const active = new Set(D.counties.map(c => c.name));
  const focusCounties = new Set(opts.focus ? (D.byId[opts.focus]?.counties || []) : opts.county ? [opts.county] : []);
  D.geo.counties.forEach(c => {
    const isLink = active.has(c.name) && mode !== 'locator';
    const cls = ['county', isLink ? 'link' : '', focusCounties.has(c.name) ? 'sel' : '', mode === 'counties' && active.has(c.name) ? 'hot' : ''].filter(Boolean).join(' ');
    const path = el('path', { d: c.rings.map(ringPath).join(''), class: cls, 'data-county': c.name }, gC);
    if (isLink) { path.setAttribute('tabindex', '-1'); el('title', {}, path).textContent = c.name + ' County: open the county sheet'; }
  });
  el('path', { class: 'border', d: D.geo.border.map(([a, b]) => 'M' + p(a).join(',') + 'L' + p(b).join(',')).join('') }, svg);
  const gNames = el('g', { class: 'g-names' }, svg);
  const gLines = el('g', { class: 'g-lines' }, svg);
  const gDates = el('g', { class: 'g-dates' }, svg);
  const gPts = el('g', { class: 'g-pts' }, svg);

  function fs() { const w = svg.getBoundingClientRect().width || W; return Math.max(10, Math.min(30, 13.5 * W / w)); }

  function draw() {
    const f = fs(), day = state.day;
    // county names
    gNames.innerHTML = '';
    if (state.layers.has('names')) {
      D.geo.counties.forEach(c => {
        const [x, y] = p(c.label);
        const t = el('text', { x, y: y + f * .3, class: 'clbl', 'font-size': (f * .72).toFixed(1) }, gNames);
        t.textContent = c.name;
        if (focusCounties.has(c.name)) t.setAttribute('style', 'fill:var(--fg);font-weight:700');
      });
    }
    // lines
    gLines.innerHTML = '';
    if (state.layers.has('lines') && mode !== 'locator') {
      D.lines.forEach(l => {
        if (ymd(toDate(l.appears)) > day) return;
        const pts = l.pts.map(pt => p(pt).join(',')).join(' ');
        el('polyline', { points: pts, fill: 'none', stroke: 'var(--grid)', 'stroke-width': Math.max(2.5, f * .22), 'stroke-opacity': .9, 'stroke-dasharray': l.id === 'valleylink' ? `${f * .55} ${f * .45}` : null, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, gLines);
        const mid = l.pts[Math.floor(l.pts.length / 2) - (l.id === 'marl' ? 1 : 2)];
        const [x, y] = p(mid);
        const t = el('text', { x: x + (l.id === 'marl' ? f * .2 : -f * 6), y: y + (l.id === 'marl' ? -f * .9 : f * 2.6), class: 'lbl', 'font-size': (f * .78).toFixed(1), 'stroke-width': f * .3, style: 'fill:var(--grid);font-family:var(--mono)' }, gLines);
        t.textContent = l.short + (l.id === 'valleylink' ? ' (pre-filing)' : '');
      });
    }
    // upcoming dates by county
    gDates.innerHTML = '';
    if (state.layers.has('dates') && mode !== 'locator') {
      const win = [day, (() => { const d = toDate(day); d.setDate(d.getDate() + (day === D.today ? 30 : 7)); return ymd(d); })()];
      const counts = {};
      D.events.forEach(e => { if (e.date && !e.tbd && e.county && e.county !== 'Statewide' && e.date >= win[0] && e.date <= win[1]) counts[e.county] = (counts[e.county] || 0) + 1; });
      D.geo.counties.forEach(c => {
        const n = counts[c.name]; if (!n) return;
        const [x, y] = p(c.label);
        const g = el('g', { transform: `translate(${x},${y})`, 'data-cal': c.name }, gDates);
        el('circle', { r: f * .46, class: 'ev-ring' }, g);
        el('circle', { r: f * .46, class: 'evdot' }, g);
        const t = el('text', { y: f * .25, 'text-anchor': 'middle', 'font-size': (f * .7).toFixed(1), style: 'fill:#000;font-family:var(--mono);font-weight:700' }, g);
        t.textContent = n;
        el('title', {}, g).textContent = `${n} public date${n > 1 ? 's' : ''} in ${c.name} County in the next ${day === D.today ? 30 : 7} days`;
      });
    }
    // projects
    gPts.innerHTML = '';
    if (state.layers.has('projects')) {
      D.projects.forEach(pr => {
        const st = statusOn(pr, day);
        if (!st) return;
        if (mode === 'locator' && pr.id !== opts.focus) return;
        const [x, y] = p([pr.lng, pr.lat]), c = statusColor(st), r = f * .55;
        const g = el('g', { class: 'pt', tabindex: mode === 'locator' ? null : 0, role: 'link', 'aria-label': `${pr.name}, ${STATUS[st].label}, ${pr.place}`, 'data-id': pr.id }, gPts);
        if (st === 'construction') el('circle', { cx: x, cy: y, r, fill: 'none', stroke: c, 'stroke-width': 2, class: 'pulse' }, g);
        if (st === 'grid') el('rect', { x: x - r * .85, y: y - r * .85, width: r * 1.7, height: r * 1.7, fill: c, class: 'mk', stroke: 'var(--map-land)', 'stroke-width': 2, transform: `rotate(45 ${x} ${y})` }, g);
        else if (st === 'rumored') el('circle', { cx: x, cy: y, r: r * .8, fill: 'var(--map-land)', class: 'mk', stroke: c, 'stroke-width': 2, 'stroke-dasharray': '3 3' }, g);
        else el('circle', { cx: x, cy: y, r, fill: c, class: 'mk', stroke: 'var(--map-land)', 'stroke-width': 2.5 }, g);
        el('circle', { cx: x, cy: y, r: r * 2.2, fill: 'transparent' }, g); // bigger hit area
        if (mode === 'locator') return;
        const [dx, dy, an] = LBL[pr.id] || [1.1, .4, 'start'];
        const t = el('text', { x: x + dx * f, y: y + dy * f + f * .1, 'text-anchor': an, class: 'lbl', 'font-size': f.toFixed(1), 'stroke-width': f * .32 }, g);
        t.textContent = SHORT[pr.id] || pr.short;
        if (pr.verify) { const v = el('text', { x: x + dx * f, y: y + dy * f + f * 1.05, 'text-anchor': an, class: 'lbl', 'font-size': (f * .66).toFixed(1), 'stroke-width': f * .25, style: 'fill:var(--signal);font-family:var(--mono)' }, g); v.textContent = '⚠ VERIFY'; }
      });
    }
  }

  // ---- slider
  function caption(day) {
    const cap = host.querySelector('.scrub-cap'); if (!cap) return;
    let best = null;
    for (const m of M) if (m.day <= day) best = m;
    const ahead = day > D.today ? M.find(m => m.day >= day) || M.filter(m => m.day > D.today).pop() : null;
    const it = ahead || best;
    const label = day === D.today ? 'Today · ' + fmtDate(day) : fmtDate(day);
    const visible = D.projects.filter(pr => statusOn(pr, day)).length;
    cap.innerHTML = it ? `<b>${esc(label)}</b><span>${visible} on the map. ${ahead ? '' : '<span class="dim">Latest:</span> '}${esc(it.t)}${it.verify ? ' <span class="vfy">⚠ Verify</span>' : ''}</span>` : `<b>${esc(label)}</b><span>Nothing on the record yet.</span>`;
  }
  function setDay(day, fromUser) {
    state.day = day;
    const inp = host.querySelector('input[type=range]');
    if (inp) {
      const v = valOf(day); if (!fromUser) inp.value = v;
      host.querySelector('.fill').style.width = (v / span * 100) + '%';
      host.querySelector('.handle').style.left = (v / span * 100) + '%';
      inp.setAttribute('aria-valuetext', fmtDate(day));
    }
    draw(); caption(day);
  }
  if (opts.scrubber) {
    const track = host.querySelector('.track');
    const ticks = [['2025-04-30', 'HB 2014 LAW', 'first'], ['2026-02-01', 'FEB 2026 · PENZANCE'], ['2026-09-03', 'SEP 3 · MASON CERTS'], [D.today, 'TODAY', 'today'], ['2027-03-06', 'MAR 6 · MARL', 'lastlbl']];
    ticks.forEach(([d, l, cls]) => {
      if (d > END) return;
      const k = document.createElement('div');
      k.className = 'tick' + (d > D.today ? ' future' : '') + (cls ? ' ' + cls : '');
      k.style.left = (valOf(d) / span * 100) + '%';
      k.innerHTML = `<span>${l}</span>`;
      track.insertBefore(k, track.querySelector('input'));
    });
    const inp = host.querySelector('input[type=range]');
    inp.addEventListener('input', () => { stop(); setDay(dayAt(+inp.value), true); });
    const btn = host.querySelector('.play');
    btn.addEventListener('click', () => state.playing ? stop() : play(state.day >= D.today ? START : state.day));
  }
  function play(from) {
    stop(); state.playing = true;
    const btn = host.querySelector('.play'); if (btn) { btn.textContent = '❚❚'; btn.setAttribute('aria-label', 'Pause the timeline'); }
    const v0 = valOf(from), v1 = valOf(D.today), dur = Math.max(2500, (v1 - v0) / 120 * 1000);
    let t0 = null;
    const stepF = ts => {
      if (!host.isConnected) return stop();
      if (t0 === null) t0 = ts;
      const k = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - k, 2);
      setDay(dayAt(v0 + (v1 - v0) * e));
      if (k < 1) state.raf = requestAnimationFrame(stepF); else stop();
    };
    state.raf = requestAnimationFrame(stepF);
  }
  function stop() {
    cancelAnimationFrame(state.raf); state.playing = false;
    const btn = host.querySelector('.play'); if (btn) { btn.textContent = '▶'; btn.setAttribute('aria-label', 'Play the timeline'); }
  }

  // ---- interaction
  svg.addEventListener('click', ev => {
    const pt = ev.target.closest('.pt');
    if (pt && mode !== 'locator') { location.hash = '#/project/' + pt.dataset.id; return; }
    const cal = ev.target.closest('[data-cal]');
    if (cal) { location.hash = '#/calendar?county=' + encodeURIComponent(cal.dataset.cal); return; }
    const c = ev.target.closest('.county.link');
    if (c) location.hash = '#/county/' + c.dataset.county.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  });
  svg.addEventListener('keydown', ev => { if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.closest('.pt')) { ev.preventDefault(); location.hash = '#/project/' + ev.target.closest('.pt').dataset.id; } });
  const showTip = (target, cx, cy) => {
    const pt = target.closest('.pt'), cty = target.closest('.county.link');
    if (pt) {
      const pr = D.byId[pt.dataset.id], st = statusOn(pr, state.day);
      tip.innerHTML = `<span>${esc(STATUS[st].label)}</span><b>${esc(pr.name)}</b>${esc(pr.place)}`;
    } else if (cty && mode !== 'locator') {
      const c = D.counties.find(x => x.name === cty.dataset.county);
      tip.innerHTML = `<span>County sheet</span><b>${esc(c.name)} County</b>${c.projects.length ? c.projects.length + ' project' + (c.projects.length > 1 ? 's' : '') + ' · ' : ''}${c.standing.length ? c.standing.length + ' standing meeting' + (c.standing.length > 1 ? 's' : '') : 'dates on the calendar'}`;
    } else { tip.hidden = true; return; }
    const r = host.getBoundingClientRect();
    tip.hidden = false;
    const x = Math.min(cx - r.left + 14, r.width - tip.offsetWidth - 8), y = Math.max(8, cy - r.top - tip.offsetHeight - 10);
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  };
  svg.addEventListener('pointermove', ev => { if (ev.pointerType === 'mouse') showTip(ev.target, ev.clientX, ev.clientY); });
  svg.addEventListener('pointerleave', () => { tip.hidden = true; });
  svg.addEventListener('focusin', ev => { const b = ev.target.getBoundingClientRect(); showTip(ev.target, b.right, b.top); });
  svg.addEventListener('focusout', () => { tip.hidden = true; });
  host.querySelectorAll('[data-layer]').forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.layer; state.layers.has(k) ? state.layers.delete(k) : state.layers.add(k);
    b.setAttribute('aria-pressed', state.layers.has(k)); draw();
  }));

  // ---- resize: labels are sized in screen pixels
  let rt = 0;
  const ro = new ResizeObserver(() => { clearTimeout(rt); rt = setTimeout(draw, 80); });
  ro.observe(svg);

  setDay(D.today);
  if (opts.autoplay && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    let played = false; try { played = sessionStorage.getItem('wvaiwatch.played') === '1'; sessionStorage.setItem('wvaiwatch.played', '1'); } catch (e) { /* ignore */ }
    if (!played) { setDay(START); setTimeout(() => play(START), 400); }
  }
  return { setDay, draw };
}
