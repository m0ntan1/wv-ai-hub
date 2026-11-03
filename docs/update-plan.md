# WV AI Watch: Update Plan

> Iteration 3 · Nov 3, 2026 (adds the Money Desk: SEC filings, the Money tab, and Rook's Read). A plan for keeping the site current and honest. It covers who does what, how often, from which sources, with which tools, and where the line is on claims.

## The goal in one paragraph
The site is only useful if its dates are right this week. Countdown chips, the "next" step on every docket card, and the county sheets all go stale fast. The plan is a short **weekly desk shift** (about 60–90 minutes) driven by a checker script that prints a to-do list, plus **same-day updates** for the handful of events that change the story. Automation drafts the work and a person approves it. Nothing publishes without a source.

## How it all fits together

**Every three hours, the news refreshes itself.** A GitHub job (`.github/workflows/news.yml`) runs `tools/fetch_news.py`. It reads 18 West Virginia outlets plus 8 targeted Bing News searches and keeps only stories that are about this beat and mention West Virginia. It tags each story with the projects it names and groups coverage of the same story under one lead headline. If anything is new, it commits `data/news.json` to `main`, and Netlify republishes the site within seconds. The front page's "In the news" section, the News page, and each case file's news section update without anyone touching them. No AI model is involved and it costs nothing. Every headline is labeled as the outlet's own words, unchecked.

**In the same job, the money data refreshes.** `tools/fetch_filings.py` reads SEC EDGAR for every company on the Money tab's roster (`data/companies.json`): new filings, plus revenue, net income, capital spending, cash, and debt from each company's structured (XBRL) data. It also runs EDGAR full-text searches for filings that name a West Virginia project, and pulls the Henry Hub gas price, the federal funds rate, and the 10-year Treasury yield from the Federal Reserve's FRED database. It writes `data/filings.json` only when something changed. The SEC requires automated readers to identify themselves, so the job reads a contact from the `SEC_USER_AGENT` repository secret; the contact is never written to the repository or the site. Without the secret, it skips the SEC and keeps the old data. Headlines and filings are the only parts of the site that publish without a person.

**Every weekday at 6:17 a.m. Eastern, Rook drafts the day's Read.** The scheduled task "WV AI Watch: Rook's Read (daily draft PR)" starts a fresh Sonnet session that follows `.claude/skills/rooks-read/SKILL.md`. Rook Calloway (an AI persona) reads the past day's headlines and filings and the site's own records, and writes up to 850 words, fewer on a quiet day, with a numbered source for every fact. Then Mercer Lang (also a persona) reviews it: his makenomistakes audit at the Heavy tier, with an independent subagent, and his four duties (source authority, quotes, not-investment-advice framing, and fair comment). He stamps it CLEARED, CONDITIONAL (fixed and re-checked in the same run), or HOLD. The draft arrives as a pull request with Mercer's review and any proposed health-read changes. **Nothing publishes until you merge it**, and the site never shows a Read that isn't CLEARED.

**Every Monday at 5:43 a.m. Eastern, a Sonnet session does the verified work.** The scheduled task "WV AI Watch: weekly desk shift (draft PR)" starts a fresh session on Sonnet 5.5, with this repository attached and the Gmail and Firecrawl connectors. It reads this plan and `DOCS.md` and works on its own branch. It runs `tools/check.py` first, and the warnings are its to-do list: docket deadlines that have passed, records not re-checked in 45 days, open ⚠ Verify items, and one-off county meeting dates. Then it works through the sources:
- **PSC emails:** your case-subscription digests from the past eight days. It moves docket cards, adds hearings and deadlines, and cites the PSC document link for each change.
- **News:** the headlines the three-hour job gathered that week. It opens each story worth keeping, confirms it, and turns it into a desk-log entry or a project timeline entry with that article as the source.
- **Official pages:** DEP notices, the Legislature's schedule, and the 17 county agenda pages, for new dates.

To keep costs down it reads pages with the built-in web fetch first. It uses Firecrawl only for pages that block plain fetching, need JavaScript, or are PDFs, with a hard cap of 25 Firecrawl calls a run. If Firecrawl is out of credits, it carries on without it and says so. It never touches the PSC website, which blocks automated tools; PSC facts come only from your emails.

It marks what it re-confirmed, runs the checker until there are no errors, and rebuilds the calendar feed and county QR codes. Before anything goes out, it runs **Mercer's makenomistakes audit** (`.claude/skills/makenomistakes`, from [m0ntan1.com](https://m0ntan1.com/skills/makenomistakes)) at the Heavy tier. Every changed fact is re-checked against its source and marked CONFIRMED, CONTRADICTED, or UNVERIFIABLE, and a fresh subagent with no memory of the run audits the work independently. Contradicted facts are fixed before the pull request opens. Unverifiable ones are listed, never buried. Then it opens a pull request titled "Desk shift: week of …" that lists every change with its source and ends with Mercer's audit footer.

It is fenced in by the rules in section 4. It cannot change a project's status, add connections to the people web, or add anything about a named private person; those go into a "Needs your call" list with its suggestion and source. A new docket card for a newly subscribed PSC case also goes under "Needs your call". It never merges. If nothing changed, it opens no pull request and says so.

**The pull request is where you come in.** As soon as it opens, GitHub runs the data check again as a second gate, and Netlify builds a preview: a full working copy of the site with the changes applied, at its own link. You read the change list, click through the preview, decide the "Needs your call" items, and merge. Netlify publishes to wvaihub.com in about 20 seconds, and everything downstream updates at once: the countdowns, the docket board, the county sheets, the `calendar.ics` that subscribers' calendars pull about twice a day, and `feed.json`. What used to be a 60–90 minute shift becomes a 15–30 minute review.

**Between Mondays, big moments don't wait.** A PSC order, a permit decision, a court ruling, a new certification, or a hearing announced on short notice gets a same-day update. Either ask Claude in a session to draft it, or edit the data yourself. It goes through the same pull request, check, preview, and merge path. Tips and corrections from readers come in through the contact form (`#/contact`). They collect in the Netlify dashboard under Forms, or in your inbox if you turn on Netlify's email notifications. Anything you act on goes through that same path, and corrections are logged publicly.

**On a slower rhythm:**
- **Monthly:** a link check (`tools/check.py --links`) to replace dead sources, a pass at every ⚠ Verify item, and a look at the county meeting schedules.
- **Every quarter:** a full verification pass like the November one.
- **During the legislative session (Jan 13 – Mar 13, 2027):** bill tracking needs to be daily, which the weekly task doesn't cover. Either you take it on, or we add a temporary daily task for those two months.

**When something breaks, it fails loudly or harmlessly:**
- **A dead outlet feed** gets skipped; the news job keeps running.
- **A failed news run:** GitHub emails you, and the checker warns when headlines are more than a week old.
- **No Gmail or no Firecrawl credits:** the Monday task says so at the top of its pull request and does what it can without them. Each pull request reports "Firecrawl calls used: N of 25".
- **No pull request on a Monday** means either nothing changed (its summary says so) or the run failed.
- **An off-topic headline** goes on the `block` list in `data/news-sources.json` and never comes back.

---

## 1. Where updates come from

| Source | Feeds | How to get it | How often |
|---|---|---|---|
| **PSC Case Subscription emails** for 26-0075 (MARL), 26-0108 (Fort Martin), 25-0450 (FRR), 25-0857 (IRP), 26-0633 (capacity rule), 24-0611 (large-load tariff), FP Valley Link 26A | `docket.json` (stage, stamp, next), `events.json` (hearings, deadlines), `desk.json` | Gmail digests, already subscribed. See `research/psc-subscription-watchlist.md` for the full list and tiers | Weekly. Same day for an order or decision |
| **DEP public notices** (air permits R14-0042 Monarch, the Google Buffalo application, Ridgeline; stormwater; enforcement) | `docket.json`, `events.json` (hearings, comment deadlines), project `timeline` | DEP DAQ public notice page and DEP news releases | Weekly |
| **Legislature** (interim schedules and agendas; 2027 bills to repeal or amend HB 2014) | `events.json`, `docket.json` (legislature) | wvlegislature.gov interim schedule and bill status pages | Weekly. **Daily during the session, Jan 13–Mar 13, 2027** |
| **Courts** (Barks v. Silicon Foundation; Ridgeline appeals being refiled; new EPCRA suits in Mingo) | `docket.json`, project `timeline` | Court reporting by the reporters below, plus counsel's public updates (WVHC, Appalachian Mountain Advocates) | Every two weeks, or on news |
| **County commissions** (17 bodies in 14 counties) | `standing.json` (`next`), `events.json` (any data-center agenda item) | The agenda link stored on each record in `standing.json` | Weekly |
| **Governor / Commerce** (certifications, the Data Center Advisory Council) | New projects, `history`, `timeline` | governor.wv.gov releases | On news |
| **News aggregator** (`tools/fetch_news.py`): 18 outlet feeds plus Bing News searches, filtered to this beat and grouped by story | `news.json` (front page "In the news", `#/news`, case files) | Automatic: just run the script | Each shift, or on a schedule (see section 5) |
| **Reporters and outlets**: Mike Tony (Gazette-Mail), Chris Schulz and Curtis Tate (WVPB), Brad McElhinny (MetroNews), Dan Parks (Country Roads News), Steve Pearson (Observer), WV Watch, Mountain State Spotlight, Valley North Record | `desk.json`, project `latest` and `timeline` | One Google Alert per project name and docket number, delivered as RSS | Weekly |
| **Community groups**: Tucker United, Mason WV United, Putnam United, WVDCAP, Stop Valley Link, WV CAG | `events.json` (town halls, protests) | Their sites and public event pages | Weekly |
| **Developers** (Valley Link open houses, Nscale) | `events.json`, labeled `developer` | Developer sites | Weekly |

### 1a. PSC case subscriptions: what's covered and what to add

The PSC emails are the backbone of the docket. They are also the only way to follow PSC cases, because the PSC website blocks automated tools. Anything you are not subscribed to, the site will miss.

**Covered now.** As of Nov 3, 2026 there is one subscription, "Maidsville / Fort Martin CPCN". Its digests carry these cases:

| Case | What it is |
|---|---|
| 26-0075-E-CN | MARL 500 kV line (NextEra) |
| 26-0108-E-CN | Fort Martin / "Maidsville Energy Center" gas plant (Mon Power / Potomac Edison) |
| 25-0450-E-GI | PJM capacity market / AEP "FRR" investigation |
| 25-0857-E-IRP | Mon Power / Potomac Edison resource plan |

**Add, in this order.** Full reasoning and sources are in `research/psc-subscription-watchlist.md`. These case numbers come from legal notices and news reporting because the PSC site was blocked, so confirm each one in Case Information before subscribing.

| Priority | Case | Why |
|---|---|---|
| 1 | **26-0633-E-GI** · HB 2014 generating-capacity rules | The PSC's own HB 2014 rulemaking; already on the docket board, but only through news |
| 1 | **FP Valley Link 26A** · Valley Link comment file | Holding file for protests. When Valley Link files its formal application, subscribe to the new `E-CN` number the same day |
| 1 | **25-0859-E-IRP** and **25-0860-E-IRP** · Appalachian Power and Wheeling Power resource plans | Where ApCo's forecast of up to 8,000 MW of new large load gets tested |
| 1 | **Data-center special contracts** (not filed yet) | FirstEnergy says it will serve data centers through special contracts needing PSC approval. If the subscription system allows criteria, add Mon Power, Potomac Edison, Appalachian Power, and Wheeling Power with keywords such as *special contract*, *data center*, *large load*, *microgrid* |
| 2 | **26-0508-E-42T** · Mon Power / Potomac Edison base-rate increase | Household-bill context; second step Jun 1, 2027 |
| 2 | **Mon Power 2026 ENEC** (look up the `26-xxxx-E-ENEC` number) and the next **ApCo ENEC** | Where PJM capacity costs, pushed up by data-center demand, reach bills |
| 3 | **26-0130-E-CN** · Mitchell plant cooling tower (optional) | Coal-plant life extension under HB 2014's policy |

**How to add one:** on psc.state.wv.us, go to **Case Information**, search the case number, open the case, and choose **Subscribe to Case**. Or use the "Modify" link in any digest email to edit your subscription criteria.

**What happens after you subscribe.** Nothing else needs setting up. The new case starts appearing in the daily digests, and the Monday task reads every digest from `docketnotify@psc.state.wv.us`. The first time it sees activity in a case with no card on the docket board, it drafts one, with the case number, stage, stamp, next date, and the PSC document link. It lists that card under "Needs your call", and you approve it when you merge. Also move the case into the "Already in your digests" table in the watchlist, so the record of what you follow stays current.

---

## 2. The weekly desk shift (Mondays)

The checker's warnings are the shift's to-do list. Run it first:

```bash
python3 -I tools/check.py
```

1. **Pull and check.** Read every WARN line: a docket "next" date that has passed, a record not re-checked in 45+ days, an open ⚠ Verify, a "next posted" county meeting date that needs confirming.
2. **PSC.** Work through new digests. Move docket cards (`stage`, `stamp`, `next`), add hearings and deadlines to `events.json`, and add one `desk.json` line per real development.
3. **DEP and Legislature.** Add hearings and comment deadlines. Update permit cards.
4. **Counties.** Open the agenda link for each of the 17 standing meetings. Update or clear `next`. Any data-center item becomes an event.
5. **News sweep.** Run `python3 -I tools/fetch_news.py`, then read the new headlines on `#/news`. Promote what matters into 3–5 desk items (with the story itself as the source), and add any off-topic URL or phrase to `block` in `data/news-sources.json`. Update `latest` on the projects that moved. Add timeline items, each with its own `src`.
6. **Stamp what you re-checked.** Set `checked` to today on every record you confirmed against its source, and bump `meta.updated`.
7. **Check again** until it reports 0 errors.
8. **Build the published files:**
   ```bash
   python3 -I tools/build_feeds.py
   ```
   This writes `calendar.ics`, `feed.json`, the county QR codes, and the sitemap.
9. **Preview:**
   ```bash
   python3 -m http.server 8000
   ```
   Open `http://localhost:8000`. Check the front-page countdowns and every case file you touched. Add `?today=YYYY-MM-DD` to the URL to see the site as of another day.
10. **Commit and push.** List the sources in the commit message. Netlify deploys from `main`.

### Same-day updates (don't wait for Monday)
A PSC order or decision, a DEP permit decision, a new state certification, a court ruling, a hearing announced less than 10 days out, or a correction.

### Monthly (first Monday)
- `python3 -I tools/check.py --links` finds dead sources. Replace each with an archived copy (web.archive.org) or a better source.
- Re-try every ⚠ Verify item. Clear the flag when a source confirms it, and log it.
- Re-confirm the meeting rules in `standing.json`.
- Review the status labels. They are editorial calls (see section 4).
- If the headline numbers changed, regenerate the social image with `assets/scripts/generate_og.py`.

### Session mode (Jan 13 – Mar 13, 2027)
Do a daily bill check. Each bill that touches HB 2014, data centers, microgrids, or local control gets a docket card (`body: legislature`). Committee hearings and floor votes become events.

---

## 3. Recipes: how to make each kind of edit

All data lives in `data/*.json`. The schema for each file is in `DOCS.md`. Times are 24-hour Eastern.

- **Add an event.** Copy an existing entry in `events.json`. You need `id` (unique, kebab-case), `type`, `title`, and `date` (or `tbd: true`). Add `county`, `project`, `venue`/`address`, `how` (how to take part), and `sources`. If anything is unconfirmed, put the reason in `flag`; that shows ⚠ Verify on the site and in the .ics file. Use `approx: true` when only the month is known.
- **Move a docket card.** Change `stage` (prefiling → open → briefing → awaiting → closed), `stamp`, and `next` (`{t, d}`). Add the event to the project's `timeline` with its `src`, and add a `desk.json` line.
- **Change a project's status.** Append a `history` entry (`{d, status, t}`) and set `status`. The map's time slider reads `history`, so the date matters.
- **Add a project.** Add it to `projects.json` with `history`, `timeline`, `sources`, `counties`, and a town-level `lat`/`lng`. The checker confirms the marker falls inside the listed county. Add people and `network.json` connections, each with a source. Add the county's standing meeting if it is missing, then rerun `build_feeds.py` for the QR code.
- **Add a connection.** In `network.json`, add `{a, b, label, src}`. The label must say only what the source says. The checker rejects a connection without a source.
- **Correct something.** Fix the data. Add a line under *Corrections* in the current verification log (`research/2026-11-verification-log.md`, or a new monthly log). If the error was material, add a desk item that starts with "Correction:". Corrections stay public.

---

## 4. Verification rules (the line we don't cross)
1. **No claim without a source the reader can open.** The checker enforces this for projects, docket cards, connections, the desk log, and hub stories.
2. **The source must actually say it.** Numbers, names, and dates have to appear in the linked source. The Nov 2026 pass checked 202 items this way. Repeat that pass every quarter.
3. **One weak source means ⚠ Verify,** with the reason written out. The flag stays visible until a better source confirms it.
4. **Private residents appear only as counts** (for example, "2,000+ protest signatures"). Residents named in published reporting can be named, with that report linked. Individual PSC filers are never named.
5. **Quotes are exact** and link to where they were said.
6. **Connections are documented relationships only.** Never infer one. The web's caveat stays on the page.
7. **Redaction bars only where the law or the filer actually withheld information.**
8. **Status labels are editorial** (Under construction, Contested, and so on). The dossier says so, and the label changes only with a dated, sourced event in `history`.
9. **The PSC website blocks automated tools.** Confirm PSC facts from the subscription emails, and say so (`psc-notice` in receipts).
10. **Nothing ships without an audit.** Every automated run that drafts site content ends with Mercer's makenomistakes audit (`.claude/skills/makenomistakes/SKILL.md`). The author never signs off on its own work, and a failed check must change the outcome: a CONTRADICTED fact is fixed or dropped before the pull request opens. Its footer goes in the pull request description. Run it yourself after hand edits: in Claude Code, type `/makenomistakes`.

---

## 5. Automation: what to automate and what stays human

| Tier | What | Status |
|---|---|---|
| **0. In the repo now** | `tools/check.py` (structure, references, dates, staleness, optional link check), `tools/build_feeds.py` (calendar.ics, feed.json, QR codes, sitemap), and `?today=` time travel for testing | Done |
| **1. Check every push** | A GitHub Action (`.github/workflows/check.yml`) runs `check.py` and `build_feeds.py` on every push and pull request and fails on errors. Netlify deploy previews show each pull request before merge. | Done. The first run passed on Nov 3, 2026 |
| **1b. News refresh on a schedule** | `.github/workflows/news.yml` runs `tools/fetch_news.py` every 3 hours (at :17 past, UTC) and commits `data/news.json` when there are new headlines, so the news section stays current between shifts. Headlines only; nothing else changes. No AI model is involved, and it is free on GitHub Actions for a public repository. Pause it from the Actions tab. | Done. Approved Nov 3, 2026 |
| **2. Weekly drafted shift** | A scheduled Claude task ("WV AI Watch: weekly desk shift (draft PR)"), **Mondays at 5:43 a.m. Eastern, on Sonnet 5.5**. It reads new PSC digests in Gmail, the week's headlines in `news.json`, and the official pages; drafts the JSON edits and desk items on a `desk/<date>` branch; runs the checker; and opens a pull request whose description lists every source plus a "Needs your call" section for status changes, new connections, and anything about a named person. **It never merges or publishes.** You review and merge. | Scheduled. First run Nov 9, 2026. Repository, Gmail, and Firecrawl attached Nov 3 |
| **1c. SEC and FRED data** | `tools/fetch_filings.py`, in the same 3-hour job. Needs the `SEC_USER_AGENT` secret. | Built Nov 3, 2026. Waiting on the secret |
| **2b. Daily Rook's Read** | A scheduled Claude task, **weekdays at 6:17 a.m. Eastern, on Sonnet 5.5**, following `.claude/skills/rooks-read/SKILL.md`. Opens a `rook/<date>` pull request; never merges. Firecrawl capped at 5 calls a run. | Scheduled Nov 3, 2026. Attach the repository (and Firecrawl, if wanted) in the task settings |
| **2c. Audio** | `tools/voice_read.py` voices a cleared Read with ElevenLabs once `ELEVENLABS_API_KEY` and `ROOK_VOICE_ID` are in the cloud environment's secrets. | Built, not yet run against the live API |
| **3. Reach** | The contact form at `#/contact` (question, tip, or correction) is live and handled by Netlify Forms. Every case file has a "Report an error" link. `calendar.ics` subscriptions and `feed.json` are live. An email digest built from `feed.json` can come later. | Contact form done; digest proposed |

What stays human: status labels, any new connection in the web, anything about a named private person, every Rook's Read, every health read on the Money tab, any change to the company roster, and the decision to publish.

### The Money Desk rules
- **Roster** (`data/companies.json`): a company joins only with a sourced tie to a West Virginia project, or as a labeled industry indicator. Private companies get "what isn't public" instead of a guess. Facts typed from an S-1 carry `factsAsOf`.
- **Health reads** (Stable / Watch / Stressed) describe financial condition from filings, never motives. They start as "Read pending" and change only when you approve one: set `health.status`, `health.why`, and `health.approved` (the checker refuses a published read without them).
- **Rook's Read** must pass `tools/check.py`: 850 words at most, a source for every `[n]`, Mercer CLEARED, no em dashes, no buy/sell or price-target language.
- **The Anthropic conflict:** Rook and Mercer run on Claude, made by Anthropic, Monarch's anchor tenant. Anthropic is covered like every other company, with a standing disclosure on every Read and on the Money tab, a stronger one on its own page, and figures only from its own filings.
- **The weekly shift** also looks at `data/filings.json` for roster companies with a new S-1/A, final prospectus (424B4), or an 8-K with items 1.03, 2.03 to 2.06, 3.01, or 4.02, and proposes updates to the curated facts under "Needs your call".

### Tier 1 workflow (now in `.github/workflows/check.yml`)
```yaml
name: check-data
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install segno
      - run: python3 -I tools/check.py
      - run: python3 -I tools/build_feeds.py
      - run: git diff --stat   # shows if published files were out of date
```

---

## 6. Known dates to staff (next ~4 months)
From `data/events.json` and `data/docket.json`. The checker warns after each one passes.

| Date | What | Note |
|---|---|---|
| Nov 4–19 | Valley Link open houses (9 towns) | Developer-run, not hearings |
| Nov 9–11 | Legislative interims | |
| Nov 10 | Rule-Making Review Committee: PSC capacity rule (150 CSR 41) | Update the 26-0633 card afterward |
| Nov 23 | MARL initial briefs ⚠ | Confirm against a PSC order |
| Dec 1 | Mon Power IRP data due (25-0857) | |
| Dec 4 | MARL reply briefs ⚠ | |
| Dec 6–8 | Legislative interims | |
| ~Dec 29 | PSC Staff recommendation on AEP's FRR status (25-0450) | |
| Jan 13, 2027 | Regular session convenes | Switch to session mode |
| Jan 26, 2027 | WV Rally for Affordable Energy | |
| Feb 2027 | Fort Martin decision deadline ⚠ | Reported, not yet confirmed |
| Mar 6, 2027 | PSC decision due on MARL | |
| Mar 13, 2027 | Session ends | |
| No date yet | Monarch air permit decision, Ridgeline appeals refiled, next Barks hearing, Valley Link formal application, Data Center Advisory Council launch | Watch weekly |

---

## 7. Blocks and assumptions

**Hard blocks**
- **SEC contact secret:** add `SEC_USER_AGENT` (for example `WV AI Watch you@example.com`) under the repository's Settings > Secrets and variables > Actions. Until then the 3-hour job refreshes FRED but not the SEC.
- **Rook's voice:** audio needs an ElevenLabs API key and a saved Rook voice in the cloud environment's secrets. At the 850-word cap a Read is about 5,000 characters, so budget roughly 2,500 credits per full-length Read on the Flash model (about twice that on the multilingual model).
- **The PSC website blocks automated access** from this environment. PSC facts come from your subscription emails, so a missed email means a missed update.
- **Some county sites don't publish schedules** (Mingo's is under construction; Grant and Mineral are inferred from agendas). Those stay ⚠ Verify until someone calls the clerk.

**Soft assumptions (overrule any of these)**
- Firecrawl runs on prepaid credits, capped at 25 calls per weekly run. Keep the balance topped up; when it runs dry, the task falls back to plain fetching and pages that need JavaScript (many county agendas) get skipped.
- About 60–90 minutes a week, on Mondays, plus same-day updates.
- Netlify keeps auto-deploying `main`, as it has so far.
- All times are Eastern. Readers' "today" comes from their own clock.
- Netlify tells browsers to recheck every file on each visit (`max-age=0, must-revalidate`), so deploys show up right away. The `?v=` value in `index.html` only matters if that ever changes.

## 8. Decisions
**Made (Nov 3, 2026):** the Money Desk is on: four tranches (The Industry, The Companies, The Backers, The Shovel Sellers); SEC filings via EDGAR; Rook's Read every weekday as a pull request you approve; Mercer's Duty 4 (fair comment and libel) added; Anthropic covered in full with a conflict disclosure; Reads capped at 850 words. The weekly shift runs Mondays; the weekly drafted pull request is on (Sonnet 5.5, with the repository, Gmail, and Firecrawl attached; Firecrawl capped at 25 calls a run); headlines refresh automatically every 3 hours; tips and corrections come in through the contact form.

**Still open:**
1. **Corrections:** should corrections get their own section on the Receipts page, or stay in the verification log?
