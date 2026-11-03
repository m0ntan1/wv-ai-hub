import { D } from '../data.js';
import { esc, toDate, ymd, MONTHS, DOW, EV_TYPES, store, icsDownload, canIcs } from '../lib.js';
import { eventCard, standingCard, wireIcs } from '../parts.js';

export function calendar(main, q) {
  const cx = { view: store.get('calview') === 'month' ? 'month' : 'agenda', type: 'all', county: q.get('county') || 'all', project: q.get('project') || 'all', showPast: false, sel: null };
  // Public dates plus the Money Desk's dated company catalysts.
  const EV = [...D.events, ...(D.catEvents || [])].sort((a, b) => ((a.date || '9999') + (a.start || '')) < ((b.date || '9999') + (b.start || '')) ? -1 : 1);
  const t = toDate(D.today); cx.month = new Date(t.getFullYear(), t.getMonth(), 1, 12);
  const counts = {}; EV.forEach(e => { counts[e.type] = (counts[e.type] || 0) + 1; });
  const counties = [...new Set([...D.events.map(e => e.county), ...D.standing.map(s => s.county)].filter(Boolean))].sort((a, b) => a === 'Statewide' ? -1 : b === 'Statewide' ? 1 : a.localeCompare(b));
  const pids = [...new Set([...D.events.map(e => e.project), ...D.standing.flatMap(s => s.projects)].filter(Boolean))].sort((a, b) => D.projName(a).localeCompare(D.projName(b)));

  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Calendar · All times Eastern</div>
      <h1 class="page-h">Meetings, hearings, <em>protests</em> &amp; town halls</h1>
      <p class="lede">Every public date in West Virginia's data center and grid fights, plus the standing county meetings where residents can speak. Past events archive themselves. Developer open houses are labeled; they are not official hearings.</p>
    </header>
    <div class="cx-toolbar">
      <div class="toggle" role="group" aria-label="Calendar view"><button type="button" data-view="agenda" aria-pressed="${cx.view === 'agenda'}">Agenda</button><button type="button" data-view="month" aria-pressed="${cx.view === 'month'}">Month</button></div>
      <label>County <select id="cxCounty"><option value="all">All counties</option>${counties.map(c => `<option value="${esc(c)}"${c === cx.county ? ' selected' : ''}>${esc(c === 'Statewide' ? c : c + ' Co.')}</option>`).join('')}</select></label>
      <label>Project <select id="cxProject"><option value="all">All projects</option>${pids.map(p => `<option value="${p}"${p === cx.project ? ' selected' : ''}>${esc(D.projName(p))}</option>`).join('')}</select></label>
      <label><input type="checkbox" id="cxPast"> Show past</label>
      <span style="flex:1"></span>
      <a class="btn" href="calendar.ics" title="Subscribe in Google, Apple, or Outlook calendar with this link">Subscribe (.ics)</a>
      <button type="button" class="btn" id="cxIcsAll">Download upcoming</button>
    </div>
    <div class="pills" id="cxTypes" role="group" aria-label="Filter by event type">
      <button type="button" class="pill" data-t="all" aria-pressed="true">All types · ${EV.length}</button>
      ${Object.keys(EV_TYPES).filter(k => counts[k]).map(k => `<button type="button" class="pill" data-t="${k}" aria-pressed="false"><i style="background:${EV_TYPES[k].color}"></i>${EV_TYPES[k].label} · ${counts[k]}</button>`).join('')}
    </div>
    <div id="cxBody"></div>
    <section class="sec">
      <div class="sec-h">Standing public meetings</div>
      <p class="dim" style="font-size:14px;max-width:820px">Regular county commission, city council, and development authority meetings in every county with a mapped project. Most include public comment. Schedules are as each body publishes them, so confirm the agenda before you go.</p>
      <div class="cx-st-grid" id="cxStanding"></div>
    </section>
  </div>`;

  const match = e => (cx.type === 'all' || e.type === cx.type) && (cx.county === 'all' || e.county === cx.county) && (cx.project === 'all' || e.project === cx.project);
  const monthLabel = k => MONTHS[+k.slice(5, 7) - 1] + ' ' + k.slice(0, 4);
  const group = evs => { const g = new Map(); evs.forEach(e => { const k = e.date.slice(0, 7); if (!g.has(k)) g.set(k, []); g.get(k).push(e); }); return g; };
  function agenda() {
    const evs = EV.filter(match);
    const up = evs.filter(e => e.date && !e.tbd && !D.isPast(e)), tbd = evs.filter(e => e.tbd), past = evs.filter(D.isPast).reverse();
    let h = '';
    group(up).forEach((list, k) => { h += `<div class="cx-group"><div class="cx-group-h">${monthLabel(k)}<span>${list.length} event${list.length > 1 ? 's' : ''}</span></div>${list.map(eventCard).join('')}</div>`; });
    if (!up.length) h += '<p class="empty">No upcoming events match these filters.</p>';
    if (tbd.length) h += `<div class="cx-group"><div class="cx-group-h">Pending · date TBD<span>${tbd.length}</span></div>${tbd.map(eventCard).join('')}</div>`;
    if (cx.showPast) group(past).forEach((list, k) => { h += `<div class="cx-group"><div class="cx-group-h">Past · ${monthLabel(k)}<span>${list.length}</span></div>${list.map(eventCard).join('')}</div>`; });
    return h;
  }
  function month() {
    const m = cx.month, y = m.getFullYear(), mo = m.getMonth();
    const first = new Date(y, mo, 1, 12), start = new Date(first); start.setDate(1 - first.getDay());
    const dated = EV.filter(e => e.date && !e.tbd && !e.approx && match(e));
    const on = d => dated.filter(e => e.date <= d && d <= (e.end || e.date));
    let cells = DOW.map(d => `<div class="cx-dow">${d}</div>`).join('');
    for (let i = 0; i < 42; i++) {
      const d = new Date(start); d.setDate(start.getDate() + i);
      const k = ymd(d), list = on(k), inM = d.getMonth() === mo;
      if (i >= 35 && !inM && d.getDay() === 0) break;
      const cls = ['cx-day', inM ? '' : 'out', list.length ? 'has' : '', k === D.today ? 'today' : '', k === cx.sel ? 'sel' : ''].filter(Boolean).join(' ');
      cells += `<button type="button" class="${cls}" data-day="${k}" aria-label="${MONTHS[d.getMonth()]} ${d.getDate()}${list.length ? ', ' + list.length + ' event' + (list.length > 1 ? 's' : '') : ''}"${list.length ? '' : ' tabindex="-1"'}>
        <span class="n">${d.getDate()}</span>
        ${list.length ? `<span class="cx-dots">${list.slice(0, 4).map(e => `<i style="background:${EV_TYPES[e.type].color}"></i>`).join('')}</span>` : ''}
        ${list.slice(0, 2).map(e => `<span class="cx-chip" style="--ev:${EV_TYPES[e.type].color}">${esc(e.title)}</span>`).join('')}${list.length > 2 ? `<span class="mono" style="font-size:10px;color:var(--fg-3)">+${list.length - 2} more</span>` : ''}
      </button>`;
    }
    const sel = cx.sel ? on(cx.sel) : [];
    return `<div class="cx-mhead"><button type="button" class="cx-nav" data-nav="-1" aria-label="Previous month">←</button><h3>${MONTHS[mo]} ${y}</h3><button type="button" class="cx-nav" data-nav="1" aria-label="Next month">→</button></div>
      <div class="cx-grid">${cells}</div>
      <p class="dim" style="font-size:12.5px;margin-top:10px">Select a day to list its events. Items without an exact date appear in Agenda view.</p>
      <div id="cxDay">${cx.sel ? (sel.length ? `<div class="cx-group"><div class="cx-group-h">${MONTHS[toDate(cx.sel).getMonth()]} ${toDate(cx.sel).getDate()}</div>${sel.map(eventCard).join('')}</div>` : '<p class="empty">No events that day.</p>') : ''}</div>`;
  }
  function render() {
    main.querySelector('#cxBody').innerHTML = cx.view === 'month' ? month() : agenda();
    const st = D.standing.filter(s => (cx.county === 'all' || s.county === cx.county) && (cx.project === 'all' || s.projects.includes(cx.project)));
    main.querySelector('#cxStanding').innerHTML = st.length ? st.map(standingCard).join('') : '<p class="empty">No standing meetings match these filters.</p>';
  }
  main.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => { cx.view = b.dataset.view; store.set('calview', cx.view); main.querySelectorAll('[data-view]').forEach(x => x.setAttribute('aria-pressed', x === b)); render(); }));
  main.querySelector('#cxTypes').addEventListener('click', ev => { const b = ev.target.closest('[data-t]'); if (!b) return; cx.type = b.dataset.t; main.querySelectorAll('[data-t]').forEach(x => x.setAttribute('aria-pressed', x === b)); render(); });
  main.querySelector('#cxCounty').addEventListener('change', ev => { cx.county = ev.target.value; render(); });
  main.querySelector('#cxProject').addEventListener('change', ev => { cx.project = ev.target.value; render(); });
  main.querySelector('#cxPast').addEventListener('change', ev => { cx.showPast = ev.target.checked; render(); });
  main.querySelector('#cxIcsAll').addEventListener('click', () => { const evs = EV.filter(e => canIcs(e) && !D.isPast(e) && match(e)); if (evs.length) icsDownload(evs, 'wv-ai-watch-upcoming.ics'); });
  main.querySelector('#cxBody').addEventListener('click', ev => {
    const nav = ev.target.closest('[data-nav]');
    if (nav) { cx.month = new Date(cx.month.getFullYear(), cx.month.getMonth() + Number(nav.dataset.nav), 1, 12); cx.sel = null; render(); return; }
    const day = ev.target.closest('.cx-day.has');
    if (day) { cx.sel = day.dataset.day; render(); main.querySelector('#cxDay')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
  });
  wireIcs(main, icsDownload);
  if (EV.some(e => e.date === D.today)) cx.sel = D.today;
  render();
  const focusId = q.get('e');
  if (focusId) {
    const e = EV.find(x => x.id === focusId);
    if (e && D.isPast(e)) { cx.showPast = true; main.querySelector('#cxPast').checked = true; render(); }
    setTimeout(() => { const el = main.querySelector('#ev-' + CSS.escape(focusId)); if (el) { el.scrollIntoView({ block: 'center' }); el.style.outline = '2px solid var(--signal)'; el.style.outlineOffset = '6px'; } }, 60);
  }
  return 'Calendar';
}
