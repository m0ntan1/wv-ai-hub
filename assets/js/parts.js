// Reusable pieces of markup shared by several views.
import { D } from './data.js';
import { esc, toDate, fmtDate, timeRange, DOW, MON, EV_TYPES, STATUS, statusColor, toneVar, stamp, vfy, srcLink, srcLinks, rx, countdown, canIcs, countyHref, projectHref, BODIES, plural } from './lib.js';

// ---------------------------------------------------------------- countdown chips
/** Next few things to show up for, grouped so a run of open houses is one chip. */
export function countdownItems(limit = 5) {
  const items = [];
  const up = D.upcoming.filter(e => !e.approx);
  for (let i = 0; i < up.length && items.length < limit - 1; i++) {
    const e = up[i];
    const series = e.title.split(':')[0];
    const sameDay = up.filter(x => x.date === e.date && x.title.split(':')[0] === series && x.title.includes(':'));
    if (sameDay.length > 1 || (e.type === 'developer' && e.title.includes(':'))) {
      const all = up.filter(x => x.title.split(':')[0] === series);
      const names = sameDay.map(x => x.title.split(':')[1].trim());
      if (items.some(it => it.series === series)) continue;
      items.push({ d: e.date, series, what: `${series}s: ${names.join(' & ')}`, when: `${DOW[toDate(e.date).getDay()]} ${fmtDate(e.date, { year: false })}${all.length > sameDay.length ? ' · then ' + (all.length - sameDay.length) + ' more' : ''}`, href: '#/calendar', tone: 'alarm', verify: e.flag });
      continue;
    }
    if (items.some(it => it.title === e.title)) continue;
    items.push({ d: e.date, title: e.title, what: e.title, when: `${DOW[toDate(e.date).getDay()]} ${fmtDate(e.date, { year: e.date.slice(0, 4) !== D.today.slice(0, 4) })}${e.county && e.county !== 'Statewide' ? ' · ' + e.county + ' Co.' : ''}`, href: '#/calendar?e=' + e.id, tone: EV_TONE[e.type] || 'cyan', verify: e.flag });
  }
  // The anchor chip: the next big decision on the docket.
  const big = D.docketNext.find(k => (k.stage === 'briefing' || k.stage === 'awaiting') && k.next.d.length === 10);
  if (big && !items.some(it => it.d === big.next.d)) items.push({ d: big.next.d, what: `${big.next.t}: ${big.title.split('(')[0].trim()}`, when: `${fmtDate(big.next.d)} · ${big.case}`, href: '#/docket', tone: 'grid', verify: big.next.verify ? big.verify : null });
  return items.slice(0, limit);
}
const EV_TONE = { hearing: 'signal', psc: 'ok', court: 'legal', legislature: 'legal', protest: 'alarm', community: 'cyan', government: 'cyan', developer: 'dim' };
export function chipsHTML(items) {
  return items.map(it => {
    const days = D.daysTo(it.d), c = countdown(days), hot = days <= 2;
    const w = Math.max(6, Math.min(100, 100 - days / 1.8));
    return `<a class="chip${hot ? ' hot' : ''}" href="${it.href}" style="--c:${toneVar(hot ? 'alarm' : it.tone)};--w:${w}%">
      <span class="cd">${c.n}<small>${c.u}</small></span>
      <span class="what">${esc(it.what)} ${vfy(it.verify)}</span>
      <span class="when">${esc(it.when)}</span></a>`;
  }).join('');
}

// ---------------------------------------------------------------- events
export function dateBlock(e) {
  if (e.tbd) return '<span class="d sm">TBD</span>';
  if (e.label) return `<span class="d sm">${esc(e.label)}</span>`;
  const a = toDate(e.date);
  if (!e.end) return `<span class="d">${a.getDate()}</span><span class="w">${DOW[a.getDay()]}</span>`;
  const b = toDate(e.end);
  if (a.getMonth() === b.getMonth()) return `<span class="d sm">${a.getDate()}–${b.getDate()}</span><span class="w">${DOW[a.getDay()]}–${DOW[b.getDay()]}</span>`;
  return `<span class="d sm">${MON[a.getMonth()]} ${a.getDate()}–${MON[b.getMonth()]} ${b.getDate()}</span>`;
}
export function eventCard(e) {
  const t = EV_TYPES[e.type] || EV_TYPES.government;
  const where = [e.venue, e.address].filter(Boolean).join(', ');
  const tr = timeRange(e), past = D.isPast(e);
  return `<article class="cx-ev${past ? ' past' : ''}" id="ev-${esc(e.id)}" style="--ev:${t.color}">
    <div class="cx-date">${dateBlock(e)}</div>
    <div>
      <div class="cx-meta"><span class="cx-type">${t.label}</span>${tr ? '<span>' + tr + '</span>' : ''}${e.county ? `<span>${e.county === 'Statewide' ? 'Statewide' : `<a href="${countyHref(e.county)}" style="color:inherit">${esc(e.county)} Co.</a>`}</span>` : ''}${vfy(e.flag)}</div>
      <h3 class="cx-title">${esc(e.title)}</h3>
      ${e.desc ? `<p class="cx-desc">${esc(e.desc)}</p>` : ''}
      ${where ? `<p class="cx-line"><b>Where</b>${esc(where)}</p>` : ''}
      ${e.virtual ? `<p class="cx-line"><b>Online</b>${esc(e.virtual)}</p>` : ''}
      ${e.host ? `<p class="cx-line"><b>Host</b>${esc(e.host)}</p>` : ''}
      ${e.how ? `<p class="cx-line"><b>Take part</b>${esc(e.how)}</p>` : ''}
      ${e.flag ? `<p class="cx-line"><b>Note</b>${esc(e.flag)}</p>` : ''}
      <div class="cx-links">
        ${e.project ? `<a href="${D.projLink(e.project)}">${esc(D.projName(e.project))} →</a>` : ''}
        ${e.company && D.coById[e.company] ? `<a href="#/company/${esc(e.company)}">${esc(D.coById[e.company].name)} on the Money tab →</a>` : ''}
        ${(e.sources || []).map(s => srcLink(s)).join('')}
        ${canIcs(e) && !past ? `<button type="button" class="cx-ics" data-ics="${esc(e.id)}">+ Add to calendar</button>` : ''}
      </div>
    </div>
  </article>`;
}
export function eventRow(e) {
  const d = toDate(e.date);
  return `<a class="ev-row" href="#/calendar?e=${esc(e.id)}">
    <div class="d">${e.tbd || !e.date ? '<span>TBD</span><b>·</b>' : `<span>${DOW[d.getDay()].toUpperCase()}</span><b>${d.getDate()}</b><span style="color:var(--fg-3)">${MON[d.getMonth()].toUpperCase()}</span>`}</div>
    <div><div class="t">${esc(e.title)} ${vfy(e.flag)}</div><div class="w">${esc([timeRange(e), e.venue, e.county && e.county !== 'Statewide' ? e.county + ' Co.' : e.county].filter(Boolean).join(' · '))}</div></div></a>`;
}
export function standingCard(s) {
  return `<div class="card cx-st">
    <h4>${esc(s.body)}</h4><div class="c"><a href="${countyHref(s.county)}" style="color:inherit">${esc(s.county)} Co.</a> · ${s.projects.map(id => `<a href="${D.projLink(id)}" style="color:inherit">${esc(D.projName(id))}</a>`).join(', ')}</div>
    <p><b>When</b>${esc(s.rule)}</p><p><b>Where</b>${esc(s.where)}</p>
    ${s.next ? `<p><b>Next posted</b>${esc(s.next)}</p>` : ''}
    ${s.note ? `<p>${esc(s.note)}</p>` : ''}
    ${s.verify ? `<p>${vfy(s.verify)} ${esc(s.verify)}</p>` : ''}
    <div class="srcs"><a class="src" href="${esc(s.url)}" target="_blank" rel="noopener">Agendas &amp; notices ↗</a></div></div>`;
}
/** Wire .ics buttons inside a container. */
export function wireIcs(root, icsDownload) {
  root.addEventListener('click', ev => {
    const b = ev.target.closest('[data-ics]'); if (!b) return;
    const e = D.events.find(x => x.id === b.dataset.ics); if (e) icsDownload([e], 'wv-ai-watch-' + e.id + '.ics');
  });
}

// ---------------------------------------------------------------- docket + projects
export function docketCard(k, { compact } = {}) {
  const tone = k.tone || 'dim';
  const next = k.next ? `<div class="nx">NEXT · ${esc(k.next.t)}${k.next.d ? ' · ' + esc(fmtDate(k.next.d)) + (k.next.d.length === 10 && k.next.d >= D.today ? ' (' + plural(D.daysTo(k.next.d), 'day') + ')' : '') : ' · date TBD'} ${k.next.verify ? vfy(k.verify) : ''}</div>` : '';
  return `<article class="dk" id="dk-${esc(k.id)}" style="--c:${toneVar(tone === 'dim' ? 'dim' : tone)}">
    <div class="no">${esc(BODIES[k.body])} · ${esc(k.case || k.where)}</div>
    <h3>${esc(k.title)}</h3>
    ${compact ? '' : `<div class="sum">${k.summary} ${k.verify && !k.next?.verify ? vfy(k.verify) : ''}</div>`}
    <div class="st">${stamp(k.stamp, tone)}</div>
    ${next}
    <div class="rel">${k.projects.filter(id => D.byId[id] || id === 'marl' || id === 'valleylink').map(id => `<a class="tag" href="${D.projLink(id)}">${esc(D.projName(id))}</a>`).join('')}${(k.counties || []).map(c => `<a class="tag" href="${countyHref(c)}">${esc(c)} Co.</a>`).join('')}</div>
    ${compact ? '' : srcLinks(k.sources)}
  </article>`;
}
export function projectCard(p) {
  const c = statusColor(p.status);
  return `<a class="pcard" href="${projectHref(p.id)}" style="--c:${c}">
    <span class="st">${esc(STATUS[p.status].label)}</span> ${vfy(p.verify)}
    <h3>${esc(p.short === 'Google' ? 'Google Buffalo' : p.name.length < 26 ? p.name : p.short)}</h3>
    <p>${esc(p.place)}</p></a>`;
}
export const statusStamp = (p, big) => stamp(STATUS[p.status].label, STATUS[p.status].tone === 'dim' ? 'dim' : STATUS[p.status].tone, big);
export { rx };
