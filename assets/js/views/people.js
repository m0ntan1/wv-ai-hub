import { D } from '../data.js';
import { esc, srcLink, hostOf } from '../lib.js';

const KIND = { person: { c: 'var(--fg)', l: 'Person' }, firm: { c: 'var(--signal)', l: 'Law firm' }, company: { c: 'var(--cyan)', l: 'Company' }, project: { c: 'var(--alarm)', l: 'Project' }, case: { c: 'var(--legal)', l: 'Case' }, group: { c: 'var(--ok)', l: 'Group' }, law: { c: 'var(--grid)', l: 'Law' } };
const VW = 1240, VH = 860;
let LAYOUT = null;

/** Deterministic force layout (same picture on every load). */
function layout() {
  if (LAYOUT) return LAYOUT;
  const nodes = D.network.nodes.map((n, i) => {
    const a = (i / D.network.nodes.length) * Math.PI * 2;
    return { ...n, x: VW / 2 + Math.cos(a) * 300, y: VH / 2 + Math.sin(a) * 240, vx: 0, vy: 0 };
  });
  const by = Object.fromEntries(nodes.map(n => [n.id, n]));
  const edges = D.network.edges.map(e => ({ ...e, s: by[e.a], t: by[e.b] }));
  const deg = {}; edges.forEach(e => { deg[e.a] = (deg[e.a] || 0) + 1; deg[e.b] = (deg[e.b] || 0) + 1; });
  const k = 78;
  for (let it = 0; it < 500; it++) {
    const temp = 18 * (1 - it / 500) + 0.5;
    nodes.forEach(n => { n.fx = 0; n.fy = 0; });
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 0.01, d = Math.sqrt(d2);
      const f = (k * k) / d * 1.2;
      dx /= d; dy /= d; a.fx += dx * f; a.fy += dy * f; b.fx -= dx * f; b.fy -= dy * f;
    }
    edges.forEach(e => {
      let dx = e.t.x - e.s.x, dy = e.t.y - e.s.y; const d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const f = (d * d) / k * 0.9; dx /= d; dy /= d;
      e.s.fx += dx * f; e.s.fy += dy * f; e.t.fx -= dx * f; e.t.fy -= dy * f;
    });
    nodes.forEach(n => {
      n.fx += (VW / 2 - n.x) * 0.9; n.fy += (VH / 2 - n.y) * 1.3;
      const m = Math.sqrt(n.fx * n.fx + n.fy * n.fy) || 1;
      n.x += n.fx / m * Math.min(m, temp); n.y += n.fy / m * Math.min(m, temp);
      n.x = Math.max(110, Math.min(VW - 110, n.x)); n.y = Math.max(40, Math.min(VH - 50, n.y));
    });
  }
  nodes.forEach(n => { n.deg = deg[n.id] || 0; n.r = n.kind === 'firm' ? 15 : n.kind === 'law' ? 13 : n.kind === 'project' ? 11 : 7 + Math.min(4, n.deg); });
  // Separate overlapping labels: each node owns a box (its label under the dot); push overlapping boxes apart.
  const box = n => { const w = n.label.length * 7 + 10; return { l: n.x - w / 2, r: n.x + w / 2, t: n.y - n.r - 4, b: n.y + n.r + 20 }; };
  for (let it = 0; it < 300; it++) {
    let moved = false;
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j], A = box(a), B = box(b);
      const ox = Math.min(A.r, B.r) - Math.max(A.l, B.l), oy = Math.min(A.b, B.b) - Math.max(A.t, B.t);
      if (ox > 0 && oy > 0) {
        moved = true;
        if (oy < ox) { const d = (oy / 2 + 1) * (a.y < b.y ? -1 : 1); a.y += d; b.y -= d; }
        else { const d = (ox / 2 + 1) * (a.x < b.x ? -1 : 1); a.x += d; b.x -= d; }
      }
    }
    nodes.forEach(n => { const half = n.label.length * 3.5 + 8; n.x = Math.max(half, Math.min(VW - half, n.x)); n.y = Math.max(30, Math.min(VH - 30, n.y)); });
    if (!moved) break;
  }
  LAYOUT = { nodes, edges, by };
  return LAYOUT;
}

export function people(main, q) {
  const L = layout();
  const projFilter = q.get('project') || 'all';
  const groups = [...new Set(D.people.map(p => p.group))];
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">People · ${D.people.length} entries · ${D.network.edges.length} sourced connections</div>
      <h1 class="page-h">Who shows up <em>where</em></h1>
      <p class="lede">Officials, companies, lawyers, judges, and the residents and groups pushing back. Click any name in the web to see every connection it has and the source for each one.</p>
    </header>
    <section class="sec">
      <div class="web-wrap">
        <div class="web-canvas"><svg class="web-svg" viewBox="0 0 ${VW} ${VH}" role="img" aria-label="Network of people, firms, companies, projects, and cases"></svg></div>
        <aside class="web-side" id="webSide" aria-live="polite"></aside>
      </div>
      <div class="legend" style="margin-top:10px">${Object.values(KIND).map(k => `<span><i style="background:${k.c}"></i>${k.l}</span>`).join('')}</div>
    </section>
    <section class="sec">
      <div class="sec-h">Directory
        <label class="act" style="display:flex;gap:8px;align-items:center;font-size:12px;color:var(--fg-2)">Project <select id="pplProj"><option value="all">All</option>${D.projects.map(p => `<option value="${p.id}"${p.id === projFilter ? ' selected' : ''}>${esc(p.short)}</option>`).join('')}</select></label>
      </div>
      <div class="ppl-cols" id="pplCols"></div>
    </section>
  </div>`;

  const svg = main.querySelector('svg');
  const edgeHTML = L.edges.map((e, i) => `<line class="e" data-i="${i}" x1="${e.s.x.toFixed(1)}" y1="${e.s.y.toFixed(1)}" x2="${e.t.x.toFixed(1)}" y2="${e.t.y.toFixed(1)}"/>`).join('');
  const nodeHTML = L.nodes.map(n => `<g class="n" data-id="${n.id}" tabindex="0" role="button" aria-label="${esc(n.label)}, ${KIND[n.kind].l}">
      ${n.kind === 'project' ? `<rect x="${(n.x - n.r).toFixed(1)}" y="${(n.y - n.r).toFixed(1)}" width="${n.r * 2}" height="${n.r * 2}" rx="3" fill="${KIND[n.kind].c}"/>` : `<circle cx="${n.x.toFixed(1)}" cy="${n.y.toFixed(1)}" r="${n.r}" fill="${n.kind === 'person' ? 'var(--bg)' : KIND[n.kind].c}" stroke="${KIND[n.kind].c}" stroke-width="2.5"/>`}
      <text x="${n.x.toFixed(1)}" y="${(n.y + n.r + 15).toFixed(1)}" text-anchor="middle">${esc(n.label)}</text>
    </g>`).join('');
  svg.innerHTML = `<g class="edges">${edgeHTML}</g><g class="elbls"></g><g class="nodes">${nodeHTML}</g>`;

  const side = main.querySelector('#webSide');
  function focus(id) {
    const n = id && L.by[id];
    const nb = new Set(n ? [id] : []);
    const hot = n ? L.edges.filter(e => e.a === id || e.b === id) : [];
    hot.forEach(e => { nb.add(e.a); nb.add(e.b); });
    svg.querySelectorAll('.e').forEach(l => { const e = L.edges[+l.dataset.i]; const h = n && (e.a === id || e.b === id); l.classList.toggle('hot', !!h); l.classList.toggle('dim', !!n && !h); });
    svg.querySelectorAll('.n').forEach(g => g.classList.toggle('dim', !!n && !nb.has(g.dataset.id)));
    svg.querySelector('.elbls').innerHTML = hot.map(e => { const mx = (e.s.x + e.t.x) / 2, my = (e.s.y + e.t.y) / 2; return `<text class="elbl" x="${mx.toFixed(1)}" y="${(my + 4).toFixed(1)}" text-anchor="middle">${esc(e.label)}</text>`; }).join('');
    if (!n) {
      side.innerHTML = `<div class="kicker">Start here</div>
        <div class="who" style="margin-top:8px">${L.nodes.length} names, ${L.edges.length} links</div>
        <p class="role">Every line is a documented relationship with a source. Pick a starting point:</p>
        <div class="pills" style="margin-top:12px">${['bowles-rice', 'nscale', 'stephen-new', 'hb2014', 'morrisey', 'ica'].map(x => `<button type="button" class="pill" data-focus="${x}">${esc(L.by[x].label)}</button>`).join('')}</div>
        <div class="caveat">A connection is a documented relationship, not an accusation. Lawyers represent clients and officials do their jobs; the web shows who represented or decided what, and when, and links the reporting.</div>`;
      history.replaceState(null, '', '#/people');
      return;
    }
    const proj = n.project && D.byId[n.project];
    side.innerHTML = `<div class="kicker" style="display:flex;justify-content:space-between"><span>Focused</span><span>${KIND[n.kind].l}</span></div>
      <div class="who" style="margin-top:8px">${esc(n.label)}</div>
      ${n.sub ? `<div class="role">${esc(n.sub)}</div>` : ''}
      ${proj ? `<p style="margin-top:10px"><a class="btn" href="#/project/${proj.id}">Open the ${esc(proj.short)} case file →</a></p>` : ''}
      <div style="margin-top:14px">${hot.map(e => { const a = L.by[e.a], b = L.by[e.b]; return `<div class="edge"><button type="button" data-focus="${e.a}" style="font-weight:700">${esc(a.label)}</button> <span class="dim">${esc(e.label)}</span> <button type="button" data-focus="${e.b}" style="font-weight:700">${esc(b.label)}</button>${e.note ? `<div class="dim" style="margin-top:3px">${esc(e.note)}</div>` : ''}<div style="margin-top:5px">${srcLink({ label: hostOf(e.src), url: e.src })} <span class="ok">✓</span></div></div>`; }).join('')}</div>
      <p style="margin-top:12px"><button type="button" class="btn" data-focus="">Clear focus</button></p>
      <div class="caveat">A connection is a documented relationship, not an accusation. Each line links the reporting it comes from.</div>`;
    history.replaceState(null, '', '#/people?focus=' + id);
  }
  main.addEventListener('click', ev => { const f = ev.target.closest('[data-focus]'); if (f) { focus(f.dataset.focus); return; } const g = ev.target.closest('.n'); if (g) focus(g.dataset.id); });
  svg.addEventListener('keydown', ev => { const g = ev.target.closest('.n'); if (g && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); focus(g.dataset.id); } });
  focus(q.get('focus') || '');

  const renderDir = pid => {
    main.querySelector('#pplCols').innerHTML = groups.map(g => {
      const list = D.people.filter(x => x.group === g && (pid === 'all' || x.projects.includes(pid)));
      if (!list.length) return '';
      return `<div><h3>${esc(g)}</h3><ul>${list.map(x => `<li><strong>${esc(x.name)}</strong>${x.role}
        <div class="srcs">${x.projects.filter(id => D.byId[id]).map(id => `<a class="tag" href="#/project/${id}">${esc(D.byId[id].short)}</a>`).join('')}${x.sources.map(s => srcLink(s)).join('')}</div></li>`).join('')}</ul></div>`;
    }).join('') || '<p class="empty">No entries for this project.</p>';
  };
  main.querySelector('#pplProj').addEventListener('change', ev => renderDir(ev.target.value));
  renderDir(projFilter);
  return 'People';
}
