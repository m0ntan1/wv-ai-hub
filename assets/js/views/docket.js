import { D } from '../data.js';
import { esc, STAGES, BODIES } from '../lib.js';
import { docketCard } from '../parts.js';

export function docket(main, q) {
  const body = q.get('body') || 'all';
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Docket · Courts, PSC, DEP, Legislature</div>
      <h1 class="page-h">Where every <em>fight</em> stands</h1>
      <p class="lede">${D.docket.length} matters, from cases not yet filed to decisions already in effect. Each card carries its case number and a stamp with its current state. Dates come from PSC docket notices, court reporting, and the agencies; anything we could not confirm wears ⚠ Verify.</p>
      <div class="pills" role="group" aria-label="Filter by body" style="margin-top:16px">
        ${[['all', 'All'], ...Object.entries(BODIES)].map(([k, l]) => `<button type="button" class="pill" data-body="${k}" aria-pressed="${k === body}">${l} · ${k === 'all' ? D.docket.length : D.docket.filter(x => x.body === k).length}</button>`).join('')}
      </div>
    </header>
    <section class="sec"><div class="cols" id="cols"></div></section>
  </div>`;
  const render = b => {
    main.querySelector('#cols').innerHTML = STAGES.map(s => {
      const list = D.docket.filter(k => k.stage === s.id && (b === 'all' || k.body === b));
      return `<div class="col" id="stage-${s.id}"><div class="col-h"><span>${esc(s.label)}</span><b>${list.length}</b></div>${list.map(k => docketCard(k)).join('') || '<p class="empty">None.</p>'}</div>`;
    }).join('');
  };
  main.querySelectorAll('[data-body]').forEach(btn => btn.addEventListener('click', () => {
    main.querySelectorAll('[data-body]').forEach(x => x.setAttribute('aria-pressed', x === btn));
    render(btn.dataset.body);
  }));
  render(body);
  const stage = q.get('stage');
  if (stage) setTimeout(() => main.querySelector('#stage-' + stage)?.scrollIntoView({ block: 'start' }), 50);
  return 'Docket';
}
