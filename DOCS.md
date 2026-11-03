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
  views/misc.js            #/projects, #/map, #/hubs, #/receipts, 404
  views/contact.js         #/contact     contact form (Netlify Forms; the hidden copy in index.html registers it at deploy)
  views/news.js            #/news        news aggregator, plus the front-page "In the news" section and each case file's news
data/*.json                The content. Edit these to update the site.
calendar.ics, feed.json    Built by tools/build_feeds.py from data/.
assets/qr/*.svg            County-sheet QR codes, built by tools/build_feeds.py.
tools/check.py             Validator: run before every publish.
tools/build_feeds.py       Builds calendar.ics, feed.json, QR codes, sitemap.
tools/build_geo.py         Builds data/geo.json from Census-derived county GeoJSON (run once; rerun only to change the boundaries).
tools/migrate/             One-time migration from the old single-file site (kept as a receipt).
research/                  Sourced dossier, calendar receipts, PSC watchlist, verification log and scripts.
design/                    Revamp proposal, concept board, screenshots.
docs/update-plan.md        How the site is kept current.
```

### Routes
Hash routes, so any static host works: `#/`, `#/map`, `#/projects`, `#/project/:id`, `#/docket`, `#/calendar`, `#/people`, `#/counties`, `#/county/:slug`, `#/hubs`, `#/receipts`, `#/contact`, `#/news`.
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
- `hubs.json`: the "other AI story" pages `{id, name, tag, pop?, major, lat?, lng?, stories[{title, html, sources[]}]}`
- `receipts.json`: results of the Nov 2026 verification pass (`rows[]` with `sec`, `title`, `status`, `urls`, `note`)
- `news.json`: built by `tools/fetch_news.py`; don't edit by hand. `{updated, sources[], items[{id, d, title, url, source, summary, projects[], via, seen, story}]}`. `story` groups coverage of the same story (the item whose `id` equals `story` leads)
- `news-sources.json`: the collector's settings: `feeds` (outlet RSS), `searches` (Bing News RSS, whose links are unwrapped to the publisher), `match` (beat terms), `wv` (West Virginia terms; all 55 county names are added automatically), `projects` (tagging words per project), `preferred` and `syndicators` (which copy leads a story), and `block` (URLs, hosts, or phrases to drop)
- `meta.json`: `updated` (bump every shift), site URLs, and the four front-page `stats` (each with its source)
- `geo.json`: 55 county outlines and the state border (from the U.S. Census Bureau, via plotly/datasets). Built by `tools/build_geo.py`
- `wv-outline.json`: ordered border ring used by the image scripts in `assets/scripts/`
