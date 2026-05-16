# WV AI Hub Index

**An interactive single-page index of AI innovation across West Virginia.**

Live site: **[wvaihub.com](https://wvaihub.com)**

Built to help residents, researchers, employers, and policymakers see where AI, data-center, energy, and workforce activity is actually happening in the Mountain State — and to give grassroots groups, controversies, and emerging hubs the same visibility as the boosterish announcements.

Sections:
- **Major Hubs** (Morgantown, Fairmont, Charleston, Huntington, Berkeley County) — innovation stories per region with sources.
- **Emerging Hubs** (Parkersburg, Wheeling, Weirton, Princeton, Beckley, Clarksburg, Tucker County) — smaller hubs worth tracking.
- **Workforce Development** — Jobs, Education, Events, Grants across AI / Tech / Bitcoin / Solar with brief descriptions and links.

## Running it locally

No build step. Open it in a browser, or serve over HTTP for the canvas fonts to behave:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

That's the whole dev loop.

## Deploying

The live site auto-deploys via **Netlify** on push to `main`. The repo has no `netlify.toml` — Netlify just serves `index.html` as-is.

Forking and want a different host? It's a static single file plus `og-image.png`. Any of these work:
- **Netlify Drop** — drag the folder onto [app.netlify.com/drop](https://app.netlify.com/drop).
- **Cloudflare Pages** — connect the repo, set output to root, done.
- **GitHub Pages** — Settings → Pages → main branch root.
- **Vercel**, **Render**, etc.

## Fork it for your state or organization

The page is intentionally built as a single self-contained file so you can fork, find-and-replace, and ship a version for your state, region, or org. Here's exactly where to look in [index.html](index.html):

1. **State outline polygon** — the `WV` array (~line 716–718). Replace with a `[lng, lat]` array describing your state's border. You can extract one from a Natural Earth shapefile, the US Census TIGER files, or any GeoJSON state outline; convert to `[[lng,lat], ...]` pairs.
2. **Major hubs** — the `HUBS` array (~line 721–727). Five entries with `{ id, name, lat, lng, stories, capital? }`. Match each to a `<section class="city-section">` block below.
3. **Emerging hubs (population top-10ish)** — the `TOP10` array (~line 730–736). Update to your supporting cities.
4. **Background marker towns** — the `TOWNS` array (~line 741–806). The map's faint background dots. Add your towns and counties; the existing entries are WV-specific.
5. **City sections** — each `<section class="city-section">` block (~line 531–642). One per major hub. Update tag, name, story count, and the story-list bullets.
6. **Emerging hub cards** — each `<div class="future-hub-card">` (~line 650–720). One per emerging hub.
7. **Workforce Development panels** — the four `<div class="wf-panel">` blocks (Jobs, Education, Events, Grants). Replace cards with your state's resources. Theme chips are CSS classes `wf-chip ai|tech|btc|solar|civic|gov|research|transition`.
8. **Hero copy** — the `.hero-content` block (~line 509–512). Change the title and subtitle.
9. **Footer motto** — `Montani Semper Liberi` (~line 1124). Pick something local.
10. **SEO metadata** — `<title>`, `<meta name="description">`, all `og:` and `twitter:` tags at the top of the file.
11. **`og-image.png`** — replace with a 1200×630 social-card image for your fork.

After editing, `python3 -m http.server 8000` to preview, then push to your fork's `main`.

## Updating the news

Stories go stale fast. The repo includes a monthly news-refresh workflow in [DOCS.md](DOCS.md) — a copy-paste prompt you can schedule in [Cowork](https://www.anthropic.com/news/cowork) or run by hand. It web-searches for fresh sourced stories, inserts them at the top of each hub section (newest-first), bumps the story counts and footer date, and opens a draft PR for you to review.

## Contributing

PRs welcome:
- New sourced stories for existing hubs.
- New emerging hubs (need: name, region tag, county or population, ≥2 sourced stories).
- New Workforce Development cards (need: real URL, current/active program).
- Visual or accessibility improvements.

Please keep every story bullet **sourced with a working link** and **neutrally worded** — the site tracks developments, both positive and contested, and visitors deserve to see the full picture.

## License

No license has been set for this repository. If you fork it, please add an explicit license file to your copy.
