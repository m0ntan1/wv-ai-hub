# WV AI Watch: How the site works

This file covers the architecture and the data formats. For the update routine (sources, cadence, checklists, verification rules), see [`docs/update-plan.md`](docs/update-plan.md).

## Architecture

A static site with no build step and no backend. `index.html` is a small shell. Everything you see is rendered in the browser by ES modules from JSON files in `data/`.

```
index.html                 Shell: <head> SEO, header/nav, footer, mobile tab bar. Loads assets/js/main.js.
assets/css/watch.css       All styles. Themes: "ink" (dark, default) and "news" (light newsprint; also the print style).
assets/js/
  main.js                  Boot: loads data, renders header and ticker, hash router, theme and Receipts-mode toggles.
  data.js                  Fetches data/*.json once; builds lookups (projects by id, counties, upcoming events, docket "next" dates).
  lib.js                   Helpers: escaping, dates (with ?today= override), status and event vocab, stamps, ⚠ Verify chips, .ics export.
  map.js                   SVG map: 55 counties, state border, projects, transmission lines, upcoming-date badges, time slider.
  parts.js                 Shared markup: countdown chips, event cards and rows, docket cards, project cards, standing meetings.
  views/front.js           #/            masthead, countdowns, headline numbers, desk log, map, "this week near you", docket strip, projects
  views/project.js         #/project/:id case file: facts, scale art, timeline, permits and cases, people and connections, take part, receipts
  views/docket.js          #/docket      stage board (not yet filed → open → briefing → awaiting decision → decided)
  views/calendar.js        #/calendar    agenda and month views, filters, .ics, standing meetings
  views/people.js          #/people      connections web (deterministic force layout) and directory
  views/county.js          #/counties, #/county/:slug   county index and printable field sheet
  views/misc.js            #/projects, #/map, #/receipts, 404
  views/hubs.js            #/hubs: one feed tagged by place and topic (filters live in the URL)
  views/contact.js         #/contact     contact form (Netlify Forms; the hidden copy in index.html registers it at deploy)
  views/news.js            #/news        news aggregator, plus the front-page "In the news" section and each case file's news
data/*.json                The content. Edit these to update the site.
calendar.ics, feed.json    Built by tools/build_feeds.py from data/.
assets/qr/*.svg            County-sheet QR codes, built by tools/build_feeds.py.
tools/check.py             Validator: run before every publish.
tools/build_feeds.py       Builds calendar.ics, feed.json, QR codes, sitemap.
tools/build_geo.py         Builds data/geo.json from Census-derived county GeoJSON (run once; rerun only to change the boundaries).
tools/fetch_filings.py     Money Desk collector: SEC EDGAR filings and figures plus FRED indicators -> data/filings.json (needs SEC_USER_AGENT).
tools/voice_read.py        Voices a cleared Rook's Read from its spoken script with ElevenLabs eleven_v4, checks each section by transcript (needs ELEVENLABS_API_KEY, ROOK_VOICE_ID, ffmpeg).
audio/rook/                Per Read: <id>.script.md (spoken script + fidelity table), <id>.mp3 (the audio), <id>.voice.json (voicing receipt).
tools/migrate/             One-time migration from the old single-file site (kept as a receipt).
research/                  Sourced dossier, calendar receipts, PSC watchlist, verification log and scripts.
design/                    Revamp proposal, concept board, screenshots.
docs/update-plan.md        How the site is kept current.
.claude/skills/            Project skills for the scheduled tasks: rooks-read (the daily Read) and makenomistakes (Mercer's audit).
```

### Routes
Hash routes, so any static host works: `#/`, `#/map`, `#/projects`, `#/project/:id`, `#/docket`, `#/calendar`, `#/people`, `#/counties`, `#/county/:slug`, `#/hubs`, `#/receipts`, `#/contact`, `#/news`, `#/money`, `#/company/:id`, `#/rook`, `#/rook/:id`, `#/desk`, `#/desk/rook`, `#/desk/mercer`.
Query strings work after the route: `#/people?focus=bowles-rice`, `#/calendar?county=Mason`, `#/calendar?e=<event id>`, `#/docket?body=psc`, `#/contact?topic=correction&about=<project>`.

### Contact form
`#/contact` posts to Netlify Forms (form name `contact`). Netlify finds the form by reading the hidden copy at the bottom of `index.html` when it deploys, so if you add or rename a field, change both places. Submissions land in the Netlify dashboard under Forms, behind Akismet spam filtering and a honeypot field. To get them by email, add a notification there (Forms > Submission notifications); the address stays private to Netlify.
Links from the old one-page site (`#projects`, `#docket`, `#calendar`, `#people`, `#proj-<id>`, `#sec-<city>`) redirect to their new homes.

### Time travel
Add `?today=YYYY-MM-DD` before the hash (for example `/?today=2027-03-01#/`) to see the site as of another day. Countdowns, past/upcoming events, and the checker's warnings all follow it. Use it to test updates and to check what readers will see next week.

### Run locally
```bash
python3 -m http.server 8000
```
Then open `http://localhost:8000`. Opening `index.html` directly from disk won't work, because the browser blocks module and JSON loading from `file://`.

---

## Data formats

All dates are `YYYY-MM-DD`, or `YYYY-MM` / `YYYY` when only the month or year is known. Times are 24-hour `HH:MM`, US Eastern. A **source** is always `{ "label": "...", "url": "https://..." }`.

### `projects.json`
| Field | Notes |
|---|---|
| `id`, `short`, `name` | `id` is used in URLs (`#/project/monarch`) and every cross-reference |
| `status` | `construction` · `certified` · `contested` · `proposed` · `rumored` · `grid` (editorial; see the update plan) |
| `place`, `counties[]` | Display place, and county names exactly as in `geo.json` |
| `lat`, `lng` | Town or road level. The checker confirms the point falls in a listed county |
| `developer`, `facts[]` | Facts are `{k, v}` with optional `verify` (a reason; shows ⚠ Verify) |
| `latest` | `{d, t}`: the most recent development, as display text |
| `history[]` | `{d, status, t}` in date order. **Drives the map's time slider.** The last entry should match `status` |
| `timeline[]` | `{d, t, kind, src, next?, verify?}`. `kind` colors the dot (certified, violation, court, permit, hearing, psc, redaction, protest, money, company, community, government, media, context). `next: true` marks the pending step |
| `scale` | Optional dot art: `{n, unit, color, caption, src, extra?, big?, bars?}` |
| `redactions[]` | Optional `{label, why, src}`, only where information is actually withheld |
| `sources[]`, `checked`, `verify?` | Sources for the facts, the date they were last confirmed, and an optional project-level flag |

### `docket.json`
`{id, body, title, where, case, status, stage, stamp, tone, summary, projects[], counties[], next?, sources[], verify?, checked}`
- `body`: `courts` · `psc` · `dep` · `legislature`
- `stage`: `prefiling` · `open` · `briefing` · `awaiting` · `closed`
- `stamp` is the short rubber-stamp text; `tone` picks its color (`alarm`, `cyan`, `legal`, `signal`, `ok`, `grid`, `dim`)
- `next`: `{t, d, verify?}`. The front page and county sheets read it; the checker warns once `d` has passed
- `summary` may contain `<strong>` for names

### `events.json`
`{id, date, end?, start?, endt?, type, title, desc?, venue?, address?, virtual?, county, host?, how?, project?, sources[], flag?, approx?, tbd?, label?}`
- `type`: `hearing` · `psc` · `court` · `legislature` · `protest` · `community` · `government` · `developer`
- `tbd: true` = pending with no date. `approx: true` = date is a month or estimate (left out of .ics). `flag` = ⚠ Verify reason
- `county`: a county name or `Statewide`

### `standing.json`
`{body, county, rule, where, next?, projects[], url, verify?, note?}`. `rule` is the published schedule in plain words. `next` is a one-off posted date that should be confirmed or cleared every shift.

### `people.json`
`{id, group, name, role, projects[], sources[]}`. `role` may contain simple HTML (links).

### `network.json`
`{nodes: [{id, label, kind, sub?, project?}], edges: [{a, b, label, src, note?}], checked}`
- `kind`: `person` · `firm` · `company` · `project` · `case` · `group` · `law`
- Edges read left to right: `a` + `label` + `b` (for example: Peter Markham, "attorney at", Bowles Rice). **Every edge needs `src`.**

### Other files
- `lines.json`: transmission corridors `{id, name, short, note, pts[[lng,lat]], appears, appears_note, counties[], sources[]}`
- `desk.json`: dated desk log for the ticker, front page, and feed `{d, t, project?, src}`
- `hubs.json`: the "other AI story" feed. Hubs are the place list: `{id, name, label, tag, region, county, pop?, major, lat?, lng?, stories[]}`. Each story: `{title, html, sources[], d, dnote?, place, county, region, topics[]}`. `d` is the date of the story's newest dated source (YYYY, YYYY-MM or YYYY-MM-DD), or null with a `dnote` saying why (a profile page). `place` is a hub id, `"statewide"` for laws and programs that apply everywhere, or null for a county with no hub. `county` is a county name or null. `region` is the hub's region, `"Statewide"`, or one of `meta.hubRegions`. `topics` come from `meta.hubTopics`. Stories stay nested under the hub they were first filed in; `place` is what the feed uses. A story's `title` must match its Receipts row (`tools/check.py` fails the build if not). Feed URLs: `#/hubs?topic=research,grants&county=Cabell&sort=place&q=text` (`place`, `county`, or `region` takes one value)
- `receipts.json`: results of the Nov 2026 verification pass (`rows[]` with `sec`, `title`, `status`, `urls`, `note`)
- `news.json`: built by `tools/fetch_news.py`; don't edit by hand. `{updated, sources[], items[{id, d, title, url, source, summary, projects[], energy?, via, seen, story}]}`. `energy: true` marks the energy side of the beat (coal, gas, plants, utilities, PJM); the News page shows it as an Energy tag. `story` groups coverage of the same story (the item whose `id` equals `story` leads)
- `news-sources.json`: the collector's settings: `feeds` (outlet RSS), `searches` (Bing News RSS, whose links are unwrapped to the publisher, and Google News RSS limited to one outlet with `site:`, whose links redirect through news.google.com; `wvOutlet: true` means a West Virginia outlet, so its items need not name the state), `match` (beat terms), `energyMatch` (energy-side terms; matching items are kept and tagged `energy`), `wv` (West Virginia terms; all 55 county names are added automatically), `projects` (tagging words per project), `preferred` and `syndicators` (which copy leads a story), and `block` (URLs, hosts, or phrases to drop)
- `companies.json`: the Money Desk roster, hand-curated. `trendRule {pct, quarters}` (a trend arrow shows only after that many quarters in a row at least pct% above or below a year earlier), `tranches[]` (the four sections), `signals[]` (industry indicators: `kind` is `capex`, `fred` with a FRED series id, or `link`), `secSearch[]` (EDGAR full-text phrases, each tied to a project), and `companies[]`: `{id, name, tranche, also[]?, group?, listing (public, ipo, private, foreign, public-body), ticker?, exchange?, sec.cik? (10 digits), hq?, projects[], node? (people-web id), parent?, tie, sources[], facts[{k, v}]? with factsAsOf, risks[]?, catalysts[{t, d?, approx?, src, verify?}]? (events or open questions that could move the company or its projects; dated ones also go on the calendar and in calendar.ics unless approx), docket[]? (docket ids that concern the company beyond its projects; their dated next steps become catalysts automatically), unknown? (what isn't public), irUrl?, verify?, conflict?, selfConflict?, health {status: pending, stable, watch, stressed, nodata, or na; why; approved}, checked}`
- `filings.json`: built by `tools/fetch_filings.py`; don't edit by hand. `sec.<company id>` has `{cik, name, tickers, exchanges, filings[{form, d, accn, doc, period?, items[]?}], metrics{revenue, netIncome, capex: {concept, q[], fy[], ytd}; cash, debt: {concept, v, end, accn, form}}, factsFrom, factsChecked}`; `search.<phrase>` has `{total, hits[]}`; `fred.<series>` has `{last, yearAgo, monthly[[YYYY-MM, value]]}`. A quarter marked `derived` is a year-to-date figure minus the previous one
- `reads.json`: Rook's Reads, newest first. `{id, d, title, body[] (plain-text paragraphs with [n] markers), sources[{n, label, url}], companies[], projects[], anthropic, audio, mercer{status, d, tier, audit, duties{1..4}, notes}}`. The site shows only Reads whose `mercer.status` is `CLEARED`. Written by the daily desk task (`.claude/skills/rooks-read/SKILL.md`)
- `meta.json`: `updated` (bump every shift), site URLs, the four front-page `stats` (each with its source), and the Hubs feed's published lists: `hubTopics[{id, label}]` and `hubRegions[]` (`tools/check.py` rejects any story that uses a topic or region not listed here)
- `geo.json`: 55 county outlines and the state border (from the U.S. Census Bureau, via plotly/datasets). Built by `tools/build_geo.py`
- `wv-outline.json`: ordered border ring used by the image scripts in `assets/scripts/`
