import { D } from '../data.js';
import { esc, fmtDate, STATUS, stamp, vfy, srcLink, srcLinks, rx, countyHref, plural, icsDownload, hostOf } from '../lib.js';
import { mountMap } from '../map.js';
import { docketCard, eventRow, standingCard, wireIcs, statusStamp } from '../parts.js';
import { stories, storyHTML } from './news.js';

const KIND_COLOR = { certified: 'var(--cyan)', violation: 'var(--alarm)', court: 'var(--legal)', permit: 'var(--grid)', hearing: 'var(--signal)', psc: 'var(--ok)', redaction: 'var(--fg)', protest: 'var(--alarm)', money: 'var(--gas)' };

export function project(main, id) {
  const p = D.byId[id];
  if (!p) return null;
  const idx = D.projects.indexOf(p), prev = D.projects[(idx - 1 + D.projects.length) % D.projects.length], next = D.projects[(idx + 1) % D.projects.length];
  const docket = D.docket.filter(k => k.projects.includes(id));
  const people = D.people.filter(x => x.projects.includes(id));
  const nodeIds = D.network.nodes.filter(n => n.project === id).map(n => n.id);
  const edges = D.network.edges.filter(e => nodeIds.includes(e.a) || nodeIds.includes(e.b));
  const evs = D.events.filter(e => e.project === id || (p.counties.includes(e.county) && !D.isPast(e)));
  const upcoming = evs.filter(e => !D.isPast(e) && e.date && !e.tbd);
  const tbd = evs.filter(e => e.tbd && e.project === id);
  const standing = D.standing.filter(s => s.projects.includes(id) || p.counties.includes(s.county));
  const rc = D.receiptFor('project', p.name);
  const cert = p.timeline.find(t => t.kind === 'certified');
  const press = stories({ project: id });
  const tabs = [['overview', 'Overview'], ['timeline', 'Timeline', p.timeline.length], ['cases', 'Permits & cases', docket.length], ['people', 'People', people.length + edges.length], ['take-part', 'Take part', upcoming.length + standing.length], ...(press.length ? [['news', 'In the news', press.length]] : []), ['receipts', 'Receipts', p.sources.length]];

  main.innerHTML = `<div class="wrap">
    <div class="crumb"><a href="#/projects">Projects</a> / ${p.counties.map(c => `<a href="${countyHref(c)}">${esc(c)} County</a>`).join(' · ')} / ${esc(p.short)}</div>
    <header class="cf-head">
      <div>
        <h1>${esc(p.name)}</h1>
        <div class="cf-meta"><span>${esc(p.developer)}</span><span>${esc(p.place)}</span></div>
        ${p.verify ? `<p style="margin-top:10px">${vfy(p.verify)} <span class="dim">${esc(p.verify)}</span></p>` : ''}
      </div>
      <div class="cf-stamps">${statusStamp(p, true)}${cert && p.status !== 'certified' ? stamp('Certified ' + fmtDate(cert.d), 'cyan') : ''}</div>
    </header>
    <nav class="tabs" aria-label="Case file sections">${tabs.map(([k, l, n], i) => `<button type="button" class="tab${i === 0 ? ' on' : ''}" data-go="${k}">${l}${n !== undefined ? `<span class="ct">${n}</span>` : ''}</button>`).join('')}</nav>

    <div class="cf-grid">
      <div>
        <section class="cf-sec" id="s-overview">
          <dl class="facts">${p.facts.map(f => `<div><dt>${esc(f.k)}</dt><dd>${esc(f.v)} ${vfy(f.verify)}</dd></div>`).join('')}</dl>
          ${rx(p.sources, { checked: p.checked, note: rc ? `Verification pass: ${rc.status === 'ok' ? 'every key fact found in the linked sources' : rc.status === 'verify' ? 'could not be fully confirmed (' + rc.note + ')' : rc.status}.` : '' })}
          <div class="latest"><time>Latest · ${esc(p.latest.d)}</time>${esc(p.latest.t)}</div>
          ${p.scale ? scaleHTML(p.scale) : ''}
        </section>

        <section class="cf-sec" id="s-timeline">
          <div class="sec-h">Timeline</div>
          <ol class="tl">${p.timeline.map(t => `<li class="${t.next ? 'next' : ''}" style="--c:${t.next ? 'var(--signal)' : KIND_COLOR[t.kind] || 'var(--fg-3)'}"><time>${t.next ? 'Next · ' + (t.d ? esc(fmtDate(t.d)) : 'date TBD') : t.d ? esc(fmtDate(t.d)) : 'Date not confirmed'}</time>${esc(t.t)} ${vfy(t.verify)}${t.src ? srcLink({ label: hostOf(t.src), url: t.src }) : ''}</li>`).join('')}</ol>
        </section>

        <section class="cf-sec" id="s-cases">
          <div class="sec-h">Permits &amp; cases <a class="src act" href="#/docket">Full docket →</a></div>
          ${docket.length ? `<div class="grid-auto">${docket.map(k => docketCard(k)).join('')}</div>` : '<p class="empty">No court, PSC, or permit case is tracked for this project yet.</p>'}
        </section>

        <section class="cf-sec" id="s-people">
          <div class="sec-h">People &amp; connections <a class="src act" href="#/people${nodeIds[0] ? '?focus=' + nodeIds[0] : ''}">See the web →</a></div>
          ${edges.length ? `<ul class="src-list">${edges.map(e => { const a = D.net.byId[e.a], b = D.net.byId[e.b]; return `<li><span><b>${esc(a.label)}</b> <span class="dim">${esc(e.label)}</span> <b>${esc(b.label)}</b>${e.note ? ` <span class="dim">· ${esc(e.note)}</span>` : ''}</span>${srcLink({ label: hostOf(e.src), url: e.src })}</li>`; }).join('')}</ul>` : ''}
          ${people.length ? `<ul class="src-list" style="margin-top:12px">${people.map(x => `<li><span><b>${esc(x.name)}</b> <span class="dim">${x.role}</span></span><span>${x.sources.slice(0, 1).map(s => srcLink(s)).join('')}</span></li>`).join('')}</ul>` : ''}
          ${!edges.length && !people.length ? '<p class="empty">No named people are linked to this project yet.</p>' : ''}
        </section>

        <section class="cf-sec" id="s-take-part">
          <div class="sec-h">Take part</div>
          ${upcoming.length ? upcoming.map(eventRow).join('') : '<p class="empty">No upcoming dated events for this project or its county.</p>'}
          ${tbd.map(eventRow).join('')}
          ${standing.length ? `<div class="cx-st-grid">${standing.map(standingCard).join('')}</div>` : ''}
        </section>

        ${press.length ? `<section class="cf-sec" id="s-news">
          <div class="sec-h">In the news <a class="src act" href="#/news?project=${id}">All ${press.length} →</a></div>
          <div class="news-list">${press.slice(0, 6).map(s => storyHTML(s, { tags: false })).join('')}</div>
          <p class="dim" style="font-size:12.5px;margin-top:8px">Headlines are each outlet's own words, not checked by us.</p>
        </section>` : ''}

        <section class="cf-sec" id="s-receipts">
          <div class="sec-h">Receipts · checked ${esc(fmtDate(p.checked))}</div>
          <ul class="src-list">${p.sources.map(s => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)} ↗</a><span class="mono dim" style="font-size:11px">${esc(hostOf(s.url))}</span></li>`).join('')}</ul>
          <p class="dim" style="font-size:13px;margin-top:10px">${rc ? (rc.status === 'ok' ? '<span class="ok">✓ VERIFIED</span> On ' + esc(fmtDate(p.checked)) + ', the key facts on this page were found in the linked sources.' : rc.status === 'verify' ? vfy(rc.note) + ' ' + esc(rc.note) : '') : ''} <a class="src" href="#/receipts">How we check →</a> · <a class="src" href="#/contact?topic=correction&about=${encodeURIComponent(p.name)}">Report an error</a></p>
        </section>

        <nav class="pager"><a href="#/project/${prev.id}"><span>← Previous</span>${esc(prev.short)}</a><a href="#/project/${next.id}" style="text-align:right"><span>Next →</span>${esc(next.short)}</a></nav>
      </div>

      <aside>
        <div class="side-box act">
          <h4>Take part</h4>
          ${upcoming[0] ? `<p><b>Next date:</b> ${esc(upcoming[0].title)}, ${esc(fmtDate(upcoming[0].date))}.</p>` : `<p>${tbd[0] ? '<b>Pending:</b> ' + esc(tbd[0].title) + '.' : 'No scheduled public date right now.'}</p>`}
          ${standing[0] ? `<p style="margin-top:8px"><b>${esc(standing[0].body)}:</b> ${esc(standing[0].rule)}. ${esc(standing[0].where)}.</p>` : ''}
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">${upcoming[0] && upcoming[0].date && !upcoming[0].approx ? `<button type="button" class="btn pri" data-ics="${esc(upcoming[0].id)}">+ Add to calendar</button>` : ''}${p.counties.map(c => `<a class="btn" href="${countyHref(c)}">⎙ ${esc(c)} sheet</a>`).join('')}</div>
        </div>
        <div class="side-box"><h4>Where</h4><div id="locator"></div><p style="font-size:12.5px;margin-top:6px">${esc(p.place)}. Marker is approximate.</p></div>
        ${(p.redactions || []).map(r => `<div class="redact-block"><div class="lbl">${esc(r.label)}</div><div><span class="redact" style="width:92%"></span><br><span class="redact" style="width:64%"></span> <span class="redact" style="width:28%"></span><br><span class="redact" style="width:80%"></span></div><div class="why">Withheld. ${esc(r.why)} ${srcLink({ label: 'source', url: r.src })}</div></div>`).join('')}
        <div class="side-box"><h4>Status history</h4>${p.history.map(h => `<p style="margin-top:6px"><span class="mono" style="font-size:11px;color:var(--fg-3)">${esc(fmtDate(h.d).toUpperCase())}</span><br>${esc(STATUS[h.status].label)}: ${esc(h.t)}</p>`).join('')}</div>
      </aside>
    </div>
  </div>`;

  mountMap(main.querySelector('#locator'), { mode: 'locator', focus: id, label: `Location of ${p.name}` });
  wireIcs(main, icsDownload);
  // Tabs scroll to sections and track the one in view.
  const tabsEl = main.querySelector('.tabs');
  tabsEl.addEventListener('click', ev => { const b = ev.target.closest('[data-go]'); if (b) main.querySelector('#s-' + b.dataset.go).scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  const io = new IntersectionObserver(entries => entries.forEach(en => { if (en.isIntersecting) tabsEl.querySelectorAll('.tab').forEach(t => t.classList.toggle('on', 's-' + t.dataset.go === en.target.id)); }), { rootMargin: '-140px 0px -60% 0px' });
  main.querySelectorAll('.cf-sec').forEach(s => io.observe(s));
  return p.name;
}

function scaleHTML(s) {
  const cols = s.big ? 10 : s.n > 300 ? 48 : s.n > 100 ? 24 : 15;
  const dot = (n, color) => Array.from({ length: n }, () => `<i style="background:var(--${color})"></i>`).join('');
  return `<div class="sec-h" style="margin-top:26px">Scale, made physical ${srcLink({ label: hostOf(s.src), url: s.src })}</div>
    <div class="dots${s.big ? ' big' : ''}" style="grid-template-columns:repeat(${cols},1fr)" role="img" aria-label="${s.n} ${esc(s.unit)}${s.extra ? ' and ' + s.extra.n + ' ' + esc(s.extra.unit) : ''}">${dot(s.n, s.color)}${s.extra ? dot(s.extra.n, s.extra.color) : ''}</div>
    <div class="scale-cap"><b style="color:var(--${s.color})">${s.n}</b><span>${esc(s.caption)}</span></div>
    ${s.bars ? `<div class="bars"><div class="sec-h" style="margin:8px 0 0">${esc(s.bars.title)} ${srcLink({ label: hostOf(s.bars.src), url: s.bars.src })}</div>${(() => { const max = Math.max(...s.bars.rows.map(r => r[1])); return s.bars.rows.map(([k, v]) => `<div class="bar"><span>${esc(k)}</span><span class="b"><i style="width:${(v / max * 100).toFixed(1)}%"></i></span><span class="v">${v.toLocaleString()} t</span></div>`).join(''); })()}</div>` : ''}`;
}
