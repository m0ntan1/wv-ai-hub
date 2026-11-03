// WV AI Watch: boot, router, header controls.
import { loadData, D } from './data.js';
import { esc, fmtDate, store, $, $$ } from './lib.js';
import { front } from './views/front.js';
import { project } from './views/project.js';
import { docket } from './views/docket.js';
import { calendar } from './views/calendar.js';
import { people } from './views/people.js';
import { counties, county } from './views/county.js';
import { projectsIndex, mapPage, hubs, receipts, notFound } from './views/misc.js';
import { contact } from './views/contact.js';

const NAV = [['', 'Front'], ['map', 'Map'], ['projects', 'Projects'], ['docket', 'Docket'], ['calendar', 'Calendar'], ['people', 'People'], ['counties', 'Counties'], ['hubs', 'Hubs'], ['receipts', 'Receipts']];
// Old single-page anchors keep working.
const LEGACY = { projects: 'projects', docket: 'docket', calendar: 'calendar', people: 'people', hero: '', watch: 'map' };

function parse() {
  let h = decodeURIComponent(location.hash.replace(/^#/, ''));
  if (!h.startsWith('/')) {
    if (h.startsWith('proj-')) return { redirect: '#/project/' + h.slice(5) };
    if (h.startsWith('sec-')) return { redirect: '#/hubs' };
    if (h in LEGACY) return { redirect: '#/' + LEGACY[h] };
    if (h) return { redirect: '#/' };
    h = '/';
  }
  const [path, qs] = h.split('?');
  const parts = path.split('/').filter(Boolean);
  return { parts, q: new URLSearchParams(qs || '') };
}

function render() {
  const r = parse();
  if (r.redirect) { history.replaceState(null, '', r.redirect); return render(); }
  const [a = '', b] = r.parts;
  const main = $('#app');
  let title;
  window.scrollTo(0, 0);
  switch (a) {
    case '': title = front(main); break;
    case 'map': title = mapPage(main); break;
    case 'projects': title = projectsIndex(main); break;
    case 'project': title = project(main, b); break;
    case 'docket': title = docket(main, r.q); break;
    case 'calendar': title = calendar(main, r.q); break;
    case 'people': title = people(main, r.q); break;
    case 'counties': title = counties(main); break;
    case 'county': title = county(main, b); break;
    case 'hubs': title = hubs(main); break;
    case 'receipts': title = receipts(main, r.q); break;
    case 'contact': title = contact(main, r.q); break;
  }
  if (!title) title = notFound(main);
  document.title = title === 'West Virginia AI Watch' ? 'West Virginia AI Watch: Data Centers, PSC Filings, Lawsuits, and Hearings Mapped' : `${title} · WV AI Watch`;
  const cur = a === 'project' ? 'projects' : a === 'county' ? 'counties' : a;
  $$('[data-nav]').forEach(x => x.toggleAttribute('aria-current', false));
  $$(`[data-nav="${cur}"]`).forEach(x => x.setAttribute('aria-current', 'page'));
  $('#drawer').classList.remove('open');
  $('#menuBtn').setAttribute('aria-expanded', 'false');
  // In-page anchors like #/docket#dk-marl
  const anchor = location.hash.split('#')[2];
  if (anchor) setTimeout(() => document.getElementById(anchor)?.scrollIntoView({ block: 'center' }), 60);
  main.focus({ preventScroll: true });
}

function header() {
  const links = NAV.map(([k, l]) => `<a href="#/${k}" data-nav="${k}">${l}</a>`).join('');
  $('#nav').innerHTML = links;
  $('#drawerLinks').innerHTML = links;
  const theme = store.get('theme') === 'news' ? 'news' : 'ink';
  const rxOn = store.get('receipts') === '1';
  setTheme(theme); setReceipts(rxOn);
  document.addEventListener('click', ev => {
    const t = ev.target.closest('[data-theme-set]'); if (t) setTheme(t.dataset.themeSet);
    const x = ev.target.closest('[data-rx-set]'); if (x) setReceipts(x.dataset.rxSet === '1');
  });
  $('#menuBtn').addEventListener('click', () => { const o = $('#drawer').classList.toggle('open'); $('#menuBtn').setAttribute('aria-expanded', o); });
  // Ticker from the desk log (duplicated for a seamless loop).
  const items = D.desk.map(x => `<a class="item" href="${x.project && D.byId[x.project] ? '#/project/' + x.project : '#/'}"><b>${esc(fmtDate(x.d, { year: false }).toUpperCase())}</b>${esc(x.t)}</a>`).join('');
  $('#ticker').innerHTML = `<span class="live">LATEST</span><div class="lane"><div class="run">${items}${items}</div></div>`;
  $('#updated').textContent = fmtDate(D.meta.updated);
}
function setTheme(t) {
  document.documentElement.dataset.theme = t; store.set('theme', t);
  $$('[data-theme-set]').forEach(b => b.setAttribute('aria-pressed', b.dataset.themeSet === t));
  document.querySelector('meta[name=theme-color]').setAttribute('content', t === 'news' ? '#F3EFE6' : '#0B0D10');
}
function setReceipts(on) {
  document.body.classList.toggle('receipts', on); store.set('receipts', on ? '1' : '0');
  $$('[data-rx-set]').forEach(b => b.setAttribute('aria-pressed', (b.dataset.rxSet === '1') === on));
}

loadData().then(() => {
  header();
  window.addEventListener('hashchange', render);
  render();
}).catch(err => {
  console.error(err);
  $('#app').innerHTML = `<div class="wrap loading">Could not load the site data (${esc(err.message)}). If you opened this file directly, serve the folder over HTTP instead, for example: <code>python3 -m http.server</code>.</div>`;
});
