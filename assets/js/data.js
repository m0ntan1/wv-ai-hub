// Loads /data/*.json once and builds the lookups every view uses.
import { today, toDate, daysBetween, slug } from './lib.js';

const FILES = ['meta', 'projects', 'lines', 'docket', 'events', 'standing', 'people', 'network', 'hubs', 'desk', 'receipts', 'geo'];
export const D = {};

export async function loadData() {
  const v = document.documentElement.dataset.v || '';
  // News is optional (a fork may not have run the collector yet), so it never blocks the site.
  const newsP = fetch(`data/news.json${v ? '?v=' + v : ''}`).then(r => r.ok ? r.json() : { items: [] }).catch(() => ({ items: [] }));
  const got = await Promise.all(FILES.map(f => fetch(`data/${f}.json${v ? '?v=' + v : ''}`).then(r => {
    if (!r.ok) throw new Error(`data/${f}.json: HTTP ${r.status}`);
    return r.json();
  })));
  FILES.forEach((f, i) => { D[f] = got[i]; });
  D.news = await newsP;
  derive();
  return D;
}

function derive() {
  const T = today();
  D.today = T;
  D.byId = Object.fromEntries(D.projects.map(p => [p.id, p]));
  D.lineById = Object.fromEntries(D.lines.map(l => [l.id, l]));
  D.extraNames = { marl: 'MARL 500 kV line', valleylink: 'Valley Link 765 kV line', hb2014: 'Statewide / HB 2014' };
  D.projName = id => D.byId[id]?.short || D.extraNames[id] || id;
  D.projLink = id => D.byId[id] ? '#/project/' + id : id === 'marl' || id === 'valleylink' ? '#/map' : '#/docket';

  // Events: past/upcoming relative to the viewer's date.
  D.isPast = e => !e.tbd && (e.end || e.date) < T;
  const key = e => (e.date || '9999') + (e.start || '00:00');
  D.events.sort((a, b) => key(a) < key(b) ? -1 : 1);
  D.upcoming = D.events.filter(e => e.date && !e.tbd && !D.isPast(e));

  // Counties: everything we can say something about.
  const cset = new Map();
  const add = (name, what) => { if (!name || name === 'Statewide') return; if (!cset.has(name)) cset.set(name, { name, slug: slug(name), projects: new Set(), standing: [], events: [], lines: new Set() }); what(cset.get(name)); };
  D.projects.forEach(p => p.counties.forEach(c => add(c, x => x.projects.add(p.id))));
  D.lines.forEach(l => (l.counties || []).forEach(c => add(c, x => x.lines.add(l.id))));
  D.standing.forEach(s => add(s.county, x => x.standing.push(s)));
  D.events.forEach(e => add(e.county, x => x.events.push(e)));
  D.counties = [...cset.values()].map(c => ({ ...c, projects: [...c.projects], lines: [...c.lines] })).sort((a, b) => a.name.localeCompare(b.name));
  D.countyBySlug = Object.fromEntries(D.counties.map(c => [c.slug, c]));

  // Certified = any project whose history or timeline shows a certification.
  D.certified = D.projects.filter(p => p.history.some(h => h.status === 'certified') || p.timeline.some(t => t.kind === 'certified'));

  // Receipts lookup: section|title -> row
  D.receiptFor = (sec, title) => D.receipts.rows.find(r => r.sec === sec && r.title.startsWith(title.slice(0, 60)));

  // Network adjacency
  D.net = { byId: Object.fromEntries(D.network.nodes.map(n => [n.id, n])) };

  // Next big decisions from the docket (dated `next`).
  D.docketNext = D.docket.filter(d => d.next && d.next.d && d.next.d >= T.slice(0, d.next.d.length)).sort((a, b) => a.next.d < b.next.d ? -1 : 1);
  D.daysTo = d => daysBetween(T, d);
  D.monthsTo = d => (toDate(d) - toDate(T)) / (86400000 * 30.4);
}
