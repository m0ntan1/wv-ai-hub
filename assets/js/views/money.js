// The Money Desk: who is paying for West Virginia's AI buildout, and how healthy they are.
// Roster: data/companies.json (hand-curated). Filings and figures: data/filings.json (tools/fetch_filings.py).
import { D } from '../data.js';
import { esc, fmtDate, MON, srcLink, srcLinks, vfy, stamp, plural } from '../lib.js';
import { chartBox, mountCharts, fmtVal } from '../charts.js';
import { stories, storyHTML } from './news.js';
import { readCard } from './reads.js';

const FORMS = { '10-K': 'Annual report', '10-K/A': 'Annual report (amended)', '10-Q': 'Quarterly report', '10-Q/A': 'Quarterly report (amended)', '8-K': 'Current report', '8-K/A': 'Current report (amended)', '20-F': 'Annual report', '6-K': 'Current report', 'S-1': 'IPO registration', 'S-1/A': 'IPO registration (amended)', 'F-1': 'IPO registration', 'F-1/A': 'IPO registration (amended)', '424B4': 'Final prospectus: offering priced', '424B1': 'Final prospectus: offering priced', 'DEF 14A': 'Proxy statement' };
const ITEMS = { '1.01': 'material agreement', '1.02': 'agreement ended', '1.03': 'bankruptcy', '2.01': 'deal completed', '2.02': 'results', '2.03': 'new debt', '2.04': 'debt trigger', '2.05': 'restructuring', '2.06': 'impairment', '3.01': 'listing notice', '3.02': 'unregistered share sale', '3.03': 'shareholder rights change', '4.01': 'auditor change', '4.02': 'restatement', '5.02': 'officer or director change', '5.03': 'bylaws change', '5.07': 'shareholder vote', '7.01': 'disclosure', '8.01': 'other event' };
// Items that tend to matter for a company's health; shown highlighted.
const LOUD = new Set(['1.03', '2.03', '2.04', '2.05', '2.06', '3.01', '4.01', '4.02']);
export const HEALTH = {
  stable: { label: 'Stable', tone: 'ok', def: 'Filings show revenue and cash that comfortably cover obligations, with no going-concern, default, or restatement flags.' },
  watch: { label: 'Watch', tone: 'signal', def: 'Something in the filings needs watching: heavy losses, reliance on financing not yet committed, customer concentration, or a material weakness.' },
  stressed: { label: 'Stressed', tone: 'alarm', def: 'Filings show acute strain: going-concern doubt that is not resolved, a missed payment or covenant breach, a restatement, or a ratings or listing notice.' },
  pending: { label: 'Health: pending', tone: 'dim', def: 'Not rated yet. The editor has not approved a health read for this company.' },
  nodata: { label: 'No public financials', tone: 'dim', def: 'Privately held, so there are no filings to read.' },
  na: { label: 'Not rated', tone: 'dim', def: 'Tracked as an indicator or a public body, not rated.' },
};
const LISTING = { public: 'Public', ipo: 'IPO filed', private: 'Private', foreign: 'Listed outside the U.S.', 'public-body': 'Public agency' };
const SERIES = ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)'];

const cikN = cik => String(+cik);
const nodash = a => a.replace(/-/g, '');
export const filingUrl = (cik, f) => `https://www.sec.gov/Archives/edgar/data/${cikN(cik)}/${nodash(f.accn)}/${f.doc}`;
const accnUrl = (cik, accn) => `https://www.sec.gov/Archives/edgar/data/${cikN(cik)}/${nodash(accn)}/${accn}-index.htm`;
const edgarUrl = cik => `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${cik}&type=&dateb=&owner=include&count=40`;
const qLabel = end => { const [y, m] = end.split('-'); return MON[+m - 1] + " '" + y.slice(2); };
const qLong = (p) => `the quarter ended ${fmtDate(p.end)}`;
export const healthChip = c => { const h = HEALTH[c.health?.status] || HEALTH.pending; return `<span class="hchip t-${h.tone}" title="${esc(h.def)}"><b>${esc(h.label)}</b>${['stable', 'watch', 'stressed'].includes(c.health?.status) ? '<small>analysis</small>' : ''}</span>`; };
const sec = id => D.filings?.sec?.[id];
const tickerOf = c => { const r = sec(c.id); return c.ticker || (r?.tickers || [])[0] || ''; };
const exchangeOf = c => c.exchange || (sec(c.id)?.exchanges || [])[0] || '';

function yoy(q, key = 'v') {
  if (!q || q.length < 2) return null;
  const last = q[q.length - 1];
  const t = new Date(last.end); t.setFullYear(t.getFullYear() - 1);
  const prev = q.find(p => Math.abs(new Date(p.end) - t) < 12 * 86400000);
  if (!prev || prev[key] <= 0 || last[key] < 0) return null;
  return { pct: (last[key] / prev[key] - 1) * 100, prev };
}
const pctTxt = p => (p >= 0 ? '+' : '−') + Math.abs(p).toFixed(0) + '%';
function latestFiling(c) { const f = sec(c.id)?.filings?.[0]; return f ? `${esc(f.form)} · ${esc(fmtDate(f.d, { year: false }))}` : ''; }
function headline(c) {
  const m = sec(c.id)?.metrics;
  const q = m?.revenue?.q;
  if (!q || !q.length) return '';
  const last = q[q.length - 1], y = yoy(q);
  return `<span class="co-num"><b>${fmtVal(last.v)}</b> revenue, ${esc(qLabel(last.end))} quarter${y ? ` <span class="${y.pct >= 0 ? 'up' : 'down'}">${pctTxt(y.pct)} y/y</span>` : ''}</span>`;
}

export function coCard(c) {
  const t = tickerOf(c);
  return `<a class="co-card" href="#/company/${esc(c.id)}">
    <div class="co-top"><span class="co-tk">${esc(t ? (c.listing === 'ipo' ? t + ' · IPO filed' : t) : LISTING[c.listing])}</span>${healthChip(c)}</div>
    <h3>${esc(c.name)}</h3>
    <p>${esc(c.tie.split('. ')[0].replace(/\.$/, ''))}.</p>
    ${headline(c)}
    <div class="co-foot">${(c.projects || []).filter(p => D.byId[p] || p === 'marl' || p === 'valleylink').map(p => `<span class="tag">${esc(D.projName(p))}</span>`).join('')}${latestFiling(c) ? `<span class="co-f">Latest: ${latestFiling(c)}</span>` : c.listing === 'private' ? '<span class="co-f">No SEC filings</span>' : ''}</div>
  </a>`;
}

export const disclaimer = (strong) => `<aside class="money-note">
  <p><b>Analysis for education only. Not investment advice.</b> MØNTAN1 and Rick Thomas are not registered investment advisors. Nothing here is a recommendation to buy, sell, or hold anything. Do your own research, starting with the filings we link.</p>
  <p class="conflict"><b>Conflict, disclosed:</b> the analysis on this desk is drafted by AI agents that run on Claude, a model made by Anthropic. Anthropic is Monarch's anchor tenant and is profiled here like every other company.${strong ? ' Weigh our Anthropic coverage with that in mind: every figure on its page links to Anthropic\'s own filing so you can check it yourself.' : ''} <a href="#/desk">Who writes this →</a></p>
</aside>`;

// ---------------------------------------------------------------- industry signals
function capexChart() {
  const ids = ['alphabet', 'microsoft', 'amazon', 'meta'];
  const sets = ids.map(id => ({ c: D.coById[id], q: sec(id)?.metrics?.capex?.q || [] })).filter(x => x.c && x.q.length);
  if (!sets.length) return '<p class="empty">Capital-spending figures appear after the filings collector runs.</p>';
  const ends = [...new Set(sets.flatMap(s => s.q.map(p => p.end)))].sort().slice(-8);
  const series = sets.map((s, i) => ({ label: s.c.name.split(' (')[0], color: SERIES[i], v: ends.map(e => s.q.find(p => p.end === e)?.v ?? null) }));
  const totals = ends.map((e, i) => series.every(s => s.v[i] !== null) ? series.reduce((a, s) => a + s.v[i], 0) : null);
  const li = totals.length - 1, prevI = totals.length - 5;
  const growth = totals[li] && prevI >= 0 && totals[prevI] ? (totals[li] / totals[prevI] - 1) * 100 : null;
  const derivedAny = sets.some(s => s.q.some(p => ends.includes(p.end) && p.derived));
  return `<div class="sig-hero"><div><b>${totals[li] !== null ? fmtVal(totals[li]) : 'n/a'}</b><span>combined, ${esc(qLabel(ends[li]))} quarter</span></div>${growth !== null ? `<div><b>${pctTxt(growth)}</b><span>vs. the same quarter a year earlier</span></div>` : ''}</div>
    ${chartBox({ type: 'line', title: 'Quarterly cash spent on property and equipment', fmt: 'usd', zero: true, height: 230, xs: ends.map(qLabel), tipX: ends.map(e => 'Quarter ended ' + fmtDate(e)), series,
      note: `From each company's 10-Q and 10-K XBRL data on SEC EDGAR.${derivedAny ? ' Some quarters are derived: the filings report capital spending year to date, so a quarter is that figure minus the previous one.' : ''} Each company tags this figure a little differently in its XBRL data; hover or open the table for exact values.` })}`;
}
function fredCard(s) {
  const f = D.filings?.fred?.[s.fred];
  if (!f) return `<article class="card sig"><h3>${esc(s.name)}</h3><p class="dim">${esc(s.what)}</p><p class="empty">Data appears after the collector runs.</p>${srcLink(s.source)}</article>`;
  const fm = s.unit === '%' ? 'pct' : 'usd2';
  const ch = f.yearAgo ? f.last.v - f.yearAgo.v : null;
  return `<article class="card sig">
    <h3>${esc(s.name)}</h3>
    <div class="sig-big"><b>${fmtVal(f.last.v, fm)}</b>${s.unit !== '%' ? `<small>${esc(s.unit)}</small>` : ''}<span>on ${esc(fmtDate(f.last.d))}</span></div>
    ${ch !== null ? `<p class="sig-ch">${ch >= 0 ? 'Up' : 'Down'} ${s.unit === '%' ? Math.abs(ch).toFixed(2) + ' percentage points' : fmtVal(Math.abs(ch), fm)} from a year earlier (${fmtVal(f.yearAgo.v, fm)} on ${esc(fmtDate(f.yearAgo.d))})</p>` : ''}
    ${chartBox({ type: 'line', fmt: fm, height: 110, xs: f.monthly.map(x => qLabel(x[0] + '-01')), tipX: f.monthly.map(x => 'Average, ' + fmtDate(x[0])), series: [{ label: s.name, color: 'var(--cyan)', v: f.monthly.map(x => x[1]) }], table: false })}
    <p class="dim sig-why"><b>Why it matters.</b> ${esc(s.why)}</p>
    <div class="srcs">${srcLink(s.source)}</div>
  </article>`;
}

// ---------------------------------------------------------------- index
export function money(main, q) {
  const C = D.companies.companies, T = D.companies.tranches;
  const by = id => C.filter(c => c.tranche === id || (c.also || []).includes(id));
  const recent = Object.entries(D.filings?.sec || {}).flatMap(([id, r]) => (r.filings || []).map(f => ({ ...f, id, cik: r.cik })))
    .sort((a, b) => a.d < b.d ? 1 : -1).slice(0, 12);
  const reads = (D.reads || []).filter(r => (r.companies || []).length).slice(0, 1);
  main.innerHTML = `<div class="wrap">
    <header style="padding-top:28px">
      <div class="kicker">Money · ${C.length} companies and backers · 4 tranches${D.filings?.updated ? ' · filings checked ' + esc(fmtDate(D.filings.updated.slice(0, 10))) : ''}</div>
      <h1 class="page-h">Follow the <em>money</em></h1>
      <p class="lede">Will these projects actually get built, and who is left holding the bill if they don't? Here is every company and investor tied to West Virginia's data center projects, what their own filings say about their health, and the industry signals that move first.</p>
    </header>
    ${disclaimer(false)}
    <nav class="pills" style="margin:18px 0 4px" aria-label="Tranches">${T.map(t => `<a class="pill" href="#/money#tr-${t.id}">${esc(t.name)}</a>`).join('')}<a class="pill" href="#/money#latest-filings">Latest filings</a><a class="pill" href="#/money#how">How this works</a></nav>
    ${reads.length ? `<section class="sec" style="padding-bottom:0">${readCard(reads[0], { compact: true })}</section>` : ''}

    <section class="sec" id="tr-industry">
      <div class="sec-h">${esc(T[0].name)}</div>
      <p class="tr-blurb">${esc(T[0].blurb)}</p>
      <div class="sig-grid">
        <article class="card sig sig-wide"><h3>Hyperscaler capital spending</h3><p class="dim">${esc(D.companies.signals.find(s => s.id === 'capex').why)}</p>${capexChart()}</article>
        ${D.companies.signals.filter(s => s.kind === 'fred').map(fredCard).join('')}
        ${D.companies.signals.filter(s => s.kind === 'link').map(s => `<article class="card sig"><h3>${esc(s.name)}</h3><p class="dim">${esc(s.what)}</p><p class="dim sig-why"><b>Why it matters.</b> ${esc(s.why)}</p><div class="srcs">${srcLink(s.source)}</div></article>`).join('')}
      </div>
    </section>

    ${T.slice(1).map(t => {
      const list = by(t.id);
      const groups = t.id === 'shovels' ? [...new Set(list.map(c => c.group || 'Other'))] : [null];
      return `<section class="sec" id="tr-${t.id}">
        <div class="sec-h">${esc(t.name)} · ${list.length}</div>
        <p class="tr-blurb">${esc(t.blurb)}</p>
        ${groups.map(g => `${g ? `<div class="cx-group-h" style="margin-top:16px">${esc(g)}</div>` : ''}<div class="co-grid">${list.filter(c => !g || (c.group || 'Other') === g).map(coCard).join('')}</div>`).join('')}
      </section>`;
    }).join('')}

    <section class="sec" id="latest-filings">
      <div class="sec-h">Latest filings across the roster <a class="src act" href="https://www.sec.gov/edgar/search/" target="_blank" rel="noopener">SEC EDGAR ↗</a></div>
      ${recent.length ? `<ul class="fil-list">${recent.map(f => filingRow(f, true)).join('')}</ul>` : '<p class="empty">Filings appear after the collector runs.</p>'}
      ${searchHTML()}
    </section>

    <section class="sec" id="how">
      <div class="sec-h">How this works</div>
      <div class="how-grid">
        <div><h4>Where the numbers come from</h4><p>A script (<a class="src" href="https://github.com/m0ntan1/WV-AI-HUB/blob/main/tools/fetch_filings.py" target="_blank" rel="noopener">fetch_filings.py ↗</a>) reads SEC EDGAR and the Federal Reserve's FRED database every three hours. No AI is involved in that step. Figures are as each company reported them, with a link to the filing. For companies still in IPO registration, the figures are typed from their S-1 and checked by hand.</p></div>
        <div><h4>Health reads</h4><p>${Object.entries(HEALTH).filter(([k]) => ['stable', 'watch', 'stressed'].includes(k)).map(([k, h]) => `<span class="hchip t-${h.tone}"><b>${h.label}</b></span> ${esc(h.def)}`).join('<br>')}<br>A read describes financial condition from filings. It is never a judgment of anyone's motives, and it changes only when the editor approves it.</p></div>
        <div><h4>Who's on the roster</h4><p>A company joins only with a sourced tie to a West Virginia project, or as a labeled industry indicator. Private companies are listed with what is and isn't public, rather than a guess. <a class="src" href="#/contact?topic=correction">Suggest a correction</a></p></div>
      </div>
    </section>
  </div>`;
  mountCharts(main);
  return 'Money';
}

function filingRow(f, who) {
  const c = D.coById[f.id];
  const items = (f.items || []).filter(i => ITEMS[i]);
  return `<li class="fil"><time>${esc(fmtDate(f.d, { year: false }))}</time>
    <span>${who && c ? `<a href="#/company/${esc(c.id)}"><b>${esc(c.name)}</b></a> · ` : ''}<a href="${esc(filingUrl(f.cik, f))}" target="_blank" rel="noopener">${esc(f.form)}</a> <span class="dim">${esc(FORMS[f.form] || '')}${f.period && !f.form.startsWith('8-K') ? ', period ending ' + esc(fmtDate(f.period)) : ''}</span>
    ${items.length ? `<span class="fil-items">${items.map(i => `<span class="${LOUD.has(i) ? 'loud' : ''}">${esc(ITEMS[i])}</span>`).join('')}</span>` : ''}</span></li>`;
}

function searchHTML(project) {
  const S = D.companies.secSearch.filter(s => !project || s.project === project);
  const got = S.map(s => ({ s, r: D.filings?.search?.[s.q] })).filter(x => x.r);
  if (!got.length) return '';
  return `<div class="cx-group-h" style="margin-top:26px">Filings that name a West Virginia project or developer (past year)</div>
    <p class="dim" style="font-size:13.5px;max-width:820px">An EDGAR full-text search for each phrase. A mention can be a footnote; it does not by itself mean a company has a stake in West Virginia. Open the filing to see the context.</p>
    <div class="grid-auto" style="margin-top:10px">${got.map(({ s, r }) => `<div class="card srch"><div class="kicker">"${esc(s.q)}"</div>
      <p class="dim" style="margin:4px 0 6px">${plural(r.total, 'filing')}${s.project ? ` · <a href="${D.projLink(s.project)}" style="color:inherit">${esc(D.projName(s.project))}</a>` : ''}</p>
      ${r.hits.length ? `<ul class="fil-list sm">${r.hits.slice(0, 4).map(h => `<li class="fil"><time>${esc(fmtDate(h.d, { year: false }))}</time><span><a href="${esc(filingUrl(h.cik, h))}" target="_blank" rel="noopener">${esc(h.form)}</a> <span class="dim">${esc(h.who[0] || '')}</span></span></li>`).join('')}</ul>` : '<p class="empty">No filings in the past year.</p>'}
      <a class="src" href="https://www.sec.gov/edgar/search/#/q=${encodeURIComponent('"' + s.q + '"')}" target="_blank" rel="noopener">Search EDGAR ↗</a></div>`).join('')}</div>`;
}

// ---------------------------------------------------------------- company page
function metricsHTML(c) {
  const r = sec(c.id), m = r?.metrics;
  if (!m || !Object.keys(m).length) return '';
  const rows = [];
  const dur = (key, label) => {
    const q = m[key]?.q; if (!q || !q.length) return;
    const last = q[q.length - 1], y = yoy(q);
    rows.push(`<div><dt>${label}</dt><dd><b>${fmtVal(last.v)}</b> in ${esc(qLong(last))}${y ? `, <span class="${y.pct >= 0 ? 'up' : 'down'}">${pctTxt(y.pct)}</span> from ${fmtVal(y.prev.v)} a year earlier` : ''}${last.derived ? ' <span class="dim">(derived from year-to-date figures)</span>' : ''} ${srcLink({ label: last.form, url: accnUrl(r.cik, last.accn) })}</dd></div>`);
  };
  dur('revenue', 'Revenue'); dur('netIncome', 'Net income'); dur('capex', 'Capital spending');
  ['cash', 'debt'].forEach(k => { const x = m[k]; if (x) rows.push(`<div><dt>${k === 'cash' ? 'Cash' : 'Long-term debt'}</dt><dd><b>${fmtVal(x.v)}</b> as of ${esc(fmtDate(x.end))} ${srcLink({ label: x.form, url: accnUrl(r.cik, x.accn) })}</dd></div>`); });
  const newestEnd = Math.max(...Object.values(m).map(v => +new Date(v.end || v.q?.[v.q.length - 1]?.end || 0)));
  const per = (r.filings || []).find(f => /^10-[QK]/.test(f.form) && f.period);
  const lag = per && +new Date(per.period) > newestEnd + 20 * 86400000;
  const charts = ['revenue', 'capex'].filter(k => m[k]?.q?.length > 2).map(k => {
    const q = m[k].q;
    return chartBox({ type: 'bar', title: k === 'revenue' ? 'Revenue by quarter' : 'Capital spending by quarter', fmt: 'usd', height: 170, xs: q.map(p => qLabel(p.end)), tipX: q.map(p => 'Quarter ended ' + fmtDate(p.end) + (p.derived ? ' (derived)' : '')), series: [{ label: k === 'revenue' ? 'Revenue' : 'Capital spending', color: k === 'revenue' ? 'var(--cyan)' : 'var(--s2)', v: q.map(p => p.v) }] });
  });
  return `<section class="cf-sec" id="s-figures">
    <div class="sec-h">From the filings <a class="src act" href="${esc(edgarUrl(r.cik))}" target="_blank" rel="noopener">All filings on EDGAR ↗</a></div>
    ${lag ? `<p class="lagnote">The SEC's structured data does not yet include the ${esc(per.form)} filed ${esc(fmtDate(per.d))} for the period ending ${esc(fmtDate(per.period))}, so these figures stop earlier. <a href="${esc(filingUrl(r.cik, per))}" target="_blank" rel="noopener">Read that filing ↗</a></p>` : ''}
    <dl class="facts">${rows.join('')}</dl>
    ${charts.length ? `<div class="co-charts">${charts.join('')}</div>` : ''}
    <p class="dim" style="font-size:12.5px;margin-top:8px">As reported in the company's XBRL data on SEC EDGAR (${esc(Object.values(m).map(v => v.concept).filter(Boolean).slice(0, 3).join(', '))}…). Year-over-year changes compare the same quarter a year earlier.</p>
  </section>`;
}

export function company(main, id) {
  const c = D.coById[id];
  if (!c) return null;
  const T = D.companies.tranches.find(t => t.id === c.tranche);
  const r = sec(c.id), t = tickerOf(c), ex = exchangeOf(c);
  const parent = c.parent && D.coById[c.parent];
  const kids = D.companies.companies.filter(x => x.parent === c.id);
  const h = HEALTH[c.health?.status] || HEALTH.pending;
  const press = stories({ q: c.name.split(' (')[0].split(' /')[0] }).slice(0, 6);
  const myReads = (D.reads || []).filter(x => (x.companies || []).includes(c.id));
  main.innerHTML = `<div class="wrap">
    <div class="crumb"><a href="#/money">Money</a> / <a href="#/money#tr-${esc(c.tranche)}">${esc(T.name)}</a> / ${esc(c.name)}</div>
    <header class="cf-head">
      <div>
        <h1>${esc(c.name)}</h1>
        <div class="cf-meta">${t ? `<span><b>${esc(t)}</b>${ex ? ' · ' + esc(ex) : ''}${c.listing === 'ipo' ? ' (planned symbol; not yet trading)' : ''}</span>` : ''}<span>${esc(LISTING[c.listing])}</span>${c.hq ? `<span>${esc(c.hq)}</span>` : ''}${c.group ? `<span>${esc(c.group)}</span>` : ''}</div>
        ${c.verify ? `<p style="margin-top:10px">${vfy(c.verify)} <span class="dim">${esc(c.verify)}</span></p>` : ''}
      </div>
      <div class="cf-stamps">${['stable', 'watch', 'stressed'].includes(c.health?.status) ? stamp(h.label + ' · analysis', h.tone, true) : stamp(h.label, 'dim')}</div>
    </header>
    ${c.selfConflict ? `<aside class="money-note conflict-strong"><p><b>Conflict, disclosed.</b> Rook and Mercer, who write this desk's analysis, run on Claude, which is made by Anthropic. This page was also built with Claude. Weigh our Anthropic coverage with that in mind. Every figure here links to Anthropic's own filing so you can check it yourself, and Anthropic gets the same rubric as every other company.</p></aside>` : ''}
    <div class="cf-grid">
      <div>
        <section class="cf-sec">
          <div class="sec-h">The West Virginia tie</div>
          <p class="co-tie">${esc(c.tie)}</p>
          ${srcLinks(c.sources)}
          ${(c.projects || []).length ? `<div class="rel" style="margin-top:12px">${c.projects.map(p => `<a class="tag" href="${D.projLink(p)}">${esc(D.projName(p))} →</a>`).join('')}${c.node ? `<a class="tag" href="#/people?focus=${esc(c.node)}">Connections web →</a>` : ''}</div>` : ''}
          ${parent ? `<p class="dim" style="margin-top:10px">Owned by <a href="#/company/${esc(parent.id)}">${esc(parent.name)}</a>.</p>` : ''}
          ${kids.length ? `<p class="dim" style="margin-top:10px">Owns ${kids.map(k => `<a href="#/company/${esc(k.id)}">${esc(k.name)}</a>`).join(', ')}.</p>` : ''}
        </section>
        ${c.facts ? `<section class="cf-sec" id="s-facts"><div class="sec-h">From the filing</div><p class="dim" style="font-size:13.5px;margin-bottom:6px">${esc(c.factsAsOf)}</p>
          <dl class="facts">${c.facts.map(f => `<div><dt>${esc(f.k)}</dt><dd>${esc(f.v)}</dd></div>`).join('')}</dl>${srcLinks(c.sources.filter(s => s.url.includes('sec.gov')))}</section>` : ''}
        ${metricsHTML(c)}
        ${c.unknown ? `<section class="cf-sec"><div class="redact-block"><div class="lbl">What isn't public</div><p>${esc(c.unknown)}</p>${c.irUrl ? `<div class="srcs">${srcLink({ label: 'Investor relations', url: c.irUrl })}</div>` : ''}</div></section>` : ''}
        ${c.risks ? `<section class="cf-sec"><div class="sec-h">Risks the filing names</div><ul class="bul">${c.risks.map(x => `<li>${esc(x)}</li>`).join('')}</ul><p class="dim" style="font-size:12.5px">Paraphrased from the filing's own risk factors; not a complete list.</p></section>` : ''}
        ${c.watch ? `<section class="cf-sec"><div class="sec-h">What to watch</div><ul class="bul">${c.watch.map(x => `<li>${esc(x)}</li>`).join('')}</ul></section>` : ''}
        ${myReads.length ? `<section class="cf-sec"><div class="sec-h">Rook's Reads on ${esc(c.name.split(' (')[0])}</div>${myReads.slice(0, 3).map(x => readCard(x, { compact: true })).join('')}</section>` : ''}
        ${press.length ? `<section class="cf-sec"><div class="sec-h">In the news <a class="src act" href="#/news?q=${encodeURIComponent(c.name.split(' (')[0].split(' /')[0])}">More →</a></div>${press.map(s => storyHTML(s)).join('')}</section>` : ''}
      </div>
      <aside>
        <div class="card side-health"><div class="kicker">Health read</div><p style="margin-top:8px">${healthChip(c)}</p>
          <p class="dim" style="font-size:13.5px;margin-top:8px">${esc(c.health?.why || h.def)}</p>
          ${c.health?.approved ? `<p class="dim mono" style="font-size:11px;margin-top:8px">Approved by the editor ${esc(fmtDate(c.health.approved))}</p>` : ''}
          <p style="margin-top:10px"><a class="src" href="#/money#how">How health reads work</a></p></div>
        ${r?.filings?.length ? `<div class="card" style="margin-top:14px"><div class="kicker">Recent SEC filings</div><ul class="fil-list sm" style="margin-top:8px">${r.filings.slice(0, 8).map(f => filingRow({ ...f, id: c.id, cik: r.cik }, false)).join('')}</ul>
          <div class="srcs"><a class="src" href="${esc(edgarUrl(r.cik))}" target="_blank" rel="noopener">All filings ↗</a></div></div>` : ''}
        ${(c.projects || []).some(p => D.companies.secSearch.some(s => s.project === p)) ? `<div class="side-search">${searchHTML(c.projects.find(p => D.companies.secSearch.some(s => s.project === p)))}</div>` : ''}
        <div style="margin-top:14px">${disclaimer(c.selfConflict)}</div>
      </aside>
    </div>
  </div>`;
  mountCharts(main);
  return c.name;
}

/** Companies tied to a project, for the case files. */
export function projectMoney(id) {
  const list = (D.companies?.companies || []).filter(c => (c.projects || []).includes(id));
  if (!list.length) return '';
  return `<div class="money-strip"><span class="kicker">Follow the money</span>${list.map(c => `<a class="tag" href="#/company/${esc(c.id)}">${esc(c.name)}</a>`).join('')}</div>`;
}
