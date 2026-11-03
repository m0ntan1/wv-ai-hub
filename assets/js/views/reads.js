// Rook's Read: the daily analysis (data/reads.json). Drafted by the desk task as a pull request,
// reviewed by Mercer, published only when the editor merges it. Body text is plain text: it is
// escaped here, and only [n] source markers become links.
import { D } from '../data.js';
import { esc, fmtDate, DAYS, toDate } from '../lib.js';

const DISCLAIM = 'Analysis and opinion, for education only. Not investment advice; MØNTAN1 and Rick Thomas are not registered investment advisors. Do your own research.';
const CONFLICT = 'Rook and Mercer run on Claude, made by Anthropic, which is Monarch\'s anchor tenant.';

const paraHTML = (r, p) => esc(p).replace(/\[(\d+)\]/g, (m, n) => `<sup><a href="#/rook/${esc(r.id)}#rs-${esc(r.id)}-${n}" class="rr-ref" aria-label="Source ${n}">${n}</a></sup>`);
const dayLine = d => { const t = toDate(d); return `${DAYS[t.getDay()]}, ${fmtDate(d)}`; };

export function mercerStamp(r) {
  const m = r.mercer || {};
  return `<a class="mercer-stamp" href="#/desk/mercer" title="Reviewed by Mercer Lang, compliance (an AI persona). See his review below the Read.">MERCER ✓ ${esc(m.status || '')} ${esc(fmtDate(m.d || r.d, { year: false }))}</a>`;
}

export function readCard(r, { compact = false, h1 = false } = {}) {
  const body = r.body || [];
  const shown = compact ? body.slice(0, 2) : body;
  const words = (body.join(' ').match(/\S+/g) || []).length;
  const mins = Math.max(1, Math.round(words / 230));
  return `<article class="rook-read${compact ? ' compact' : ''}" id="read-${esc(r.id)}">
    <div class="rr-top"><span class="rr-kick">Rook's Read</span><time datetime="${esc(r.d)}">${esc(dayLine(r.d))}</time>${mercerStamp(r)}</div>
    <${h1 ? 'h1' : 'h3'} class="rr-title">${compact ? `<a href="#/rook/${esc(r.id)}">${esc(r.title)}</a>` : esc(r.title)}</${h1 ? 'h1' : 'h3'}>
    <div class="rr-by">By <a href="#/desk/rook">Rook Calloway</a> · Daily Vibe Check WV · ${mins} min read${r.anthropic ? ' · <span class="rr-flag">Anthropic: conflict disclosed</span>' : ''}</div>
    ${r.audio ? `<audio class="rr-audio" controls preload="none" src="${esc(r.audio)}"><a href="${esc(r.audio)}">Listen (MP3)</a></audio><p class="rr-voice">Audio: Rook's voice is synthetic (ElevenLabs).</p>` : ''}
    <div class="rr-body">${shown.map(p => `<p>${paraHTML(r, p)}</p>`).join('')}</div>
    ${compact && body.length > shown.length ? `<p><a class="btn" href="#/rook/${esc(r.id)}">Keep reading →</a></p>` : ''}
    ${compact ? '' : `<ol class="rr-src">${(r.sources || []).map(s => `<li id="rs-${esc(r.id)}-${esc(s.n)}" value="${esc(s.n)}"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)} ↗</a></li>`).join('')}</ol>`}
    <p class="rr-disc">${esc(DISCLAIM)} ${esc(CONFLICT)}</p>
    ${compact ? '' : reviewHTML(r)}
  </article>`;
}

function reviewHTML(r) {
  const m = r.mercer || {};
  const DUTY = { 1: 'Source authority', 2: 'Quotes and copyright', 3: 'Not investment advice', 4: 'Fair comment and libel' };
  return `<details class="rr-review"><summary>Mercer's review</summary>
    ${m.audit ? `<pre class="rr-audit">${esc(m.audit)}</pre>` : ''}
    <dl class="facts">${Object.entries(DUTY).map(([k, l]) => `<div><dt>Duty ${k}</dt><dd><b>${esc(l)}.</b> ${esc((m.duties || {})[k] || '')}</dd></div>`).join('')}</dl>
    ${m.notes ? `<p class="dim" style="margin-top:8px">${esc(m.notes)}</p>` : ''}
    <p class="dim" style="font-size:12.5px;margin-top:8px">Mercer Lang is an AI persona. His review is a check on sourcing and framing, not legal advice. The editor read and approved this Read before it published.</p>
  </details>`;
}

/** The newest Read, for the pinned spot in the news. */
export const latestRead = () => (D.reads || [])[0];

export function rook(main, id) {
  const all = D.reads || [];
  if (id) {
    const r = all.find(x => x.id === id);
    if (!r) return null;
    const i = all.indexOf(r), newer = all[i - 1], older = all[i + 1];
    main.innerHTML = `<div class="wrap" style="max-width:900px">
      <div class="crumb"><a href="#/news">News</a> / <a href="#/rook">Rook's Read</a> / ${esc(fmtDate(r.d))}</div>
      <div style="margin-top:18px">${readCard(r, { h1: true })}</div>
      ${(r.companies || []).length || (r.projects || []).length ? `<div class="rel" style="margin-top:14px">${(r.companies || []).filter(c => D.coById[c]).map(c => `<a class="tag" href="#/company/${esc(c)}">${esc(D.coById[c].name)}</a>`).join('')}${(r.projects || []).map(p => `<a class="tag" href="${D.projLink(p)}">${esc(D.projName(p))}</a>`).join('')}</div>` : ''}
      <nav class="rr-nav">${older ? `<a href="#/rook/${esc(older.id)}">← ${esc(fmtDate(older.d, { year: false }))}</a>` : '<span></span>'}<a href="#/rook">All Reads</a>${newer ? `<a href="#/rook/${esc(newer.id)}">${esc(fmtDate(newer.d, { year: false }))} →</a>` : '<span></span>'}</nav>
    </div>`;
    return "Rook's Read: " + r.title;
  }
  main.innerHTML = `<div class="wrap" style="max-width:900px">
    <header style="padding-top:28px">
      <div class="kicker">Rook's Read · ${all.length} ${all.length === 1 ? 'Read' : 'Reads'}</div>
      <h1 class="page-h">Rook's <em>Read</em></h1>
      <p class="lede">A daily take on the news and the money behind West Virginia's data centers, by <a href="#/desk/rook">Rook Calloway</a>. Critical, but he calls balls and strikes. Every Read is checked by <a href="#/desk/mercer">Mercer Lang</a> for sourcing, quotes, investment-advice framing, and fairness, then approved by the editor before it appears here.</p>
      <p class="dim" style="font-size:13.5px;margin-top:10px">Rook and Mercer are AI personas. <a href="#/desk">How the desk works</a></p>
    </header>
    <section class="sec">${all.length ? all.map(r => readCard(r, { compact: true })).join('') : `<div class="card"><p><b>The first Read is on its way.</b> Rook drafts each weekday morning; nothing appears here until Mercer clears it and the editor approves it.</p></div>`}</section>
  </div>`;
  return "Rook's Read";
}
