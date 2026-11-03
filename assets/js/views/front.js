import { D } from '../data.js';
import { esc, fmtDate, toDate, DAYS, MONTHS, STAGES, store, srcLink, rx, ymd } from '../lib.js';
import { mountMap } from '../map.js';
import { countdownItems, chipsHTML, eventRow, projectCard } from '../parts.js';
import { stories, storyHTML, newsNote } from './news.js';

export function front(main) {
  const T = D.today, td = toDate(T);
  const todayEv = D.events.find(e => e.date === T && e.type === 'government');
  const certN = D.certified.length;
  const stats = D.meta.stats || [];
  const stageCount = id => D.docket.filter(k => k.stage === id).length;
  const county = store.get('county') || 'Mason';

  main.innerHTML = `
  <div class="topo">
  <div class="wrap">
    <header class="mast">
      <div>
        <div class="kicker">${DAYS[td.getDay()]}, ${MONTHS[td.getMonth()]} ${td.getDate()}, ${td.getFullYear()}${todayEv ? ` · <b>${esc(todayEv.title)}</b>` : ''} · Data updated ${esc(fmtDate(D.meta.updated))}</div>
        <h1>West Virginia's<br><em>AI Watch</em></h1>
      </div>
      <div class="sub"><b>Mapping AI Across the Mountain State</b>${D.projects.length} projects · ${D.docket.filter(k => k.body === 'psc').length} PSC dockets · ${D.docket.filter(k => k.body === 'courts' && k.id !== 'county-challenge').length} court cases<br>Every claim sourced · ⚠ marks the unconfirmed</div>
    </header>
    <div class="rule2"></div>

    <section class="sec" style="padding-top:18px">
      <div class="sec-h">Next times you can show up <a class="src act" href="calendar.ics">Subscribe to every date (.ics)</a></div>
      <div class="chips">${chipsHTML(countdownItems(5))}</div>
    </section>

    <div class="fp-body">
      <div>
        <h2 class="fp-hed">${D.projects.length} projects. ${certN} certified by the state. <span>For those ${certN}, no county zoning vote.</span></h2>
        <p class="lede" style="font-size:15.5px;margin-top:12px">HB 2014 lets certified data centers and their microgrids skip county and city zoning. This is everything that has been announced, permitted, protested, or sued over since, with a source on every line.</p>
        ${rx([{ label: 'HB 2014 bill history', url: 'https://bills.wvlegislature.gov/bill/history/2025/rs/HB2014' }, { label: 'WVCBP on local control', url: 'https://wvpolicy.org/five-ways-hb-2014-harms-communities-local-governments-and-schools/' }], { checked: D.meta.updated })}
        <div class="stats">${stats.map(s => `<div><b>${esc(String(s.v).replace('{events}', D.events.length))}</b><span>${esc(s.l)}</span>${rx([s.src && { label: s.srcLabel || 'Source', url: s.src }])}</div>`).join('')}</div>
        <div class="sec-h" style="margin-top:26px">On the desk <a class="src act" href="#/receipts">How we check</a></div>
        <ul class="desk">${D.desk.slice(0, 5).map(x => `<li><time>${esc(fmtDate(x.d, { year: false }))}</time><span>${esc(x.t)} ${srcLink({ label: 'source', url: x.src })}</span></li>`).join('')}</ul>
      </div>
      <div id="fpMap"></div>
    </div>
  </div>
  </div>

  <div class="wrap">
    <section class="sec">
      <div class="near">
        <div>
          <div class="sec-h">This week near you
            <label class="act" style="display:flex;gap:8px;align-items:center;font-size:12px;color:var(--fg-2)">County
              <select id="nearCounty">${D.counties.map(c => `<option${c.name === county ? ' selected' : ''}>${esc(c.name)}</option>`).join('')}</select></label>
          </div>
          <div id="nearList"></div>
        </div>
        <div>
          <div class="sec-h">Where every fight stands <a class="src act" href="#/docket">Docket →</a></div>
          <div class="stage-strip">${STAGES.map(s => `<a href="#/docket?stage=${s.id}"><b>${stageCount(s.id)}</b><span>${esc(s.label)}</span></a>`).join('')}</div>
          <div style="margin-top:14px">${D.docketNext.slice(0, 4).map(k => `<a class="ev-row" href="#/docket#dk-${esc(k.id)}"><div class="d"><span>${esc(k.next.d.length === 10 ? fmtDate(k.next.d, { year: false }).toUpperCase() : fmtDate(k.next.d).toUpperCase())}</span></div><div><div class="t">${esc(k.next.t)}</div><div class="w">${esc(k.title)}</div></div></a>`).join('')}</div>
        </div>
      </div>
    </section>

    ${D.news.items && D.news.items.length ? `<section class="sec">
      <div class="sec-h">In the news <a class="src act" href="#/news">All news →</a></div>
      <div class="news-grid">${stories().slice(0, 8).map(s => storyHTML(s)).join('')}</div>
      <p class="dim" style="font-size:12.5px;margin-top:12px">${esc(newsNote())}</p>
    </section>` : ''}

    <section class="sec">
      <div class="sec-h">Every project · open a case file <a class="src act" href="#/projects">All projects →</a></div>
      <div class="pcards">${D.projects.map(projectCard).join('')}</div>
    </section>
  </div>`;

  mountMap(main.querySelector('#fpMap'), { mode: 'front', scrubber: true, autoplay: true, layerPills: true,
    note: 'Markers are approximate (town or road level). Lines are illustrative corridors; Valley Link has no approved route. Click a county for its sheet.' });

  const renderNear = () => {
    const name = main.querySelector('#nearCounty').value;
    store.set('county', name);
    const c = D.counties.find(x => x.name === name);
    const end = toDate(T); end.setDate(end.getDate() + 14);
    const evs = D.upcoming.filter(e => e.date <= ymd(end) && (e.county === name || e.county === 'Statewide'));
    main.querySelector('#nearList').innerHTML = `
      ${evs.length ? evs.map(eventRow).join('') : `<p class="empty">No dated events in ${esc(name)} County in the next two weeks.</p>`}
      ${c.standing.map(s => `<div class="ev-row"><div class="d"><span>↻</span></div><div><div class="t">${esc(s.body)}</div><div class="w">${esc(s.rule)} · ${esc(s.where)}</div></div></div>`).join('')}
      <p style="margin-top:12px"><a class="btn" href="#/county/${esc(c.slug)}">${esc(name)} County sheet →</a></p>`;
  };
  main.querySelector('#nearCounty').addEventListener('change', renderNear);
  renderNear();
  return 'West Virginia AI Watch';
}
