// Hubs: one news feed of West Virginia's AI-skills, research, business and energy stories (data/hubs.json),
// tagged by place and topic so it can be sorted and filtered. Filters live in the URL: #/hubs?topic=research&region=North+Central
import { D } from '../data.js';
import { esc, fmtDate, srcLinks } from '../lib.js';

const SORTS = [['new', 'Newest first'], ['old', 'Oldest first'], ['place', 'Place (A to Z)'], ['region', 'Region']];
const STATEWIDE = 'Statewide';

export function hubs(main, q = new URLSearchParams()) {
  const hubById = Object.fromEntries(D.hubs.map(h => [h.id, h]));
  const TOPICS = D.meta.hubTopics, TOPIC_LABEL = Object.fromEntries(TOPICS.map(t => [t.id, t.label]));
  const placeLabel = s => s.place === 'statewide' ? STATEWIDE : s.place ? (hubById[s.place].label || hubById[s.place].name) : s.county ? s.county + ' County' : STATEWIDE;
  const items = D.hubs.flatMap(h => h.stories.map((s, i) => ({ ...s, key: h.id + '-' + i, placeName: placeLabel(s) })));

  // ---- state, read from the URL
  const st = { q: q.get('q') || '', sort: SORTS.some(x => x[0] === q.get('sort')) ? q.get('sort') : 'new', topics: new Set((q.get('topic') || '').split(',').filter(t => TOPIC_LABEL[t])), kind: '', value: '' };
  for (const k of ['place', 'county', 'region']) if (q.get(k)) { st.kind = k; st.value = q.get(k); break; }

  const count = f => items.filter(f).length;
  const where = it => !st.kind ? true : st.kind === 'place' ? it.place === st.value : st.kind === 'county' ? it.county === st.value : it.region === st.value;
  const matches = it => {
    if (!where(it)) return false;
    if (st.topics.size && !it.topics.some(t => st.topics.has(t))) return false;
    if (st.q) {
      const hay = (it.title + ' ' + it.html.replace(/<[^>]+>/g, ' ') + ' ' + it.sources.map(s => s.label).join(' ') + ' ' + it.placeName + ' ' + (it.county || '') + ' ' + it.region).toLowerCase();
      if (!st.q.toLowerCase().split(/\s+/).filter(Boolean).every(w => hay.includes(w))) return false;
    }
    return true;
  };
  const byNew = (a, b) => !a.d !== !b.d ? (a.d ? -1 : 1) : (a.d === b.d ? a.title.localeCompare(b.title) : a.d < b.d ? 1 : -1);
  const byName = (x, y) => x === y ? 0 : x === STATEWIDE ? -1 : y === STATEWIDE ? 1 : x.localeCompare(y);
  const sorters = {
    new: byNew,
    old: (a, b) => !a.d !== !b.d ? (a.d ? -1 : 1) : (a.d === b.d ? a.title.localeCompare(b.title) : a.d < b.d ? -1 : 1),
    place: (a, b) => byName(a.placeName, b.placeName) || byNew(a, b),
    region: (a, b) => byName(a.region, b.region) || byName(a.placeName, b.placeName) || byNew(a, b),
  };

  // ---- the place menu: statewide, regions, cities, counties (with how many items each holds)
  const opt = (kind, value, label, n) => `<option value="${esc(kind + ':' + value)}"${st.kind === kind && st.value === value ? ' selected' : ''}>${esc(label)} (${n})</option>`;
  const regions = ['Statewide', ...D.meta.hubRegions].filter(r => count(i => i.region === r));
  const cities = D.hubs.filter(h => count(i => i.place === h.id)).sort((a, b) => (a.label || a.name).localeCompare(b.label || b.name));
  const counties = [...new Set(items.map(i => i.county).filter(Boolean))].sort();
  const whereMenu = `<option value="">All of West Virginia (${items.length})</option>
    <optgroup label="Regions">${regions.map(r => opt('region', r, r === 'Statewide' ? 'Statewide items' : r, count(i => i.region === r))).join('')}</optgroup>
    <optgroup label="Cities and hubs">${cities.map(h => opt('place', h.id, h.label || h.name, count(i => i.place === h.id))).join('')}</optgroup>
    <optgroup label="Counties">${counties.map(c => opt('county', c, c + ' County', count(i => i.county === c))).join('')}</optgroup>`;

  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Hubs · the other AI story</div>
      <h1 class="page-h">Research, classrooms, <em>startups</em></h1>
      <p class="lede">Not every AI story in West Virginia is a data center. This is one feed of the universities, schools, companies, and programs building AI skills and businesses in the state, plus the energy and computing work around them. Every item is tagged by place and topic: sort and filter below, or click any tag. Each links its source and was checked against it (see Receipts).</p>
      <details class="hf-how"><summary>How to read this feed</summary>
        <p>Where a story reports an announcement, plan, or goal, it says so: jobs and investment figures are what was announced, not what has been delivered. An item's date is the date of its newest source. Items marked Background are profiles with no publication date. Place tags are the city or hub, the county, and one of eight regions; the regions are our own groupings, not official ones, and a story about a law or program that applies across the state is tagged Statewide.</p>
      </details>
    </header>
    <section class="sec hf">
      <div class="cx-toolbar" style="margin-top:0">
        <input class="rc-search" id="hfQ" type="search" placeholder="Search stories, sources, places" aria-label="Search the hubs feed" value="${esc(st.q)}">
        <label>Place <select id="hfW">${whereMenu}</select></label>
        <label>Sort <select id="hfS">${SORTS.map(([v, l]) => `<option value="${v}"${st.sort === v ? ' selected' : ''}>${l}</option>`).join('')}</select></label>
      </div>
      <div class="pills hf-topics" id="hfT" role="group" aria-label="Topics">${TOPICS.map(t => `<button type="button" class="pill" data-topic="${t.id}" aria-pressed="false">${esc(t.label)} <span class="hf-n">${count(i => i.topics.includes(t.id))}</span></button>`).join('')}</div>
      <div class="hf-status"><span class="dim mono" id="hfN" role="status" aria-live="polite"></span> <button type="button" class="hf-clear" id="hfX" hidden>Clear filters</button></div>
      <div id="hfList" class="hf-list"></div>
    </section>
  </div>`;

  const $ = id => main.querySelector('#' + id);
  const tag = (kind, value, text, cls = '') => `<button type="button" class="tag hf-tag ${cls}" data-f="${kind}" data-v="${esc(value)}" aria-label="Filter by ${esc(text)}">${esc(text)}</button>`;
  const item = it => {
    const dated = !!it.d, when = dated ? fmtDate(it.d) : 'Background';
    const showCounty = it.county && it.placeName !== it.county + ' County';
    return `<article class="hf-item" id="hf-${esc(it.key)}">
      <div class="news-meta"><time${dated ? ` datetime="${esc(it.d)}"` : ''}${!dated && it.dnote ? ` title="${esc(it.dnote)}"` : ''}>${esc(when)}</time></div>
      <h3>${esc(it.title)}</h3>
      <div class="hf-body" data-body>${it.html}</div>
      <button type="button" class="hf-more" aria-expanded="false" hidden>Read more</button>
      ${srcLinks(it.sources)}
      <div class="news-foot hf-tags">
        ${it.place && it.place !== 'statewide' ? tag('place', it.place, it.placeName, 'hf-place') : ''}${showCounty || (!it.place && it.county) ? tag('county', it.county, it.county + ' Co.', it.place ? '' : 'hf-place') : ''}${tag('region', it.region, it.region)}
        ${it.topics.map(t => tag('topic', t, TOPIC_LABEL[t], 'hf-topic')).join('')}
      </div>
    </article>`;
  };
  const measure = () => {
    if (!document.body.contains($('hfList'))) { window.removeEventListener('resize', onResize); return; }
    main.querySelectorAll('.hf-item').forEach(a => {
      const body = a.querySelector('[data-body]'), btn = a.querySelector('.hf-more');
      const open = a.classList.contains('open');
      a.classList.remove('open');
      const over = body.scrollHeight > body.clientHeight + 2;
      a.classList.toggle('open', open);
      btn.hidden = !over && !open;
    });
  };
  let rt; const onResize = () => { clearTimeout(rt); rt = setTimeout(measure, 150); };

  const sync = () => {
    const p = new URLSearchParams();
    if (st.q) p.set('q', st.q);
    if (st.kind) p.set(st.kind, st.value);
    if (st.topics.size) p.set('topic', [...st.topics].join(','));
    if (st.sort !== 'new') p.set('sort', st.sort);
    history.replaceState(null, '', '#/hubs' + (p.toString() ? '?' + p : ''));
  };
  const render = () => {
    const rows = items.filter(matches).sort(sorters[st.sort]);
    $('hfList').innerHTML = rows.length ? rows.map(item).join('') : `<p class="dim" style="padding:28px 0">Nothing matches those filters.</p>`;
    $('hfN').textContent = rows.length + ' of ' + items.length + ' items';
    const active = !!(st.q || st.kind || st.topics.size);
    $('hfX').hidden = !active;
    main.querySelectorAll('#hfT .pill').forEach(b => b.setAttribute('aria-pressed', String(st.topics.has(b.dataset.topic))));
    $('hfW').value = st.kind ? st.kind + ':' + st.value : '';
    $('hfS').value = st.sort;
    sync();
    requestAnimationFrame(measure);
  };

  $('hfQ').addEventListener('input', e => { st.q = e.target.value.trim(); render(); });
  $('hfS').addEventListener('change', e => { st.sort = e.target.value; render(); });
  $('hfW').addEventListener('change', e => { const v = e.target.value; const i = v.indexOf(':'); st.kind = i < 0 ? '' : v.slice(0, i); st.value = i < 0 ? '' : v.slice(i + 1); render(); });
  $('hfX').addEventListener('click', () => { st.q = ''; st.kind = ''; st.value = ''; st.topics.clear(); $('hfQ').value = ''; render(); });
  main.querySelector('.hf').addEventListener('click', e => {
    const t = e.target.closest('[data-topic], [data-f], .hf-more');
    if (!t) return;
    if (t.matches('.hf-more')) {
      const a = t.closest('.hf-item'); const open = a.classList.toggle('open');
      t.setAttribute('aria-expanded', String(open)); t.textContent = open ? 'Show less' : 'Read more'; return;
    }
    const topic = t.dataset.topic || (t.dataset.f === 'topic' ? t.dataset.v : null);
    if (topic) { st.topics.has(topic) ? st.topics.delete(topic) : st.topics.add(topic); }
    else { const same = st.kind === t.dataset.f && st.value === t.dataset.v; st.kind = same ? '' : t.dataset.f; st.value = same ? '' : t.dataset.v; }
    render();
    if (!t.matches('[data-topic]')) window.scrollTo({ top: main.querySelector('.hf').offsetTop - 70, behavior: 'smooth' });
  });
  window.addEventListener('resize', onResize);
  render();
  return 'Hubs';
}
