# WV AI Watch: Revamp Proposal (draft, Nov 3, 2026)

> Iteration 1, in Markdown. The visual concept board (`design/concept-board.html`, screenshots in `design/screens/`) shows the key screens with real data. Nothing on the live site changes until a direction is picked.

## The shift
The old site was a **booster map**: glowing hubs, innovation stories, a jobs board. The research turned it into a **watchdog**: 13 projects, 7 PSC dockets, 3 court fights, 51 public dates, 52 named people, and a verification log. The design should say *accountability desk*, not *tech brochure*.

**Working name for the direction: "The Watch Desk."** It's a night-shift newsroom for West Virginia's AI buildout. It leads with what's happening and when you can show up, makes the scale physical, and puts its receipts on everything.

---

## Seven design principles
1. **Lead with what's live, not with a pretty map.** The first screen answers "what's happening this week, and where can I be?"
2. **One spine: place × time.** A single map with a time scrubber ties every project, hearing, permit, and protest together.
3. **Everything is a case file.** Each project gets a dossier that pulls in its timeline, permits, court cases, people, upcoming dates, and sources. Today the same facts are spread across four sections.
4. **Make the scale physical.** "864 engines" is abstract; 864 dots is not. Convert numbers into things people can see.
5. **Follow the connections.** People, firms, projects, and cases form a web. Show it, with a source on every connection.
6. **Receipts are a feature, not a footnote.** Verification status sits on every item. "⚠ Verify" is honest and visible.
7. **Built for showing up.** Comment deadlines get urgency. Every date can be downloaded as `.ics`. Every county gets a printable one-pager to bring to the commission meeting.

---

## Signature features (the wild swings)

| # | Feature | What it does | Why it matters |
|---|---|---|---|
| 1 | **Countdown masthead** | Front page opens on a strip of live countdown chips: *Valley Link open houses: tomorrow · Rule-Making Review on the PSC rule: 7 days · MARL decision: 123 days*. Computed from the viewer's date. | Turns the site from an archive into a reason to come back weekly. |
| 2 | **Time scrubber map** | Drag from **2025** (HB 2014 becomes law) to **Mar 2027**. Projects appear when announced, certifications stamp in, permits land, protests pulse, corridors draw. Autoplays once on load. | Shows in 10 seconds how fast this happened. Nothing else tells the story that quickly. |
| 3 | **Case files** | Folder-tab dossier per project: *Overview · Timeline · Permits & cases · People · Take part · Receipts.* Each has a shareable deep link (`#/project/monarch`). | One link to send a neighbor. Ends the hunting across sections. |
| 4 | **Redaction bars** | Where information is actually withheld by law, show it as a black bar: e.g. certification petitions confidential under HB 4983. Hover: "Withheld under HB 4983." | Makes secrecy visible without editorializing. Used only where it's factually true. |
| 5 | **Docket stamps + stage board** | Courts and PSC cases as a kanban board: *Filed → Hearings → Briefing → Awaiting decision → Decided*, with rubber-stamp marks (PENDING, DISMISSED, DECISION DUE MAR 6). | Answers "where does each fight stand?" at a glance. |
| 6 | **Scale units** | Interstitial data art: 864 engine dots (Monarch), 2,250-acre footprint overlaid on Point Pleasant, 30 million gallons of diesel (Ridgeline) as tanker-truck units, 2,000+ protest signatures as a crowd. | Numbers people can feel, each with its source. |
| 7 | **Connections web** | Force-directed network of people, firms, projects, and cases. Example: Bowles Rice appears on both the Ridgeline side (Speaker Hanshaw, William Lorensen) and the Monarch predecessor side (Peter Markham for a Fidelis affiliate). Click any link to see its source. | The watchdog view: who shows up where. |
| 8 | **County sheets (print-ready)** | Pick a county and get a one-page printable sheet: projects, standing meetings with times and addresses, upcoming hearings, how to comment, and QR codes back to case files. | A field tool for town halls and commission meetings. |
| 9 | **Receipts mode** | A global toggle that expands every claim to show its source and verification status inline. Links to the verification log. | Trust as a visible product feature. |

---

## Information architecture
Single static site, hash routes (no build step, any static host):

```
/                    Front page: countdown masthead, headline numbers, latest ticker, map teaser
#/map                Full map + time scrubber + layers (projects, power, transmission, hearings, counties)
#/project/:id        Case file (13 of them)
#/calendar           Agenda / month / standing meetings (exists; restyle)
#/docket             Stage board (courts, PSC, DEP, legislature)
#/people             Connections web + directory
#/county/:name       County sheet (printable)
#/hubs               The other AI story: research, education, startups (current hub content, demoted)
#/receipts           Verification log, rendered
```

**Data:** move inline arrays into `/data/*.json` (`projects`, `events`, `standing`, `docket`, `people`, `edges`, `hubs`). Every record carries `project`, `county`, `sources[]`, and `verify` fields so any view can cross-link. The existing Python generators keep producing the receipts Markdown.

---

## Visual system

**Palette: "ink & signal."** Darker and warmer than today's navy glow.

| Token | Value | Use |
|---|---|---|
| `--ink` | `#0B0D10` | Background (near-black, not navy) |
| `--paper` | `#EDE8DC` | Primary text (warm off-white) |
| `--cyan` | `#00D4FF` | Brand, links (kept from current site) |
| `--signal` | `#FFB020` | Deadlines, ⚠ Verify, countdowns |
| `--alarm` | `#FF5C5C` | Violations, protests, under construction |
| `--gas` | `#FF8A3D` | Gas generation |
| `--grid` | `#5AA9FF` | Grid-connected and transmission |
| `--legal` | `#C084FC` | Courts and contested items |

**Light "newsprint" theme** (`#F3EFE6` paper, `#111` ink) for county sheets and print, and as an optional toggle.

**Type:** keep the brand trio. **Instrument Serif** for headlines (editorial voice), **JetBrains Mono** for data, stamps, and telemetry, **DM Sans** for body.

**Texture:** the topo contour lines stay as a faint watermark (brand continuity), plus halftone and paper grain only in print mode.

**Motion:** one big moment, the scrubber autoplay. Everything else is restrained. Respect `prefers-reduced-motion`.

---

## Phasing
| Phase | Scope | Size |
|---|---|---|
| **1. Foundation** | Data split to JSON, hash router, new front page with countdown masthead, case files, palette and type refresh | Largest UX gain |
| **2. Place × time** | Time-scrubber map, layers, county boundaries, county sheets with print CSS | Signature moment |
| **3. Watchdog views** | Docket stage board, connections web (D3), scale-unit interstitials, receipts mode | Depth |
| **4. Reach** | RSS/JSON feed of new events, subscribable `.ics` URL, per-project OG share images (extend `generate_og.py`) | Distribution |

## Decisions for you
1. **Default theme:** dark "ink & signal" (recommended) or light "newsprint"? Either way, the other is available as a toggle.
2. **Map engine:** keep the custom-drawn canvas map and add county boundaries (recommended, distinctive), or switch to a real basemap (MapLibre plus free vector tiles) with roads and terrain?
3. **Innovation hubs:** demote to a "The other AI story" page (recommended), or retire them?
4. **Single file vs. data files:** split data into `/data/*.json` (recommended for maintainability), or stay one file?
5. **Connections web:** go as far as mapping lawyers and firms across projects? It's all sourced, but it is the most pointed feature on the site.

---

## Concept board: what each frame shows
Open `design/concept-board.html` in a browser (it is self-contained apart from Google Fonts). Static screenshots are in `design/screens/`.

| Frame | Screen | What to look at |
|---|---|---|
| 00 | Cover | Name of the direction and the seven principles |
| 01 | Front page, desktop | Ticker, masthead, five countdown chips (1 / 7 / 20 / 28 / 123 days from Nov 3), headline numbers, map with layer pills and the time scrubber |
| 01b | Front page, phone | Sideways countdown chips, "This week near you" for one remembered county, bottom tab bar |
| 02 | Case file: Monarch | Folder tabs, a dated timeline ending in a "NEXT" item, 864 engine dots plus 12 diesel generators, projected emissions bars, Take part box, redaction block for the HB 4983 confidential petition, receipts list |
| 03 | Docket stage board | 12 matters in five columns from "Not yet filed" to "Decided / closed", each with a case number and a rubber stamp; unconfirmed dates wear ⚠ Verify |
| 04 | Connections web | Bowles Rice in focus: Hanshaw and William Lorensen on the Ridgeline side, Peter Markham on the Monarch-predecessor side, each line labeled and sourced in the side panel |
| 05 | County sheet: Mason | Newsprint theme at letter size: both projects, the commission's meeting time and address, what to watch for, the two laws, and a QR placeholder |
| 06 | Style tile + decisions | Palette, type, stamps, chips, redaction bar, and the five decisions below |

## Receipts: how the board was made
1. **Data:** every number and date on the board was copied from the site's verified data (`index.html` PROJECTS, docket cards, and `research/calendar_data.py`), the dossier (`research/2026-11-wv-ai-watch-dossier.md`), and the verification log. Nothing new was researched for the board.
2. **Spot checks while building:** the "2,000+ signatures" figure is from the MARL section of the PSC docket record (dossier §4b), so the board says "against the MARL line." The Peter Markham connection was re-read in the saved Gazette-Mail permits article: he wrote to the DEP for MGS CNP 1 LLC, a Fidelis New Energy affiliate. The HB 2014 signing day is not in our sources, so the scrubber starts at "2025" with no day.
3. **Things removed for honesty:** a "4.3 GW combined" Mason County figure was cut because it added Monarch's on-site generation to Tamarack's grid draw, which are different measures. An "Updated 6:00 a.m." timestamp was cut because it was invented. "The one law firm on two projects" became "a law firm that turns up on two projects", since we did not check every firm.
4. **Map:** the West Virginia outline and project positions come from the same coordinates the live site uses, projected to SVG.
5. **Rendering:** Playwright (headless Chromium) captured each frame. The run reported no console errors and confirmed all three brand fonts loaded.

## Soft and hard blocks
**Hard blocks (need you, or something outside this repo):**
- **The five decisions above.** Phase 1 can't start until at least decisions 1, 3, and 4 are made.
- **QR codes** on county sheets need a decision on the final URL scheme (`#/county/mason` vs a real path). The board shows a placeholder pattern, not a working code.
- **The PSC website blocks automated access** from this environment, so docket stages stay hand-maintained from your PSC email digests unless the site can be reached another way.

**Soft blocks (assumptions you can overrule):**
- The countdown chips assume the calendar data stays current. A stale date becomes a wrong countdown, so each chip needs an owner and a "last checked" date.
- County lines for the map would come from public Census TIGER boundaries (not yet pulled).
- The connections web is hand-placed for 17 nodes. A full version with all 52 people needs a force layout (D3) and a review rule: no line without a source.
- "This week near you" stores one county in the browser only. No accounts, no tracking.
- Status labels (Under construction, Contested, and so on) are an editorial classification, as the dossier already says.

