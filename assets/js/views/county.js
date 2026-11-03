import { D } from '../data.js';
import { esc, fmtDate, timeRange, plural, srcLink, vfy, toDate, ymd } from '../lib.js';
import { mountMap } from '../map.js';
import { statusStamp } from '../parts.js';

export function counties(main) {
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Counties · printable field sheets</div>
      <h1 class="page-h">Pick your <em>county</em></h1>
      <p class="lede">Each sheet fits on one printed page: the projects, the standing meetings with times and addresses, upcoming dates, what to watch for, and a QR code back to the live case files. Bring it to the commission meeting.</p>
    </header>
    <section class="sec" style="display:grid;grid-template-columns:minmax(0,1fr);gap:24px">
      <div id="ctyMap"></div>
      <div class="cty-grid">${D.counties.map(c => {
        const nx = c.events.filter(e => e.date && !e.tbd && !D.isPast(e))[0];
        return `<a class="cty" href="#/county/${c.slug}"><span class="n">${[c.projects.length && plural(c.projects.length, 'project'), c.lines.length && plural(c.lines.length, 'line'), c.standing.length && plural(c.standing.length, 'standing meeting')].filter(Boolean).join(' · ') || 'dates on the calendar'}</span><h3>${esc(c.name)}</h3><p>${c.projects.map(id => esc(D.byId[id].short)).join(', ') || (c.lines.length ? c.lines.map(D.projName).join(', ') : 'Calendar events')}${nx ? `<br>Next: ${esc(nx.title)}, ${esc(fmtDate(nx.date, { year: false }))}` : ''}</p></a>`;
      }).join('')}</div>
    </section>
  </div>`;
  mountMap(main.querySelector('#ctyMap'), { mode: 'counties', layers: ['projects', 'names'], label: 'Counties with tracked projects, lines, meetings, or dates' });
  return 'Counties';
}

export function county(main, slugName) {
  const c = D.countyBySlug[slugName];
  if (!c) return null;
  const projs = c.projects.map(id => D.byId[id]);
  const lines = c.lines.map(id => D.lineById[id]);
  const certified = projs.filter(p => D.certified.includes(p));
  const end = toDate(D.today); end.setDate(end.getDate() + 75);
  const upcoming = D.upcoming.filter(e => e.county === c.name && e.date <= ymd(end));
  const tbd = D.events.filter(e => e.tbd && e.county === c.name);
  // One line per pending item: a project's own "next" step wins over the docket card and the TBD calendar entry for the same thing.
  const hasNext = new Set(projs.filter(p => p.timeline.some(t => t.next)).map(p => p.id));
  const watch = [
    ...projs.flatMap(p => p.timeline.filter(t => t.next).map(t => ({ t: `${p.short}: ${t.t}`, d: t.d, verify: t.verify }))),
    ...D.docket.filter(k => k.next && k.projects.some(id => (c.projects.includes(id) && !hasNext.has(id)) || c.lines.includes(id))).map(k => ({ t: `${k.next.t}: ${k.title}`, d: k.next.d, verify: k.next.verify ? k.verify : null })),
    ...tbd.filter(e => !hasNext.has(e.project)).map(e => ({ t: e.title, d: '', verify: e.flag })),
  ].filter((w, i, a) => a.findIndex(x => x.t === w.t) === i);
  const ids = new Set([...c.projects, ...c.lines]);
  const who = D.people.filter(x => x.projects.some(id => ids.has(id)) && x.group !== 'State Government').slice(0, 10);
  const url = `wvaihub.com/#/county/${c.slug}`;

  main.innerHTML = `<div class="wrap">
    <div class="crumb"><a href="#/counties">Counties</a> / ${esc(c.name)}</div>
    <div class="sheet-tools no-print">
      <button type="button" class="btn pri" id="printBtn">⎙ Print this sheet</button>
      <span class="dim" style="font-size:13px">Prints on one letter-size page in the light newsprint style.</span>
    </div>
    <article class="sheet sh">
      <div class="sh-top">
        <div><div class="kicker">WV AI Watch · County field sheet</div><h1 class="sh-title">${esc(c.name)} <em>County</em></h1></div>
        <div><div class="qr"><img src="assets/qr/${c.slug}.svg" alt="QR code linking to ${esc(url)}" onerror="this.parentNode.style.display='none'"></div><div class="qr-cap">${esc(url)}</div></div>
      </div>
      <div class="sh-strip"><span>Printed ${esc(fmtDate(D.today))}</span><span>Data checked ${esc(fmtDate(D.meta.updated))}</span>${projs.length ? `<span>${plural(projs.length, 'project')}</span>` : ''}${certified.length ? `<span>${certified.length} state-certified</span><span>County zoning preempted (HB 2014)</span>` : ''}${lines.length ? `<span>${lines.map(l => esc(l.short)).join(' · ')}</span>` : ''}</div>
      <div class="sh-cols">
        <div>
          ${projs.length ? `<h3 style="margin-top:20px">Projects in the county</h3>${projs.map(p => `<div class="sh-proj">
            <h4><a href="#/project/${p.id}">${esc(p.name)}</a> ${statusStamp(p)}</h4>
            <p><b>${esc(p.developer.split('.')[0])}.</b> ${esc(p.place)}. ${vfy(p.verify)}</p>
            ${p.facts.slice(0, 2).map(f => `<p><b>${esc(f.k)}:</b> ${esc(f.v)} ${vfy(f.verify)}</p>`).join('')}
            <p><b>Latest (${esc(p.latest.d)}):</b> ${esc(p.latest.t)}</p></div>`).join('')}` : ''}
          ${lines.length ? `<h3 style="margin-top:20px">Transmission lines</h3>${lines.map(l => `<div class="sh-proj"><h4>${esc(l.name)}</h4><p>${esc(l.note)}</p></div>`).join('')}` : ''}
          ${!projs.length && !lines.length ? '<h3 style="margin-top:20px">On the record</h3><p class="dim">No mapped project here. This county is on the calendar for the dates listed on this sheet.</p>' : ''}
          ${who.length ? `<h3 style="margin-top:6px">Who to know</h3><p style="font-size:13px;line-height:1.55">${who.map(x => `<b>${esc(x.name)}</b> <span class="dim">${esc(x.role.replace(/<[^>]+>/g, '').replace(/\s*\.$/, ''))}</span>`).join(' · ')}</p>` : ''}
        </div>
        <div>
          <div class="sh-box" style="margin-top:20px">
            <h5>Where to show up</h5>
            ${c.standing.length ? c.standing.map(s => `<div class="sh-meet"><div class="sh-big">${esc(s.body)}</div><p style="margin-top:4px"><b>${esc(s.rule)}</b><br>${esc(s.where)}${s.next ? `<br>Next posted: ${esc(s.next)}` : ''} ${vfy(s.verify)}</p></div>`).join('') : '<p>No standing meeting tracked for this county. Check the county commission\'s website.</p>'}
          </div>
          <div class="sh-box">
            <h5>Upcoming dates</h5>
            ${upcoming.length ? `<ul>${upcoming.map(e => `<li><b>${esc(fmtDate(e.date, { year: false }))}${e.start ? ', ' + esc(timeRange(e)) : ''}</b>: ${esc(e.title)}${e.venue ? '. ' + esc(e.venue) : ''} ${vfy(e.flag)}</li>`).join('')}</ul>` : '<p>No dated events in the next 75 days.</p>'}
          </div>
          ${watch.length ? `<div class="sh-box"><h5>Watch for</h5><ul>${watch.map(w => `<li>${esc(w.t)}${w.d ? ` (${esc(fmtDate(w.d))})` : ''} ${vfy(w.verify)}</li>`).join('')}</ul></div>` : ''}
          <div class="sh-box dash"><h5>Know the law</h5><p><b>HB 2014 (2025)</b> lets certified data centers skip county zoning and sends 30% of their property tax to the host county. <b>HB 4983 (2026)</b> keeps certification petitions confidential.</p></div>
          <p class="mono" style="font-size:10.5px;line-height:1.5">Every line on this sheet is sourced at wvaihub.com/#/receipts. Items marked ⚠ VERIFY could not be confirmed against their source.</p>
        </div>
      </div>
      <div class="sh-foot"><span>WV AI Watch · Montani Semper Liberi</span><span>Curated by MØNTAN1.com</span></div>
    </article>
    <section class="sec no-print"><div id="ctyLoc" style="max-width:520px"></div></section>
  </div>`;
  main.querySelector('#printBtn').addEventListener('click', () => window.print());
  mountMap(main.querySelector('#ctyLoc'), { mode: 'counties', county: c.name, layers: ['projects', 'lines'], label: `${c.name} County on the map` });
  return c.name + ' County';
}
