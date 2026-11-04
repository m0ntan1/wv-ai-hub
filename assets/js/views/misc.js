// Smaller pages: projects index, full map, hubs, receipts, not found.
import { D } from '../data.js';
import { esc, fmtDate, STATUS, STATUS_ORDER, statusColor, srcLink, srcLinks, hostOf } from '../lib.js';
import { mountMap } from '../map.js';
import { projectCard } from '../parts.js';

export function projectsIndex(main) {
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Projects · ${D.projects.length} case files</div>
      <h1 class="page-h">Every data center and <em>AI power</em> project</h1>
      <p class="lede">Data centers, the gas plants and microgrids built to power them, and the cases they set off. Each case file pulls together the timeline, permits and court cases, people, upcoming dates, and sources.</p>
    </header>
    ${STATUS_ORDER.map(st => { const list = D.projects.filter(p => p.status === st); return list.length ? `<section class="sec" style="padding:22px 0 6px"><div class="sec-h"><span style="color:${statusColor(st)}">●</span> ${esc(STATUS[st].label)} · ${list.length}</div><div class="pcards">${list.map(projectCard).join('')}</div></section>` : ''; }).join('')}
    <section class="sec"><div class="sec-h">Transmission lines</div>
      <div class="grid-auto">${D.lines.map(l => `<div class="card"><div class="kicker" style="color:var(--grid)">${esc(l.short)}</div><h3 style="font-family:var(--serif);font-weight:400;font-size:26px;margin:6px 0">${esc(l.name)}</h3><p class="dim" style="font-size:14px">${esc(l.note)}</p>${srcLinks(l.sources)}</div>`).join('')}</div>
    </section>
  </div>`;
  return 'Projects';
}

export function mapPage(main) {
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Map · place × time</div>
      <h1 class="page-h">Watch it <em>happen</em></h1>
      <p class="lede">Press play, or drag the slider, to see projects appear, get certified, go under construction, and get contested, from the day HB 2014 became law to the decisions still ahead. Click a project for its case file, or a county for its sheet.</p>
    </header>
    <section class="sec" style="padding-top:18px"><div id="bigMap"></div>
      <div class="legend" style="margin-top:12px">${STATUS_ORDER.map(st => `<span><i style="background:${statusColor(st)}"></i>${esc(STATUS[st].label)}</span>`).join('')}<span><i style="background:var(--grid);border-radius:1px;height:3px;width:14px;vertical-align:3px"></i>Transmission line</span><span><i style="background:var(--signal)"></i>Upcoming public dates (count)</span></div>
    </section>
  </div>`;
  mountMap(main.querySelector('#bigMap'), { mode: 'full', scrubber: true, layerPills: true, layers: ['projects', 'lines', 'dates', 'names'],
    note: 'Markers are approximate (town or road level), not parcel boundaries. Lines are illustrative corridors; Valley Link has no approved route. County lines: U.S. Census Bureau.' });
  return 'Map';
}

export function hubs(main) {
  const major = D.hubs.filter(h => h.major), emerging = D.hubs.filter(h => !h.major);
  const hubHTML = h => `<article class="hub" id="hub-${esc(h.id)}"><div><h2>${esc(h.name)}</h2><div class="tagl">${esc(h.tag)}${h.pop ? ' · ' + esc(h.pop) : ''}</div><div class="tagl" style="color:var(--cyan)">${h.stories.length} ${h.stories.length === 1 ? 'story' : 'stories'}</div></div>
    <div>${h.stories.map(s => `<div class="story"><strong>${esc(s.title)}</strong>${s.html}${srcLinks(s.sources)}</div>`).join('')}</div></article>`;
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Hubs · the other AI story</div>
      <h1 class="page-h">Research, classrooms, <em>startups</em></h1>
      <p class="lede">Not every AI story in West Virginia is a data center. These are the universities, schools, companies, and programs building AI skills and businesses in the state, plus the energy, computing, cybersecurity, and manufacturing work around them. Stories were first compiled in May 2026, and 13 were added on Nov 4, 2026. Each one links its source. Where a story reports an announcement, plan, or goal, it says so: jobs and investment figures are what was announced, not what has been delivered. See Receipts for how each was checked.</p>
    </header>
    <section class="sec"><div class="sec-h">Major hubs</div>${major.map(hubHTML).join('')}</section>
    <section class="sec"><div class="sec-h">Emerging hubs</div>${emerging.map(hubHTML).join('')}</section>
  </div>`;
  return 'Hubs';
}

export function receipts(main, q) {
  const R = D.receipts, S = R.summary;
  const SEC = { hub: 'Hub stories', project: 'Projects', event: 'Calendar', standing: 'Standing meetings', docket: 'Docket', people: 'People' };
  const secOf = r => r.sec.startsWith('hub') ? 'hub' : r.sec;
  const LBL = { ok: '✓ Confirmed', psc: 'PSC notice', verify: '⚠ Verify', gap: 'Gap' };
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Receipts · checked ${esc(fmtDate(R.checked))}</div>
      <h1 class="page-h">How we know <em>what we say</em></h1>
      <p class="lede">On ${esc(fmtDate(R.checked))}, every item on this site was checked against the source it links to. A script fetched each source and confirmed that the key facts (numbers, names, dates) appear in it. Items we could not confirm stay on the site, marked ⚠ Verify with the reason, so you can check them yourself. Items added after that date, such as the hub stories added Nov 4, 2026, say when they were checked.</p>
    </header>
    <div class="rc-stats">
      <div><b style="color:var(--ok)">${S.ok || 0}</b><span>confirmed against the linked source</span></div>
      <div><b>${S.psc || 0}</b><span>confirmed from PSC docket notices (the PSC site blocks automated tools)</span></div>
      <div><b style="color:var(--signal)">${S.verify || 0}</b><span>shown with ⚠ Verify and the reason</span></div>
      <div><b>${S.gap || 0}</b><span>unresolved gaps</span></div>
    </div>
    <p class="dim" style="font-size:14px">Full method, corrections, and every check: <a class="src" href="https://github.com/m0ntan1/WV-AI-HUB/blob/main/${esc(R.log)}" target="_blank" rel="noopener">verification log ↗</a> · How the site stays current: <a class="src" href="https://github.com/m0ntan1/WV-AI-HUB/blob/main/docs/update-plan.md" target="_blank" rel="noopener">update plan ↗</a> · Turn on <b>Receipts mode</b> in the header to see sources inline across the site. Spot an error? <a class="src" href="#/contact?topic=correction">Send a correction</a>.</p>
    <section class="sec">
      <div class="cx-toolbar" style="margin-top:0">
        <input class="rc-search" id="rcQ" type="search" placeholder="Search items or sources" aria-label="Search receipts">
        <label>Status <select id="rcS"><option value="all">All</option>${Object.keys(LBL).filter(k => S[k]).map(k => `<option value="${k}"${q.get('status') === k ? ' selected' : ''}>${LBL[k]}</option>`).join('')}</select></label>
        <label>Section <select id="rcSec"><option value="all">All</option>${Object.entries(SEC).map(([k, v]) => `<option value="${k}">${v}</option>`).join('')}</select></label>
        <span class="dim mono" id="rcN" style="font-size:12px"></span>
      </div>
      <div style="overflow-x:auto"><table class="rc-table"><thead><tr><th>Item</th><th>Status</th><th class="hide-sm">Section</th><th class="hide-sm">Sources</th></tr></thead><tbody id="rcB"></tbody></table></div>
    </section>
  </div>`;
  const render = () => {
    const qq = main.querySelector('#rcQ').value.toLowerCase(), st = main.querySelector('#rcS').value, sec = main.querySelector('#rcSec').value;
    const rows = R.rows.filter(r => (st === 'all' || r.status === st) && (sec === 'all' || secOf(r) === sec) && (!qq || (r.title + ' ' + r.urls.join(' ') + ' ' + r.note).toLowerCase().includes(qq)));
    main.querySelector('#rcN').textContent = rows.length + ' of ' + R.rows.length;
    main.querySelector('#rcB').innerHTML = rows.map(r => `<tr><td>${esc(r.title)}${r.note ? `<div class="dim" style="font-size:12.5px;margin-top:3px">${esc(r.note)}</div>` : ''}</td>
      <td class="s" style="color:${r.status === 'ok' ? 'var(--ok)' : r.status === 'verify' ? 'var(--signal)' : 'var(--fg-2)'}">${LBL[r.status] || esc(r.status)}</td>
      <td class="hide-sm s">${esc(SEC[secOf(r)] || r.sec)}${r.sec.startsWith('hub:') ? '<br>' + esc(r.sec.slice(4)) : ''}</td>
      <td class="hide-sm">${r.urls.map(u => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(hostOf(u))}</a>`).join('<br>')}</td></tr>`).join('');
  };
  ['rcQ', 'rcS', 'rcSec'].forEach(id => main.querySelector('#' + id).addEventListener('input', render));
  render();
  return 'Receipts';
}

export function notFound(main) {
  main.innerHTML = `<div class="wrap" style="padding:80px var(--gutter)"><div class="kicker">404</div><h1 class="page-h">Nothing on the record <em>here</em></h1><p class="lede">That page does not exist. Try the <a href="#/">front page</a>, the <a href="#/map">map</a>, or the <a href="#/projects">projects</a>.</p></div>`;
  return 'Not found';
}
