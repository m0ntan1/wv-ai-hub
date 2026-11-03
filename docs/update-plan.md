# WV AI Watch: Update Plan

> Iteration 1 · Nov 3, 2026. A plan for keeping the site current and honest. It covers who does what, how often, from which sources, with which tools, and where the line is on claims.

## The goal in one paragraph
The site is only useful if its dates are right this week. Countdown chips, the "next" step on every docket card, and the county sheets all go stale fast. The plan is a short **weekly desk shift** (about 60–90 minutes) driven by a checker script that prints a to-do list, plus **same-day updates** for the handful of events that change the story. Automation drafts the work and a person approves it. Nothing publishes without a source.

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
| **Reporters and outlets**: Mike Tony (Gazette-Mail), Chris Schulz and Curtis Tate (WVPB), Brad McElhinny (MetroNews), Dan Parks (Country Roads News), Steve Pearson (Observer), WV Watch, Mountain State Spotlight, Valley North Record | `desk.json`, project `latest` and `timeline` | One Google Alert per project name and docket number, delivered as RSS | Weekly |
| **Community groups**: Tucker United, Mason WV United, Putnam United, WVDCAP, Stop Valley Link, WV CAG | `events.json` (town halls, protests) | Their sites and public event pages | Weekly |
| **Developers** (Valley Link open houses, Nscale) | `events.json`, labeled `developer` | Developer sites | Weekly |

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
5. **News sweep.** Write 3–5 desk items. Update `latest` on the projects that moved. Add timeline items, each with its own `src`.
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

---

## 5. Automation: what to automate and what stays human

| Tier | What | Status |
|---|---|---|
| **0. In the repo now** | `tools/check.py` (structure, references, dates, staleness, optional link check), `tools/build_feeds.py` (calendar.ics, feed.json, QR codes, sitemap), and `?today=` time travel for testing | Done |
| **1. Check every push** | A GitHub Action runs `check.py` and `build_feeds.py` on every push and pull request and fails on errors. Netlify deploy previews show each pull request before merge. | Ready to add (workflow file below) |
| **2. Weekly drafted shift** | A scheduled Claude task, Mondays early morning ET. It reads new PSC digests in Gmail, sweeps the sources in section 1, drafts the JSON edits and desk items on a branch, runs the checker, and opens a pull request whose description lists every source. **It never publishes.** You review and merge. | Needs your go-ahead |
| **3. Reach** | A "Send a tip or correction" link (mailto first, a form later). `calendar.ics` subscriptions and `feed.json` are already live. An email digest built from `feed.json` can come later. | Proposed |

What stays human: status labels, any new connection in the web, anything about a named private person, and the decision to publish.

### Tier 1 workflow file (`.github/workflows/check.yml`)
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
- **Tier 2 needs your approval.** A scheduled task runs in your account and reads your Gmail PSC digests. I won't create it unless you say so.
- **The PSC website blocks automated access** from this environment. PSC facts come from your subscription emails, so a missed email means a missed update.
- **The workflow file needs workflow permission on the repository.** If a push that adds it is refused, add the file through GitHub's web editor instead.
- **Some county sites don't publish schedules** (Mingo's is under construction; Grant and Mineral are inferred from agendas). Those stay ⚠ Verify until someone calls the clerk.

**Soft assumptions (overrule any of these)**
- About 60–90 minutes a week, on Mondays, plus same-day updates.
- Netlify keeps auto-deploying `main`, as it has so far.
- All times are Eastern. Readers' "today" comes from their own clock.
- Browsers may cache the site's scripts for a while after a deploy. When a release changes code (not just data), bump the `?v=` value in `index.html`.

## 8. Decisions for you
1. **Cadence:** is a Monday shift right, or should it be another day?
2. **Tier 2:** should I set up the weekly scheduled task that drafts a pull request?
3. **Corrections:** should corrections get their own section on the Receipts page, or stay in the verification log?
4. **Tips:** a plain mailto link to start, or a form?
