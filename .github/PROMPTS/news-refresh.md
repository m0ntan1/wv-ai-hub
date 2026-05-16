# Monthly News Refresh — WV-AI-HUB

**Trigger:** First Monday of each month, 9 AM ET (cron: `0 13 1-7 * MON` UTC)
**Action:** Open a PR titled `News refresh — YYYY-MM`. Do NOT merge; leave for human review.

This document is a complete, self-contained prompt. Any scheduled AI agent (Cowork scheduled task, Claude Code `/schedule`, GitHub Actions running Claude, etc.) can execute it against this repository on the cadence above.

## Steps

1. **Inventory.** Read `index.html`. List every `<section class="city-section">` story-item and every `<div class="future-hub-card">` story.

2. **Find new stories.** For each region below, search for AI, tech, data-center, or Bitcoin news from the **last 60 days**. Only verifiable sources: university press releases, news outlets, government press releases, organization homepages, meetup pages.
   - Morgantown, Fairmont, Charleston, Huntington, Berkeley County
   - Parkersburg, Wheeling, Weirton, Princeton, Beckley, Clarksburg, Tucker County

3. **Verify existing stories.** WebFetch every `story-source` URL.
   - **404 / 403 / SSL error** → flag for removal in PR description.
   - **200 but article >18 months old** → flag for review.
   - **200 and current** → keep.

4. **Draft additions in house style.**
   - Format: `<strong>Title.</strong> 1-2 sentence summary. <a class="story-source" href="...">Source: Outlet, Mon YYYY →</a>`
   - **Zero em dashes.** Use periods, colons, or recasts.
   - No AI-stilted phrasing: avoid `leverage`, `robust`, `comprehensive`, `harness`, `delve`, `cutting-edge`, `next-generation`, `state-of-the-art`, `transformative`.
   - Match existing entries' length and tone.

5. **Re-sort** each section newest → oldest. Upcoming events lead. Evergreen org pages sink to the bottom.

6. **Resync counts.** Update both the `N innovation stories` HTML headers AND the JS `HUBS` array. If grand total changed, also update:
   - `assets/scripts/generate_og.py` (the stat number inside the script)
   - `index.html` meta description, og:description, twitter:description (`N+` references)
   - Run `python3 assets/scripts/generate_og.py` and commit the new `assets/og-image.png`.

7. **Update `assets/sitemap.xml` `<lastmod>`** to today's date.

8. **Open a PR.** Body should list:
   - Additions (one bullet per story, with the source URL and a sentence on why it qualifies).
   - Stale or broken items flagged for removal (human decides).
   - Files touched.
   - Test plan checklist (preview renders, counts match, og-image refreshed).

## Constraints

- One PR per refresh. **No auto-merge.**
- Do not modify the Mountain State Freedom Tech meetup entry — that is curator-managed.
- Do not touch `LICENSE`, `.gitignore`, `_redirects`, `README.md`, the site `<footer>`, or anything in `assets/scripts/fonts/`.
- If unsure about a story's accuracy, leave it out and note it in the PR body for human consideration. **Citation quality > story count.**
- If you cannot reach an external source, note it and skip rather than fabricate.

## Quality bar

A human reading the resulting PR should be able to merge it as-is, with no edits, in most months. The agent's job is to do the toil (search, verify, sort, count, regenerate); the human's job is editorial yes/no.
