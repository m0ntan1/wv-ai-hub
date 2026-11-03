// Loads /data/*.json once and builds the lookups every view uses.
import { today, toDate, daysBetween, slug } from './lib.js';

const FILES = ['meta', 'projects', 'lines', 'docket', 'events', 'standing', 'people', 'network', 'hubs', 'desk', 'receipts', 'geo'];
export const D = {};

export async function loadData() {
  const v = document.documentElement.dataset.v || '';
  // News is optional (a fork may not have run the collector yet), so it never blocks the site.
  const opt = (f, empty) => fetch(`data/${f}.json${v ? '?v=' + v : ''}`).then(r => r.ok ? r.json() : empty).catch(() => empty);
  const newsP = opt('news', { items: [] });
  // The Money Desk roster and Rook's Reads are small and optional; the filings file is larger, so it loads on demand.
  const coP = opt('companies', { tranches: [], signals: [], secSearch: [], companies: [] });
  const readsP = opt('reads', { reads: [] });
  D.loadFilings = () => D.filingsP || (D.filingsP = opt('filings', { sec: {}, search: {}, fred: {} }).then(x => { D.filings = x; return x; }));
  const got = await Promise.all(FILES.map(f => fetch(`data/${f}.json${v ? '?v=' + v : ''}`).then(r => {
    if (!r.ok) throw new Error(`data/${f}.json: HTTP ${r.status}`);
    return r.json();
  })));
  FILES.forEach((f, i) => { D[f] = got[i]; });
  D.news = await newsP;
  D.companies = await coP;
  D.reads = ((await readsP).reads || []).filter(r => r.mercer && r.mercer.status === 'CLEARED').sort((x, y) => x.d < y.d ? 1 : -1);
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

  // Money Desk lookups
  D.coById = Object.fromEntries((D.companies.companies || []).map(c => [c.id, c]));

  // Network adjacency
  D.net = { byId: Object.fromEntries(D.network.nodes.map(n => [n.id, n])) };

  // Next big decisions from the docket (dated `next`).
  D.docketNext = D.docket.filter(d => d.next && d.next.d && d.next.d >= T.slice(0, d.next.d.length)).sort((a, b) => a.next.d < b.next.d ? -1 : 1);
  D.daysTo = d => daysBetween(T, d);

  // Money Desk catalysts: events or open questions that could move a company or its West Virginia projects.
  // Hand-curated ones come from companies.json; dated docket steps on a company's projects (or listed cases) are added.
  D.catalysts = [];
  (D.companies.companies || []).forEach(c => {
    (c.catalysts || []).forEach((x, i) => D.catalysts.push({ ...x, id: `cat-${c.id}-${i}`, cid: c.id, company: c.name, kind: 'company' }));
    D.docketNext.filter(k => k.projects.some(p => (c.projects || []).includes(p)) || (c.docket || []).includes(k.id))
      .forEach(k => D.catalysts.push({ id: `dk-${c.id}-${k.id}`, cid: c.id, company: c.name, kind: 'docket', dk: k.id, t: `${k.next.t}: ${k.title}`, d: k.next.d, src: k.sources[0], verify: k.next.verify ? k.verify : null }));
  });
  // Dated company catalysts also go on the calendar (kept apart from D.events so counts and "Take part" lists stay about public dates).
  D.catEvents = D.catalysts.filter(x => x.kind === 'company' && x.d && x.d.length === 10).map(x => ({
    id: x.id, type: 'money', title: `${x.company}: ${x.t}`, date: x.d, approx: !!x.approx, company: x.cid,
    desc: "A Money Desk catalyst: an event that could change this company's condition or a West Virginia project, for better or worse.",
    sources: [x.src], flag: x.verify || null }));
  D.monthsTo = d => (toDate(d) - toDate(T)) / (86400000 * 30.4);
}
