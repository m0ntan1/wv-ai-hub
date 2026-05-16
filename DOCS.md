# WV AI Hub Index — Operating Notes

This document covers two ongoing operational tasks for the maintainer:

1. **[Monthly News Refresh](#monthly-news-refresh)** — a copy-paste prompt for Cowork or any agent runner that pulls fresh sourced stories into the page.
2. **[Forking for another state](#forking-for-another-state-or-organization)** — step-by-step checklist for adapting this project to a different region.

The high-level project description lives in [README.md](README.md). This file is for the recurring work.

---

## Monthly News Refresh

The site's stories go stale within ~30 days. To keep it useful, run the following prompt monthly. It's self-contained — paste it whole into Cowork's scheduled-task creator (or any agent runner with web search + git access). Cowork handles the cadence; the prompt handles the work.

### Scheduling in Cowork

1. Open Cowork → Scheduled Tasks → "Create scheduled task."
2. Cadence: **monthly**, day 1, ~9:00 AM your timezone.
3. Repository: `m0ntan1/WV-AI-HUB-INDEX` (or your fork).
4. Paste the **Refresh Prompt** below as the task instruction.

### Refresh prompt

```
You are refreshing the WV AI Hub Index (index.html). Your goal: surface news from the
last 30 days as new sourced story bullets, sorted newest-first, while leaving the
site's structure and aesthetic intact.

PROCESS

1. Read index.html. Identify the section structure: 5 major hubs (Morgantown, Fairmont,
   Charleston, Huntington, Berkeley County), the emerging-hubs grid (currently 7 cards
   including Tucker County), and the Workforce Development section.

2. Run web searches for material from the last ~30 days on:
   - West Virginia AI policy, legislation, and Governor's office announcements
   - Data centers in WV (Penzance / Falling Waters, Fidelis Monarch / Mason Co.,
     Fundamental Data / Tucker Co., any new sites)
   - NOAA Fairmont / I-79 Technology Park / Rhea supercomputer
   - WVU, Marshall, WVU Tech, WVU-P, Eastern WV CTC AI and tech program news
   - Bitcoin mining or crypto policy news touching WV
   - Solar and just-transition workforce news in WV
   - Tucker United and other grassroots data-center responses
   - Generation WV, TechConnect WV, WorkForce WV, ARC, EDA grant announcements

3. For each story you'd add, gather:
   - A 1-2 sentence neutral lead with a strong opening clause in bold
   - A real working source URL (verify it loads)
   - The geographic hub or workforce subsection it belongs to

4. Edit index.html:
   - For hub sections: insert new <div class="story-item"> blocks at the TOP of the
     relevant <div class="stories-list"> (newest first). Pattern:
     <div class="story-item"><div class="story-bullet"></div><div class="story-text">
     <strong>LEAD</strong> — BODY.<a class="story-source" href="URL" target="_blank">
     Source: NAME, DATE →</a></div></div>
   - For emerging-hub cards: insert <div class="future-hub-story"> at the TOP of the
     relevant card's <div class="future-hub-stories">.
   - For Workforce Development: add new <div class="wf-card"> entries to the right
     wf-panel (#wf-jobs / #wf-education / #wf-events / #wf-grants). Use existing
     theme-chip classes (wf-chip ai|tech|btc|solar|civic|gov|research|transition).
   - Update each modified section's story-count number ("N innovation stories").
   - Update the footer line "Data compiled <Month YYYY>" to the current month.

5. Style/tone constraints:
   - Neutral wording, both positive and contested developments welcome
   - No AI/Claude attribution anywhere in the HTML, comments, commit, or PR body
   - No marketing language; one strong clause, one factual body sentence
   - Source labels follow "Source: PUBLICATION, MONTH YYYY →" format

6. Verify:
   - Start `python3 -m http.server 8000` and confirm the page loads without console
     errors. Verify the new stories render in the right sections.
   - Run `git grep -i "claude\\|anthropic\\|co-authored-by\\|generated with\\|🤖"` —
     it should return no hits in modified files.

7. Commit and push:
   - Branch: `news-refresh/YYYY-MM`
   - Commit message:
     ```
     Monthly news refresh — <Month YYYY>

     - <hub>: <N> new stories (newest first)
     - <hub>: ...
     - Workforce Development: <N> new entries
     - Footer date bumped to <Month YYYY>
     ```
   - NO Co-Authored-By line. NO "Generated with Claude Code" footer.
   - Open a draft PR titled "Monthly news refresh — <Month YYYY>" with a checklist
     body listing each story added and its source. NO AI attribution in the PR body.
   - Return the PR URL.

8. Do NOT merge. The maintainer reviews and merges manually.

ROLLBACK: if you can't find at least 3 new sourced stories across all sections,
do not commit. Report "no refresh needed" and exit.
```

### What to do when Cowork fires

The agent will open a draft PR. Review it for:
- Sources actually load and aren't paywalled-to-uselessness.
- Story leads aren't editorialized.
- New cards' theme chips make sense.
- Story-count badges actually match the new totals.

If the PR looks good, merge. Netlify will redeploy in ~1 minute.

---

## Forking for Another State or Organization

The README has the short version. Here's the file-by-file checklist with anchors.

### Files

| File | Action |
|------|--------|
| `index.html` | Edit in-place. Single source of truth for everything user-facing. |
| `README.md` | Replace project description, live-site link, hub list. |
| `DOCS.md` | Update this file's refresh prompt to mention your state. |
| `og-image.png` | Replace with a 1200×630 social-card for your fork. |

### index.html sections (line numbers approximate)

1. **`<title>` and meta tags** (lines ~1–22) — change `West Virginia — AI Innovation Map` to your name, update description, `og:image` path if you rename the file.
2. **`WV` outline polygon** (lines ~716–718) — replace the `[lng, lat]` array with your state's polygon. Sources for state outlines:
   - [Natural Earth](https://www.naturalearthdata.com/) (admin-1 states)
   - [US Census TIGER/Line](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
   - Convert GeoJSON to `[[lng,lat],...]` with `jq` or a quick Python script.
3. **`HUBS` array** (lines ~721–727) — 5 major hubs. `{ id, name, lat, lng, stories, capital? }`.
4. **`TOP10` array** (lines ~730–736) — supporting cities/regions for emerging-hub map markers.
5. **`TOWNS` array** (lines ~741–806) — faint background markers. Add your towns and counties.
6. **Major-hub sections** — five `<section class="city-section">` blocks. Update tag, name, story count, story bullets.
7. **Emerging-hub cards** — `<div class="future-hub-card">` entries inside `<div class="future-hubs-grid">`. Pop and region tag per card.
8. **Workforce Development panels** — four `<div class="wf-panel">` blocks. Replace cards with your state's job boards, schools, events, grants. Theme chips: `wf-chip ai|tech|btc|solar|civic|gov|research|transition`.
9. **Hero copy** (`<section class="hero">`) — title, subtitle.
10. **Footer motto** (`<p class="big-text">`) — pick a local phrase.

### After editing

```bash
python3 -m http.server 8000   # preview at http://localhost:8000
git add -A
git commit -m "Initial fork for <YourState>"
git push
```

Then point Netlify (or your host) at the repo. Done.

### License

The upstream repo has not set a license. If you fork, please add an explicit license file (`LICENSE.md`) — MIT, Apache 2.0, CC BY 4.0, or whatever fits your situation.
