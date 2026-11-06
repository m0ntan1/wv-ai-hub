// Shared helpers for WV AI Watch. No dependencies.

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
// Only http(s) links may reach an href. Data files are edited by people and by automated feeds, so this is the last gate.
export const safeUrl = u => { try { const p = new URL(String(u ?? ''), 'https://wvaihub.com/'); return (p.protocol === 'https:' || p.protocol === 'http:') ? String(u) : '#'; } catch (e) { return '#'; } };
// True when a URL's host is the domain or one of its subdomains. includes('sec.gov') would also accept https://evil.example/?sec.gov
export const hostIs = (u, domain) => { try { const h = new URL(String(u)).hostname.toLowerCase(); return h === domain || h.endsWith('.' + domain); } catch (e) { return false; } };
// Plain text of an HTML snippet. Parsed by the browser instead of a regex, which misses nested tags like <<b>script>.
export const plainText = s => new DOMParser().parseFromString(String(s ?? ''), 'text/html').body.textContent;
export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
export const slug = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export const store = {
  get(k) { try { return localStorage.getItem('wvaiwatch.' + k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem('wvaiwatch.' + k, v); } catch (e) { /* private mode: ignore */ } },
};

// ---------------------------------------------------------------- dates
export const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
export const MON = MONTHS.map(m => m.slice(0, 3));
export const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
export const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const pad = n => String(n).padStart(2, '0');
export const ymd = d => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
/** Today in the viewer's time zone. `?today=YYYY-MM-DD` overrides it (for testing and archiving). */
export function today() {
  try {
    const q = new URLSearchParams(location.search).get('today');
    if (q && /^\d{4}-\d{2}-\d{2}$/.test(q)) return q;
  } catch (e) { /* ignore */ }
  return ymd(new Date());
}
/** Parse 'YYYY', 'YYYY-MM' or 'YYYY-MM-DD' to a noon-local Date (the first of the period). */
export function toDate(s) {
  if (!s) return null;
  const [y, m = '01', d = '01'] = String(s).split('-');
  return new Date(+y, +m - 1, +d, 12);
}
export const precision = s => !s ? 0 : String(s).split('-').length; // 1 year, 2 month, 3 day
export function fmtDate(s, { year = true, short = true } = {}) {
  if (!s) return 'Date TBD';
  const p = precision(s), d = toDate(s), M = short ? MON : MONTHS;
  if (p === 1) return String(d.getFullYear());
  if (p === 2) return M[d.getMonth()] + (year ? ' ' + d.getFullYear() : '');
  return M[d.getMonth()] + ' ' + d.getDate() + (year ? ', ' + d.getFullYear() : '');
}
export const daysBetween = (a, b) => Math.round((toDate(b) - toDate(a)) / 86400000);
export function countdown(days) {
  if (days === 0) return { n: 'TODAY', u: '' };
  if (days === 1) return { n: '1', u: 'DAY' };
  return { n: String(days), u: 'DAYS' };
}
export function fmt12(t) {
  const [h, m] = t.split(':').map(Number);
  return { t: ((h % 12) || 12) + ':' + pad(m), ap: h < 12 ? 'a.m.' : 'p.m.' };
}
export function timeRange(e) {
  if (!e.start) return '';
  const a = fmt12(e.start);
  if (!e.endt) return a.t + ' ' + a.ap;
  const b = fmt12(e.endt);
  return a.ap === b.ap ? a.t + '–' + b.t + ' ' + b.ap : a.t + ' ' + a.ap + '–' + b.t + ' ' + b.ap;
}

// ---------------------------------------------------------------- vocab
export const STATUS = {
  construction: { label: 'Under construction', short: 'Construction', tone: 'alarm' },
  certified: { label: 'State-certified', short: 'Certified', tone: 'cyan' },
  contested: { label: 'Permitted · contested', short: 'Contested', tone: 'legal' },
  proposed: { label: 'Proposed', short: 'Proposed', tone: 'dim' },
  rumored: { label: 'Rumored', short: 'Rumored', tone: 'dim' },
  grid: { label: 'Power plant', short: 'Power', tone: 'gas' },
};
export const STATUS_ORDER = ['construction', 'certified', 'contested', 'proposed', 'rumored', 'grid'];
export const toneVar = t => ({ alarm: 'var(--alarm)', cyan: 'var(--cyan)', legal: 'var(--legal)', dim: 'var(--fg-2)', gas: 'var(--gas)', grid: 'var(--grid)', signal: 'var(--signal)', ok: 'var(--ok)' }[t] || 'var(--fg-2)');
export const statusColor = st => st === 'rumored' ? 'var(--fg-3)' : toneVar(STATUS[st]?.tone);

export const EV_TYPES = {
  hearing: { label: 'DEP hearing / comment', color: 'var(--signal)' },
  psc: { label: 'PSC', color: 'var(--ok)' },
  court: { label: 'Court', color: 'var(--legal)' },
  legislature: { label: 'Legislature', color: 'var(--grid)' },
  protest: { label: 'Protest / rally', color: 'var(--alarm)' },
  community: { label: 'Town hall / community', color: 'var(--cyan)' },
  government: { label: 'Government', color: 'var(--fg-2)' },
  developer: { label: 'Developer open house', color: 'var(--fg-3)' },
  money: { label: 'Money desk catalyst', color: 'var(--copper)' },
};
export const STAGES = [
  { id: 'prefiling', label: 'Not yet filed' },
  { id: 'open', label: 'Open · in progress' },
  { id: 'briefing', label: 'Briefing' },
  { id: 'awaiting', label: 'Awaiting decision' },
  { id: 'closed', label: 'Decided · in effect' },
];
export const BODIES = { courts: 'Courts', psc: 'PSC', dep: 'DEP', legislature: 'Legislature' };

// ---------------------------------------------------------------- bits of markup
export const vfy = note => note ? `<span class="vfy" title="${esc(note)}" tabindex="0">⚠ Verify</span>` : '';
export const stamp = (text, tone, big) => `<span class="stamp t-${esc(tone || 'dim')}${big ? ' big' : ''}">${esc(text)}</span>`;
export const srcLink = (s, extra = '') => `<a class="src" href="${esc(safeUrl(s.url))}" target="_blank" rel="noopener"${extra}>${esc(s.label)} ↗</a>`;
export const srcLinks = list => (list && list.length) ? `<div class="srcs">${list.map(s => srcLink(s)).join('')}</div>` : '';
export const hostOf = u => { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return u; } };
export const urlSrc = u => u ? { label: hostOf(u), url: u } : null;
/** Receipts-mode block: hidden unless body.receipts. */
export function rx(sources, { checked, note } = {}) {
  const list = (sources || []).filter(Boolean);
  if (!list.length && !note) return '';
  return `<div class="rx"><span class="mono">RECEIPTS${checked ? ' · checked ' + esc(fmtDate(checked)) : ''}</span>${note ? '<div>' + esc(note) + '</div>' : ''}${srcLinks(list)}</div>`;
}
export const plural = (n, one, many = one + 's') => n + ' ' + (n === 1 ? one : many);
export const countyHref = c => '#/county/' + slug(c);
export const projectHref = id => '#/project/' + id;

// ---------------------------------------------------------------- .ics
const VTZ = ['BEGIN:VTIMEZONE', 'TZID:America/New_York', 'BEGIN:DAYLIGHT', 'TZOFFSETFROM:-0500', 'TZOFFSETTO:-0400', 'TZNAME:EDT', 'DTSTART:19700308T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU', 'END:DAYLIGHT', 'BEGIN:STANDARD', 'TZOFFSETFROM:-0400', 'TZOFFSETTO:-0500', 'TZNAME:EST', 'DTSTART:19701101T020000', 'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU', 'END:STANDARD', 'END:VTIMEZONE'];
const icsEsc = s => String(s).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
const icsFold = line => { const out = []; while (line.length > 70) { out.push(line.slice(0, 70)); line = ' ' + line.slice(70); } out.push(line); return out.join('\r\n'); };
export const canIcs = e => e.date && !e.tbd && !e.approx;
export function icsEvent(e) {
  const d = e.date.replace(/-/g, '');
  const L = ['BEGIN:VEVENT', 'UID:' + e.id + '@wvaihub.com', 'DTSTAMP:' + new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '')];
  if (e.start) {
    let en = e.endt;
    if (!en) { const [h, m] = e.start.split(':').map(Number); en = pad(Math.min(h + 2, 23)) + ':' + pad(m); }
    L.push('DTSTART;TZID=America/New_York:' + d + 'T' + e.start.replace(':', '') + '00', 'DTEND;TZID=America/New_York:' + (e.end || e.date).replace(/-/g, '') + 'T' + en.replace(':', '') + '00');
  } else {
    const end = toDate(e.end || e.date); end.setDate(end.getDate() + 1);
    L.push('DTSTART;VALUE=DATE:' + d, 'DTEND;VALUE=DATE:' + ymd(end).replace(/-/g, ''));
  }
  L.push('SUMMARY:' + icsEsc(e.title));
  const loc = [e.venue, e.address, e.virtual].filter(Boolean).join(', ');
  if (loc) L.push('LOCATION:' + icsEsc(loc));
  const desc = [e.desc, e.how && 'How to take part: ' + e.how, e.flag && 'Note: ' + e.flag, ...(e.sources || []).map(s => s.label + ': ' + s.url), 'Via WV AI Watch: https://wvaihub.com/#/calendar'].filter(Boolean).join('\n');
  L.push('DESCRIPTION:' + icsEsc(desc));
  if (e.sources && e.sources[0]) L.push('URL:' + e.sources[0].url);
  L.push('END:VEVENT');
  return L.map(icsFold).join('\r\n');
}
export function icsDownload(evs, name) {
  const body = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//WV AI Watch//Calendar//EN', 'CALSCALE:GREGORIAN', 'X-WR-CALNAME:WV AI Watch', 'X-WR-TIMEZONE:America/New_York', ...VTZ].join('\r\n')
    + '\r\n' + evs.map(icsEvent).join('\r\n') + '\r\nEND:VCALENDAR\r\n';
  try {
    const url = URL.createObjectURL(new Blob([body], { type: 'text/calendar;charset=utf-8' }));
    const a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 500);
  } catch (err) { console.warn('ics export failed', err); }
}
