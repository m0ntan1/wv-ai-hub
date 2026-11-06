# Skeleton: turn WV AI Watch into a template for any state and any topic

**Status: design for your review.** Nothing below is built yet except the coupling measurements. You asked to iterate in Markdown first; once you approve this, step 1 of "Build order" starts.

## The idea in one paragraph

The site engine is already generic: static HTML plus JSON, no build step. What is *not* generic is the content, a handful of hard-coded constants, and the editorial rules. So the template is **one config file (`instance.json`) plus a scaffolder** that writes a fresh, valid-but-empty site for a given *state* and *topic*, with the checker green from minute one. The proof it works is not a doc; it is a test matrix that scaffolds N instances and runs the real tools against each.

## Measured coupling (matches in tracked files, so you can see the real work)

| Layer | WV / state refs | Topic refs (data center, HB 2014, microgrid) | Named-entity refs (Monarch, Rook, Mercer…) |
|---|---|---|---|
| `data/` | 565 | 766 | 389 |
| `assets/js/` (engine) | 41 | 19 | 63 |
| `tools/` | 54 | 77 | 73 |
| `index.html` | 37 | 7 | 3 |
| `research/` (receipts) | 424 | 500 | 165 |

Reading it: **`data/` and `research/` are content, so they are swapped, not edited.** The engine (`assets/js`, `tools`, `index.html`) has about 130 state-specific lines and about 100 topic-specific lines to turn into config. That is a tractable job, not a rewrite.

## The three seams (what `instance.json` has to carry)

**State seam** (swap to change geography)
- `tools/build_geo.py:19` `WV = '54'` (state FIPS) → `geo.json` counties + border; `data/wv-outline.json` for the social card.
- `tools/check.py:84` "marker is outside West Virginia" and the county checks.
- Footer/SEO/JSON-LD in `index.html`; calendar and feed titles in `tools/build_feeds.py:39,65,79,107`.
- News filter: `news-sources.json` keys `wv` (26 terms) and the county list from `geo.json`.
- Regulator vocabulary: PSC, DEP, county commissions, state legislature (`assets/js/lib.js` `BODIES`, `EV_TYPES`).

**Topic seam** (swap to change subject)
- `news-sources.json`: `match` (28), `energyMatch` (47), `projects` (14 keyword sets), `block`, and the 15 Google News queries (the query text embeds "data center OR microgrid OR coal…").
- Vocabulary: project statuses, event types, docket stages (`lib.js` `STATUS`, `EV_TYPES`), page headings in `views/*.js`.
- The Money tab: roster in `data/companies.json`, SEC queries in `data/filings.json` (`secSearch`), FRED series in `tools/fetch_filings.py`.
- Editorial rules in `.claude/skills/rooks-read/SKILL.md` (HB 2014 and PSC case numbers are baked into the prose).

**Persona/brand seam** (optional)
- Rook and Mercer are MØNTAN1 personas. For forks, ship the **role** (money-desk writer, auditor) with placeholder names and a `persona:` block, so nobody publishes under Rook Calloway by accident.

## Proposed skeleton (what the scaffolder emits)

```
instance.json              state, topic, site URL, repo, brand, regulator names, personas, feature flags
data/                      every file present, schema-valid, EMPTY (projects: [], events: [], …) + geo for the chosen state
tools/                     unchanged engine; reads instance.json instead of constants
tools/scaffold.py          NEW: instance.json -> writes data/, news-sources, index.html SEO, feeds titles, OG card
tools/smoke.py             NEW: the "does it run" test (below)
assets/js/                 unchanged engine; vocab loaded from data/vocab.json (new, from instance.json)
.github/workflows/         check.yml, news.yml (cron), both parameterized by repo
docs/TEMPLATE.md           10-step "new instance" checklist (replaces README fork section)
.claude/skills/<desk>/     desk skill generated from a template with topic rules filled in
SECURITY.md, _headers      carried over from the fixes in this branch
```

## How we will know it runs (test matrix)

`tools/smoke.py <instance>` does, for each scaffolded instance:
1. `scaffold.py` → fresh dir. **Pass:** `check.py` 0 errors on empty data.
2. `build_geo.py` for the state (needs Census download; cached copy offline). **Pass:** N counties found, border closes.
3. `build_feeds.py`. **Pass:** `calendar.ics`, `feed.json`, QR codes, sitemap build.
4. `fetch_news.py --dry-run` (new flag). **Pass:** ≥1 relevant item, 0 non-http links, 0 WV leakage in non-WV instances.
5. Playwright loads every route. **Pass:** 0 page errors; front page shows the instance's own state and topic.
6. **Leak test:** grep the output for `West Virginia|wvaihub|Monarch|Rook Calloway`. **Pass:** zero matches in non-WV instances. This is the check most likely to fail first and is the real measure of "template-ness."

**Matrix (proposed):**

| Run | State | Topic | What it proves |
|---|---|---|---|
| A | WV | data centers | The refactor didn't break the original |
| B | VA | data centers | **State seam works** (VA is the largest data-center market, so news volume is real) |
| C | OH | data centers | A second state, different regulator (PUCO) |
| D | WV | AI in schools | **Topic seam works** with state held fixed |
| E | PA | water/PFAS or housing (pick one) | Both seams moved at once, and no AI/energy assumptions remain |

## Assumptions and risks (disclosed up front)

**Hard blocks**
- **Per-state regulators and docket systems differ.** The PSC link/format logic (and "never scrape psc.state.wv.us") is WV-specific. A new state means new source rules, and these cannot be auto-generated. The skeleton gives you slots and a checklist, not the answer. The scaffolder cannot do the human work of finding each state's dockets.
- **SEC/FRED "Money Desk" is data-center-specific.** For non-finance topics it should be a feature flag (`features.moneyDesk: false`), and the Money tab and `fetch_filings.py` drop out cleanly. Needs verifying that nothing else imports it.
- **Network:** `build_geo.py` needs Census downloads and the live news test needs outbound RSS. This sandbox's proxy may block some outlets, so Run B–E news counts can be partial here and need re-running in your CI.

**Soft blocks / judgment calls**
- "Topic" is not a free variable. The page set (docket board, case files, county sheets) assumes **projects that move through regulatory stages with dated hearings.** Data centers fit that. "AI in schools" (Run D) fits less well, which is *why* it's a good test: if the engine only works for permit-fight topics, we find out and say so.
- The Rook's Read pipeline (daily audio essay, auditor persona, PR to editor) can be a template feature flag, but it carries editorial and conflict-of-interest rules (the Anthropic disclosure) that are specific to this site. Forks must write their own.
- AI personas and the "no AI in the fetch step" promise on `#/desk` are published claims. The template must keep them true for each instance, not copy WV's wording.

**Assumptions I made**
- You want a **template inside this repo** (`template/` or a `--init` mode), not a separate repo. A separate GitHub "template repository" is a reasonable alternative; say so and I'll package for that instead.
- "Different topics" means different *subjects on the same engine*, not a different kind of site.
- Tests run offline-first with fixtures, with live network as an optional second pass.

## Build order (after you approve)

1. **`instance.json` + `scaffold.py`**: extract the ~230 hard-coded lines into config. Run A must still pass byte-for-byte (diff of `data/`, `feed.json`, `calendar.ics`).
2. **`smoke.py` + leak test**, run on A. Fix leaks until clean.
3. **Run B (VA) and C (OH)**: state seam. Report what broke.
4. **Run D (WV schools) and E**: topic seam. Report honestly where the engine's assumptions show.
5. **Template docs** (`docs/TEMPLATE.md`), skill template, and one-click "Use this template" packaging.

## Decisions I need from you

1. In-repo `template/` or a separate GitHub template repo?
2. Run E topic: **water/PFAS**, **housing**, or your pick?
3. Personas: ship Rook/Mercer as the default, or placeholders only in the template?
4. Is `features.moneyDesk` off by default for non-finance topics?
