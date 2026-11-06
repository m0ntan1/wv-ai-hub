# Security and public-readiness scan: wv-ai-hub

**Date:** 2026-11-06 · **Branch scanned:** `main` @ `076b8ba` (128 commits, 137 tracked files) · **Fixes on branch:** `claude/inspiring-tesla-107ylb`

## Bottom line

**Safe to be public, with two things only you can do** (GitHub settings, see "Owner actions"). No credentials in the files or in any of the 128 commits. One real code weakness (a link-scheme gap in the news ingester) was found and fixed. Nothing was exploited: the live data has 0 bad links out of 70.

## Findings

| # | Severity | Finding | Status |
|---|---|---|---|
| M1 | Medium (latent) | **Untrusted RSS links could carry `javascript:` / `data:` schemes.** `fetch_news.py:clean_url` kept any scheme; `esc()` stops HTML injection but not a hostile `href`. A malicious or hijacked feed item would become a clickable script link on `#/news`. | **Fixed**: ingest rejects non-http(s) (`tools/fetch_news.py`); render allowlists via new `safeUrl()` (`assets/js/lib.js`, `views/news.js`, `srcLink`). |
| M2 | Medium | **No security headers** (no `_headers` / `netlify.toml`). | **Partly fixed**: added `_headers` (nosniff, frame deny, referrer, permissions, HSTS). **CSP still open**: `index.html` has inline scripts (theme boot, JSON-LD), so a CSP needs hashes first. |
| M3 | Medium | **Workflow least-privilege.** `check.yml` had no `permissions:` block (inherits repo default). `news.yml` interpolated step outputs straight into a shell line. Actions are pinned to tags, not commit SHAs. | **Fixed**: `check.yml` now `contents: read`; `news.yml` passes outputs via `env:`; added Dependabot for Actions. **Open**: SHA-pinning (needs network lookup I did not have). |
| M4 | Medium (design) | **Prompt-injection surface in the Rook's Read agent.** The skill ingests RSS headlines and scraped pages, and the agent can open PRs. Existing controls are good: headlines are "leads not facts," Firecrawl capped at 5 calls, the agent "never merges," a human reviews the PR. | **No code change.** Depends on the owner action below (branch protection) to be enforced rather than promised. |
| L1 | Low | **Personal email in git history.** 56 commits carry `rick@montanibitcoin.com` as author. Cannot be removed without rewriting history. | Decision for you. |
| L2 | Low | **ElevenLabs voice ID** printed in `docs/update-plan.md:170`. An identifier, not a credential. | Left as is; remove if you prefer. |
| L3 | Low | **Working files public:** `research/_raw-notes.md` ("working file") and `research/verification/*`. Contents are reported public-record facts; nothing private found. | Your call. Fine to keep as "receipts." |
| L4 | Low | **Licensing:** MIT covers code, but `data/news.json` holds third-party headlines/summaries (280 chars). | Add a data-license note if you want forks to reuse the data. |
| L5 | Low | **Repo growth:** `audio/rook/*.mp3` is ~3 MB per weekday, about 0.75 GB a year committed to git. | Move audio to Releases, Netlify, or a bucket before it matters. |
| I1 | Info | Google Fonts loaded from Google (visitor IP goes to Google). Contact form is Netlify Forms with honeypot. | Consider self-hosting fonts; a one-line privacy note. |

## What was clean

- **Secrets, full history:** regex sweep for OpenAI/ElevenLabs/GitHub/AWS/Google/Slack keys, private-key blocks, bearer tokens, `password=`/`secret=` over every revision. The only hits are `'xi-api-key': k` header lines in `tools/voice_read.py`, where `k` comes from `os.environ`. Also a 40+ character high-entropy sweep: only long URLs.
- **Sensitive filenames ever committed** (`.env`, `.pem`, `.key`, `secret`, `credential`, `token`): none, ever.
- **Secrets handling by design:** `.gitignore` blocks `.env*`; keys are read from environment only (`voice_read.py:81`, `fetch_filings.py:29`); the SEC user-agent is a repo secret.
- **XSS:** 50 `innerHTML` writes, all through the `esc()` helper for data fields (spot-checked news, money, calendar, people). No `eval`, `document.write`, or `new Function`.
- **Phones/emails:** only `@wvaihub.com` calendar addresses, the PSC notification address, the owner's published contact, and `you@example.com` placeholders.
- **Data integrity:** `python3 -I tools/check.py` returns 0 errors, 13 warnings (open "⚠ Verify" items the site discloses itself).

## Receipts: how this was done

```bash
git rev-list --all | wc -l                         # 128 commits covered
git grep -nIE '<key patterns>' $(git rev-list --all)   # secrets across every revision
git log --all --name-only --format= | sort -u | grep -iE '\.env|\.pem|secret|token'   # filenames ever committed
git grep -nIoE '<email regex>'                     # PII
grep -nE 'innerHTML|eval\(|document\.write' -r assets/js     # XSS sinks
python3 -I tools/check.py                          # data validation
```
M1 was **proved, not assumed**: `clean_url('javascript:alert(1)')` returned `javascript:alert(1)` before the fix and `''` after. After the fix a Playwright pass over `#/ #/news #/money #/docket #/calendar` showed 0 page errors and 0 `javascript:`/`data:` links.

## Assumptions, soft and hard blocks

**Hard blocks (could not check from here):**
- GitHub repo **settings**: visibility, branch protection, secret scanning and push protection, "Actions from fork PRs" policy, private vulnerability reporting, Actions secrets. No tool in this session reads them.
- Netlify settings (deploy-preview exposure, form notifications).
- Whether the live site at wvaihub.com matches `main`.

**Soft blocks (limited, not zero):**
- No gitleaks/trufflehog installed, so secret detection is regex plus entropy, not a dedicated engine. The GitHub secret-scanning tool wants file contents, not a repo path, so I did not run it. Treat "no secrets" as "none found by these patterns," and turn on GitHub secret scanning to get the real engine for free.
- Pattern sweeps skip binaries (mp3, png, webp, ttf).
- SHA-pinning was not done: resolving SHAs needs network lookups outside this repo's scope.

**Assumptions:** the owner email on the site is intentionally public; the repo is meant to stay MIT; `main` is the deploy branch.

## Owner actions (2 minutes, in GitHub Settings)

1. **Settings > Code security:** enable **Secret scanning**, **Push protection**, **Private vulnerability reporting**, Dependabot alerts.
2. **Settings > Branches > protect `main`:** require a pull request and one approval, block force-push. This is what makes "the agent never merges" a rule instead of a habit. Note `news.yml` pushes straight to `main` as `github-actions[bot]`; allow that bot to bypass, or the headline job will fail.
3. **Settings > Actions > General:** "Fork pull request workflows": require approval for first-time contributors; default token permissions: read.
4. Optional: GitHub account > Emails > "Keep my email addresses private" (affects future commits only).
