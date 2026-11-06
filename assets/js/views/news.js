// News aggregator: headlines gathered by tools/fetch_news.py (data/news.json), grouped into stories.
import { D } from '../data.js';
import { esc, safeUrl, MON } from '../lib.js';
import { readCard, latestRead } from './reads.js';

const when = iso => { const d = new Date(iso); return isNaN(d) ? '' : MON[d.getMonth()] + ' ' + d.getDate(); };
export function ago(iso) {
  const h = Math.round((Date.now() - new Date(iso)) / 3600000);
  if (!isFinite(h)) return '';
  if (h < 1) return 'less than an hour ago';
  if (h < 48) return h + ' hour' + (h === 1 ? '' : 's') + ' ago';
  return Math.round(h / 24) + ' days ago';
}

/** Group items into stories: the lead item plus the other outlets that covered it. Newest first. */
export function stories({ project, source, q } = {}) {
  const by = new Map();
  (D.news.items || []).forEach(i => { const k = i.story || i.id; if (!by.has(k)) by.set(k, []); by.get(k).push(i); });
  let list = [...by.entries()].map(([k, items]) => {
    const lead = items.find(i => i.id === k) || items[0];
    return { lead, also: items.filter(i => i !== lead), latest: items.reduce((m, i) => i.d > m ? i.d : m, ''), projects: [...new Set(items.flatMap(i => i.projects || []))] };
  });
  if (project) list = list.filter(s => s.projects.includes(project));
  if (source) list = list.filter(s => [s.lead, ...s.also].some(i => i.source === source));
  if (q) { const qq = q.toLowerCase(); list = list.filter(s => [s.lead, ...s.also].some(i => (i.title + ' ' + i.summary + ' ' + i.source).toLowerCase().includes(qq))); }
  return list.sort((a, b) => a.latest < b.latest ? 1 : -1);
}

export function storyHTML(s, { summary = false, tags = true } = {}) {
  const l = s.lead;
  return `<article class="news-item">
    <div class="news-meta"><time datetime="${esc(l.d)}">${esc(when(l.d))}</time><span>${esc(l.source)}</span></div>
    <h3><a href="${esc(safeUrl(l.url))}" target="_blank" rel="noopener">${esc(l.title)}</a></h3>
    ${summary && l.summary ? `<p class="news-sum">${esc(l.summary)}</p>` : ''}
    <div class="news-foot">
      ${tags && [s.lead, ...s.also].some(i => i.energy) ? `<span class="tag tag-energy" title="Coal, gas, utilities and the grid">Energy</span>` : ''}
      ${tags ? s.projects.map(id => `<a class="tag" href="${D.projLink(id)}">${esc(D.projName(id))}</a>`).join('') : ''}
      ${s.also.length ? `<details class="news-also"><summary>+${s.also.length} more outlet${s.also.length > 1 ? 's' : ''}</summary>${s.also.map(i => `<a href="${esc(safeUrl(i.url))}" target="_blank" rel="noopener">${esc(i.source)}: ${esc(i.title)}</a>`).join('')}</details>` : ''}
    </div>
  </article>`;
}

export const newsNote = () => `Gathered ${D.news.schedule ? D.news.schedule + ' ' : ''}from ${D.news.sources ? D.news.sources.length : 'several'} sources${D.news.updated ? ', last updated ' + ago(D.news.updated) : ''}. Headlines are each outlet's own words; we haven't checked them. Verified developments go in the desk log and the case files.`;

export function news(main, q) {
  const all = stories();
  const outlets = [...new Set((D.news.items || []).map(i => i.source))].sort((a, b) => a.localeCompare(b));
  const pids = [...new Set(all.flatMap(s => s.projects))].sort((a, b) => D.projName(a).localeCompare(D.projName(b)));
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">News · ${all.length} stories</div>
      <h1 class="page-h">In the <em>news</em></h1>
      <p class="lede">Coverage of West Virginia's data centers, microgrids, and power lines, and the energy fight behind them (coal and the miners, gas, power plants, utilities and rates; tagged Energy), from local papers, TV stations, newsletters, and national outlets. When several outlets cover the same story, it appears once, with the others listed under it.</p>
      <p class="dim" style="font-size:13.5px;margin-top:10px;max-width:820px">${esc(newsNote())}</p>
    </header>
    <div class="cx-toolbar">
      <input class="rc-search" id="nwQ" type="search" placeholder="Search headlines" aria-label="Search headlines" value="${esc(q.get('q') || '')}">
      <label>Project <select id="nwP"><option value="">All</option>${pids.map(p => `<option value="${p}"${p === q.get('project') ? ' selected' : ''}>${esc(D.projName(p))}</option>`).join('')}</select></label>
      <label>Outlet <select id="nwS"><option value="">All</option>${outlets.map(o => `<option${o === q.get('source') ? ' selected' : ''}>${esc(o)}</option>`).join('')}</select></label>
      <span class="dim mono" id="nwN" style="font-size:12px"></span>
    </div>
    ${latestRead() ? `<section style="max-width:860px;margin-top:18px">${readCard(latestRead(), { compact: true })}<p class="dim" style="font-size:13px;margin-top:-6px"><a href="#/rook">Every Rook's Read →</a></p></section>` : ''}
    <section class="news-list" id="nwList"></section>
  </div>`;
  const render = () => {
    const list = stories({ q: main.querySelector('#nwQ').value.trim(), project: main.querySelector('#nwP').value, source: main.querySelector('#nwS').value });
    main.querySelector('#nwN').textContent = list.length + ' of ' + all.length;
    let html = '', month = '';
    list.forEach(s => {
      const d = new Date(s.latest), m = d.toLocaleString('en-US', { month: 'long', year: 'numeric' });
      if (m !== month) { html += `<div class="cx-group-h" style="margin-top:22px">${esc(m)}</div>`; month = m; }
      html += storyHTML(s, { summary: true });
    });
    main.querySelector('#nwList').innerHTML = html || '<p class="empty">No stories match.</p>';
  };
  ['nwQ', 'nwP', 'nwS'].forEach(id => main.querySelector('#' + id).addEventListener('input', render));
  render();
  return 'News';
}
