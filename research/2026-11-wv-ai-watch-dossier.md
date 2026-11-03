# WV AI Watch: Project Dossier (Deep-Dive, Nov 3, 2026)

> Working Markdown draft. The site's new **Project Watch**, **Docket**, **Calendar**, and **Who's Who** sections are built from this file. Every claim links to its source. Where sources disagree, both figures are shown and flagged **⚠ conflict**.

---

## 0. Method, receipts, and disclosures

**How this was built**
1. Started from aggregator trackers (nearbydatacenters.org, Country Roads News archive, Ban the Bots, Compute Atlas, cleanview) to get a candidate list of projects.
2. Verified each project against primary or first-line reporting: WV Gazette-Mail (Mike Tony), West Virginia Watch, WV Public Broadcasting (Chris Schulz, Curtis Tate), WV MetroNews (Brad McElhinny), Herald-Dispatch, WSAZ/WOWK/WCHS/WDTV/WTOV, Observer (Jefferson Co.), Dominion Post, Country Roads News (Dan Parks), NPR, TechCrunch.
3. Pulled regulatory hooks: PSC case numbers, DEP permit numbers, court case names, bill numbers.
4. Pulled calendar items (hearings, protests, town halls, open houses) and flagged those that are past vs. upcoming relative to **Nov 3, 2026 (Election Day)**.

**Hard blocks (could not do)**
- Could not query the PSC e-filing system, DEP permit database, or court dockets directly. Docket statuses come from reporting and public notices, not the dockets themselves.
- Several pages returned 403/404/503 (West Virginia Watch on two stories, NPR on Oct 31). Their facts come from search summaries and syndicated copies only.
- Election results for Nov 3, 2026 were not available at time of writing.

**Soft blocks / assumptions**
- Map coordinates are **approximate** (town-level or road-level), not parcel boundaries. Transmission corridors are **illustrative**: Valley Link has no approved route, and MARL is drawn county-to-county.
- "Status" categories (Under Construction / Certified / Permitted-Contested / Proposed / Rumored) are my editorial classification of the reporting.
- Trackers disagree on megawatts for several projects. The site shows ranges where that happens.

**Disclosure.** This research and build was done with Claude, an AI model made by Anthropic. Anthropic is reported as the anchor customer at Nscale's Monarch Compute Campus (Mason County). That project is covered here with the same sourcing standard as every other entry, including violations and opposition.

---

## 1. Statewide framework

| Item | What it does | Status | Source |
|---|---|---|---|
| **HB 2014** (2025), "Power Generation and Consumption Act" | Creates High Impact Data Center (≥90 MW) certification and Certified Microgrid Districts (up to 2,250 acres). Preempts county/municipal zoning and ordinances for certified projects. Sends 30% of property-tax revenue to the host county. | Signed by Gov. Patrick Morrisey Apr 30, 2025. Effective Jul 2025. | [WV Legislature](https://bills.wvlegislature.gov/bill/history/2025/rs/HB2014), [WVCBP](https://wvpolicy.org/five-ways-hb-2014-harms-communities-local-governments-and-schools/) |
| **HB 4983** (2026) | Approves Commerce rule 145 CSR 20. Certification petitions kept confidential. | Passed House 78-16. Final House approval Mar 13, 2026. Signed Apr 2026. | [Gazette-Mail](https://www.wvgazettemail.com/news/legislative_session/wv-house-passes-data-center-enticement-bill-that-would-keep-project-details-hidden/article_d93196ac-1291-4a25-8f34-629ca46f2604.html), [nearbydatacenters](https://nearbydatacenters.org/wv/) |
| **Bills that died in 2026** | HB 5620 and SB 658 (restore local control), HB 5590 (water-use notice), HB 4013 (Mountaineer Flexible Tax Credit), others. | Died | [Mountain State Spotlight](https://mountainstatespotlight.org/2026/02/25/lawmakers-block-data-center-bills/) |
| **Responsible Data Center Development Plan** | 7 principles over 20 years. Run by the Commerce Dept.'s Data Economy Office (Director **Chris Morris**). Promises a Data Center Advisory Council (academia, local gov't, conservation, industry, utilities) to recommend setbacks, noise, and security standards. | Policy only, not law. Unveiled Aug 11, 2026. No public council roster found. | [Plan PDF](https://westvirginia.gov/wp-content/uploads/2026/08/Data-Center-Principles-August-2026-FINAL-8-26.pdf), [WDTV](https://www.wdtv.com/2026/08/11/west-virginia-unveils-20-year-responsible-data-center-development-plan/), [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/the-same-story-morrisey-data-center-plan-doubles-down-on-industry-regulation-gaps/article_e22e72d4-4aa9-4696-8396-51e98d4f3e08.html) |
| **AG declines Berkeley Co. opinion** | Berkeley County sent a 10-page request (Sep 18) about how HB 2014 preemption affects its stormwater MS4 duties and PSDs. AG **J.B. McCuskey** declined on Oct 9 because of pending litigation. | Oct 9, 2026 | [MetroNews](https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/) |

**Certified High Impact Data Centers (as of Nov 3, 2026):** Penzance Bedington (Berkeley), Google (Putnam), Nscale Monarch (Mason), and Starwood Project Tamarack (Mason). The first two were certified by June 2026 ([WCHS](https://wchstv.com/news/local/two-wv-data-centers-approved-but-neither-plans-microgrids-under-hb-2014)). Monarch and Tamarack were announced Sep 3, 2026 at the WV Chamber summit at The Greenbrier ([Herald-Dispatch](https://www.herald-dispatch.com/business/morrisey-hails-state-certifications-for-two-mason-county-data-center-projects/article_924875e0-77b4-45ab-9115-2ff4b193a6ae.html)).

---

## 2. Projects

### 2.1 Monarch Compute Campus · Mason County (near Point Pleasant) · UNDER CONSTRUCTION
- **Developer:** Nscale (UK). It acquired American Intelligence & Power Corp. (AIPCorp, a Fidelis New Energy / 8090 Industries affiliate) in March 2026. The project entity is Monarch Cloud Campus LLC (Houston).
- **People:** Daniel Shapiro (Nscale Chief Power Officer), William Calhoun (Monarch Cloud Campus executive), Jason Bechtle (site manager).
- **Scale:** Up to 2,250 acres off Ohio River Road (WV-62). Phase 1 is a 1.35 GW data center plus a 2.16 GW off-grid gas microgrid with **864 reciprocating engines**, 12 diesel generators, 6 diesel fire pumps, and 6 gas heaters. Nscale cites a $69.2B investment, 4,375 construction jobs, and 645 permanent jobs, with an expansion path to 8+ GW.
- **Customers:** **Anthropic** signed a $44.6B contract for the first 460 MW building (per Nscale's Sep 18, 2026 IPO filing), and a second ~$45B building is under discussion. **Microsoft** had a 1.35 GW letter of interest that was never produced to reporters. Bloomberg reported Microsoft walked away. ⚠ conflict.
- **Financing:** **Nvidia** is in talks to guarantee billions in construction debt through a "residual value guarantee" (The Information / Bloomberg, Oct 30, 2026). Nvidia committed $1B in convertible financing to Nscale in September.
- **State money:** The WV EDA approved a forgivable $62.5M loan in 2023 to Fidelis subsidiary Mountaineer GigaSystem LLC for an earlier hydrogen plan. $25M was disbursed, and the $37.5M second tranche was waived.
- **Permits:** Air permit **R14-0042** (applied Apr 20, 2026). DEP's preliminary finding is that it meets requirements. The Oct 20 workshop was at Point Pleasant High School, the virtual hearing was Oct 29, and **comments closed Oct 30, 2026**. DEP engineers: Joe Kessler (NSR permitting manager) and Edward Andrews (NSR engineer). Projected annual emissions: 1,043 t CO, 900 t VOC, 506 t NOx, and 38 t PM2.5. It is a "major stationary source." Stormwater permit WVR312628 covers a 556.5-acre pipeline disturbance in Putnam/Mason (hearing was June 15). The Environmental Integrity Project ranks it #2 nationally among planned data-center gas plants for GHG emissions.
- **Violations:** DEP dust warning (May 5). Silt-fence failure flooded about 6 homes (May 23–24, Meadowlands Estates / University Lane). DEP notices on May 28, Jun 4, and Jun 10, an early-July enforcement order, and a particulate violation letter on Aug 11 from DAQ Director Laura Crowder.
- **Community:** Voluntary home-buyout program (24 closed and 14 under contract as of Aug 14, with offers open to Jun 30, 2028). Donations: $250K to the Sheriff, $150K to ambulance, $50K to the Development Authority. Residents quoted: Kimberly Mattox, Stephanie Butcher, Carl Matheny, Joshua Jeffers, and Jeanette DiDomenico. Group: **Mason WV United** (Elaine Matheny).
- Sources: [Gazette-Mail (permits)](https://www.wvgazettemail.com/news/energy_and_environment/new-permits-eyed-for-mason-co-data-center-tied-project-after-eight-figure-wv-support/article_6a2e5e86-a19e-442d-831c-24f1760bbf80.html), [Gazette-Mail (Oct 20 meeting)](https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html), [Gazette-Mail (opposition)](https://www.wvgazettemail.com/news/energy_and_environment/monarch-google-data-center-project-environmental-dangers-driving-resident-opposition/article_b35e6ed1-15af-4975-9772-54b89bb5a013.html), [TechCrunch](https://techcrunch.com/2026/10/30/nvidia-weighs-playing-the-cosigner-for-nscales-ai-data-center-in-west-virginia/), [Herald-Dispatch](https://www.herald-dispatch.com/business/morrisey-hails-state-certifications-for-two-mason-county-data-center-projects/article_924875e0-77b4-45ab-9115-2ff4b193a6ae.html), [Ban the Bots tracker](https://www.banthebots.org/explainers/ai-data-centers-in-west-virginia)

### 2.2 Project Tamarack · Mason County (West Columbia) · CERTIFIED
- **Developer:** Starwood Digital Ventures (data-center arm of Starwood Capital Group, Miami Beach). CEO **Anthony Balestrieri**.
- **Scale:** $12B, ~2.16 GW drawn from the grid through existing Appalachian Power infrastructure, with no on-site plant. 1,000+ construction jobs and 300+ permanent. Closed-loop cooling. Promises a Mason County Community Advisory Group.
- **Context:** Starwood's 1.2 GW "Project Washington" in Delaware was denied, and a Delaware board upheld the denial in March 2026.
- **Status:** Certified Sep 3, 2026. No timeline released. Resident Kimberly Mattox lives a quarter mile away.
- Sources: [WOWK](https://www.wowktv.com/news/west-virginia/mason-county-wv/second-mason-co-data-center-will-land-in-west-columbia/), [WSAZ "Total shocker"](https://www.wsaz.com/2026/09/04/total-shocker-residents-react-second-data-center-coming-mason-county/), [WV Watch](https://westvirginiawatch.com/2026/09/08/new-data-center-project-coming-to-mason-county-wv-spearheaded-by-florida-based-real-estate-group/)

### 2.3 Google Buffalo Campus · Putnam County · CERTIFIED
- **Developer:** Google, via affiliate **Cumulus Group LLC**.
- **Scale:** 1,699–1,700 acres along Charleston Rd / WV-62, east of the Kanawha River, near the 765 kV ApCo line. Eight data-center buildings per the Army Corps application (⚠ conflict: one tracker says three buildings of ~300K sq ft). Google says it pays for power and for water/sewer upgrades.
- **Permits:** DEP air permit application filed Jul 22, 2026: 288 diesel emergency generators (2,750 kW each), 128 cooling towers, and 294 belly tanks. Projected 249 t/yr NOx. The Army Corps application shows 34+ acres of wetlands (17) and 45,000+ ft of streams (34) affected.
- **Process:** Certified in March 2026 after six-plus months of closed-door meetings (revealed by a Gazette-Mail FOIA). Announced Mar 27, 2026.
- **People:** County Commission President **Andy Skidmore** said the county was weighing an HB 2014 lawsuit with Monongalia County. Residents include Melanie and Tim Lacy, Barbie Fronk, Ashley Armstrong, and Dr. Kyle McCausland. Group: **Putnam United** (Heather Ransom, Jessica Lacy, Joseph DeGroff).
- Sources: [MetroNews](https://wvmetronews.com/2026/04/14/putnam-county-residents-speak-out-about-proposed-google-data-center-near-buffalo/), [Governor](https://governor.wv.gov/article/governor-morrisey-announces-google-data-center-project-putnam-county), [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/monarch-google-data-center-project-environmental-dangers-driving-resident-opposition/article_b35e6ed1-15af-4975-9772-54b89bb5a013.html)

### 2.4 Ridgeline · Tucker (and Grant) County, near Davis & Thomas · AIR-PERMITTED, CONTESTED
- **Developer:** Fundamental Data LLC (Purcellville, VA). "Responsible individual": **Casey Chapman**.
- **Scale:** Phase 1 is a ~785 MW gas plant with diesel backup (~30M gal diesel storage in three 10M-gal tanks). The company has floated ~1.3 GW of solar. The site starts at 291 acres and could reach 10,000 acres. Reporting has described the full complex at up to 5.2 GW. Target: 2028.
- **Legal and regulatory timeline:**
  - 2025: DEP air permit issued as a *minor* source.
  - Feb 5, 2026: Air Quality Board upholds it.
  - Mar 12: Tucker United, WV Highlands Conservancy, and Sierra Club appeal to the Intermediate Court of Appeals (ICA), represented by Appalachian Mountain Advocates.
  - Mar 16: House Speaker **Roger Hanshaw** (R-Clay, Bowles Rice) becomes Fundamental Data's counsel.
  - Apr 20: ICA Chief Judge Daniel Greear seeks recusal. Judge Charles Lorensen also recuses (his son William Lorensen is a Bowles Rice attorney on the case). Chief Justice C. Haley Bunn appoints Judges Shawn Nines, Gregory Howard, and S. Ryan White.
  - Jun 3: SCAWV denies Fundamental Data's motion to bypass the ICA.
  - Jun 18: Commerce Deputy Secretary **Nick Preservati** issues a notice that the company missed the certification deadline. It was rescinded Jul 1–2.
  - Jul 21: A company engineer/consultant says "we were the guys that basically wrote the bill." Jul 23: Morrisey says "Shame on them."
  - Aug 17: DEP accepts a redacted purchase agreement as proof of site control.
  - **Aug 26: ICA dismisses both appeals on jurisdiction** (they belong in circuit court or SCAWV), not on the merits. The groups say they will refile and seek a hearing (Aug 28–31).
  - Sep 2: A geologists' study cites abandoned-mine subsidence and methane risks.
  - Oct 31: NPR national story on dark skies and ski areas.
- **Local government:** Davis Town Council voted 5-0 to oppose (May 2025). The Tucker County Commission takes no position. State Sen. Randy Smith dismissed opponents as "vacation homeowners."
- **Health study:** A Harvard T.H. Chan (Dominici Lab) study projects $19–35M in health damages.
- **Opposition:** **Tucker United** (Director **Amy Margolies**), WV Highlands Conservancy (Interim ED **Olivia Miller**, Luanne McGovern), and Sierra Club WV.
- Sources: [Gazette-Mail (legal obstacles)](https://www.wvgazettemail.com/news/energy_and_environment/wv-data-center-project-pushback-from-state-and-citizens-runs-into-legal-obstacles/article_b7a4f8f7-4fae-4dab-b808-cb8d0b0c1c94.html), [WTAP (ICA dismissal)](https://www.wtap.com/2026/08/26/state-appeals-court-dismisses-environmental-groups-lawsuits-over-tucker-county-data-center-plant/), [WV Watch (site control)](https://westvirginiawatch.com/2026/08/17/wv-dep-says-fundamental-data-controls-site-of-proposed-tucker-county-data-center-power-plant/), [Country Roads News archive](https://countryroads.substack.com/p/data-center-story-archive), [WVHC update](https://www.wvhighlands.org/?p=15053), [WVHC refile](https://www.wvhighlands.org/?p=15160), [NPR](https://www.npr.org/2026/10/31/nx-s1-5992790/data-centers-west-virginia-skiing-dark-skies)

### 2.5 Adams Fork Energy Campuses · Mingo County (Wharncliffe/Twisted Gun + Holden/Harless) · AIR-PERMITTED
- **Developer:** TransGas Development Systems LLC (New York City). CEO **Adam Victor**. Representative Adam Victor Jr.
- **Scale:** Two gas plants, 117 engines each, ~2,457 MW aggregate per site (⚠ conflict: trackers list 1,200–2,850 MW). Data centers at the Twisted Gun Golf Course (Wharncliffe) and Harless Industrial Park (Holden). A legacy ammonia-plant permit status is unclear. Cooling would use mine-pool water.
- **Permits:** DEP air permits **R13-3714 / R13-3715** were issued in October 2025.
- **Lawsuit:** Ten residents filed in U.S. District Court (S.D. W.Va.) on Dec 3, 2025 against TransGas, the Army Corps, Fish & Wildlife, and FERC. Judge **Robert Chambers** dismissed the TransGas claims in March 2026 and the agency claims on **Jun 22, 2026, without prejudice**. Attorney **Stephen New** (Beckley) plans new EPCRA suits and has said he will also target Penzance and QTS.
- Sources: [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/wv-data-center-project-pushback-from-state-and-citizens-runs-into-legal-obstacles/article_b7a4f8f7-4fae-4dab-b808-cb8d0b0c1c94.html), [WV Watch (lawsuit)](https://westvirginiawatch.com/2025/12/05/mingo-county-residents-file-federal-lawsuit-against-company-building-power-plants-data-center-in-wv/), [GEM wiki](https://www.gem.wiki/Adams_Fork_Data_Center_Energy_Campus)

### 2.6 Penzance Bedington Campus · Berkeley County (Falling Waters / Bedington) · CERTIFIED (first under HB 2014)
- **Developer:** Penzance (Washington, D.C.). Entity: Bedington Owner LLC.
- **Scale:** $4B, 548 acres, 1.9M sq ft, 600 MW IT, grid-connected, no microgrid. ~1,000 construction jobs and 125 full-time.
- **Status:** Announced Feb 2026 by Gov. Morrisey as WV's first "High Impact Intelligence Center." The DEP stormwater construction permit application was accepted as complete (Jul 29–30, 2026). Berkeley Commission President **Eddie Gochenour** supports it. The county says it has "no oversight." The County's AG opinion request was declined Oct 9.
- **Opposition:** **No Data Centers in the Eastern Panhandle** (Rupok Bhuiyan) and a resident petition.
- Sources: [Governor](https://governor.wv.gov/news/press-releases/2026/pages/gov-morrisey-announces-states-first-high-impact-intelligence-center.aspx), [WV Watch](https://westvirginiawatch.com/2026/02/26/d-c-based-real-estate-firm-investing-4b-for-new-data-center-development-in-berkeley-county-wv/), [Observer](https://observerwv.com/bedington-data-center-project-seeks-construction-permit/), [MetroNews](https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/)

### 2.7 QTS Kearneysville · Berkeley/Jefferson line · CONCEPT APPROVED (Berkeley parcels)
- **Developer:** QTS Data Centers (a Blackstone portfolio company).
- **Scale:** ~300 acres split across Berkeley and Jefferson. Two buildings, a switching station, and a water tank. The Berkeley Planning Commission approved the concept plan in March 2025. Jefferson County has received no plans.
- Sources: [Observer](https://observerwv.com/plan-for-data-center-complex-near-kearneysville-approved), [Baxtel](https://baxtel.com/campus/qts-kearneysville-campus)

### 2.8 Summit Point site · Jefferson County · PROPOSED (thinly sourced)
- **Developer:** Ryan Stuart Development, 235 acres. A presentation to the Charles Town Utility Board was reported Apr 29, 2026. No filings found. Jefferson County Commissioner **Cara Keys** has criticized HB 2014's lack of setbacks and groundwater protections.
- Sources: [nearbydatacenters](https://nearbydatacenters.org/wv/), [Observer tag](https://observerwv.com/tag/summit-point-utility-project/)

### 2.9 Hog Lick Aggregates · Marion County (White Hall) · FEASIBILITY STUDY
- **Developer:** Hog Lick Aggregates (quarry). President **Brian Redmond**.
- **Scale:** 277–300 acres, with 1,500 more available. Phased up to 1 GW on gas and/or grid. Proposes geothermal cooling in the flooded "Krissy Mine." Previously involved in the ARCH2 hydrogen hub. Redmond: "too early for anyone to light their hair on fire."
- Sources: [WDTV](https://www.wdtv.com/2026/05/05/local-company-proposes-data-center-marion-county/), [Register-Herald](https://www.register-herald.com/west_virginia/news/fairmont-company-president-defends-data-center-says-too-early-to-protest-his-plan/article_de4430dd-e3f5-5176-9c2a-b45a862f9a88.html)

### 2.10 Centre Foundry / Warwood · Wheeling (Ohio County) · CONTESTED IN COURT
- **Developer:** Silicon Foundation Energy, partnered with Stokes Inc. (SC). The 15-acre former Centre Foundry at 74 Warwood Ave was bought for $1.5M.
- **Scale:** Phase 1 is 10 MW on the grid, then 20–30 MW, with a stated end-state of a 100 MW regional hub. Later described as 50 MW and under the 90 MW HB 2014 threshold, which means City of Wheeling oversight. Gas backup and closed-loop river-water cooling.
- **Lawsuit:** **Barks v. Silicon Foundation** (Ohio County Circuit Court). Twelve residents argue HB 2014 unconstitutionally strips local land-use control. The AG's office intervened to defend the statute.
- **People:** Del. **Shawn Fluharty** (D-Ohio) held town halls at the Warwood Veterans Association (June 2026) and attended a Waterfront Hall meeting. Ohio County resident **Amanda McWhorter** (WVDCAP).
- Sources: [WVPB](https://wvpublic.org/story/energy-environment/states-sixth-data-center-announced-near-wheeling/), [WTOV (town hall)](https://wtov9.com/news/local/warwood-residents-state-delegate-raise-concerns-over-proposed-data-center-at-town-hall-warwood-data-center-local-control-house-bill-2014-shawn-fluharty-health-concerns-environmental-impact-wheeling), [WTOV (50 MW)](https://wtov9.com/news/local/officials-say-revised-warwood-data-center-would-draw-river-water-no-discharge-or-rate-hikes-warwood-data-center-silicon-foundation-closed-loop-river-water-no-discharge-utility-rates-shawn-fluharty), [MetroNews](https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/)

### 2.11 Monroe County (near Ballard) · RUMORED
- The Commission's Feb 2026 statement said authority now sits with the state. Protest held Oct 2026 in Giles County, VA outside the law office of landowner Jason Buckland, per WVTF. There is also a "Monroe County Bill of Rights" petition.
- Sources: [WVTF/Radio IQ](https://www.wvtf.org/news/2026-10-26/residents-gather-in-giles-to-protest-potential-monroe-county-data-center), [Mountain Messenger](https://mountainmessenger.com/?p=100074)

### 2.12 Power and grid projects driven by data-center load
- **Fort Martin gas addition (Monongalia Co.):** Mon Power / Potomac Edison (FirstEnergy). 1,200 MW gas plus 70 MW solar, $2.48B. Filed Feb 2026. Public comment hearing Jul 15 and evidentiary hearing Jul 16. **No PSC decision yet**, with a statutory deadline of Feb 2027. Sierra Club WV contests "abandonment" cost recovery and notes no signed data-center contract. [WVPB](https://wvpublic.org/story/energy-environment/application-to-convert-coal-fired-fort-martin-to-gas-submitted-to-psc/), [Sierra Club](https://www.sierraclub.org/press-releases/2026/06/sierra-club-west-virginia-files-testimony-mon-power-s-248-billion-gas-plant)
- **MARL – Mid-Atlantic Resiliency Link (PSC Case 26-0075-E-CN):** NextEra Energy Transmission MidAtlantic. 500 kV, ~58.9 WV miles across Monongalia, Preston, Mineral, and Hampshire. 190+ landowner intervenors. PSC staff analyst Daniel Egnatoff recommended denial. Evidentiary hearings ended Oct 30 (one listing shows Nov 2). **Initial briefs due Nov 23, replies Dec 4, decision expected ~Mar 6, 2027.** [Valley North Record](https://valleynorthrecord.substack.com/p/regional-osint-db7), [WV Legals notice](https://wvlegals.com/?p=201001)
- **Valley Link / "Valley North" 765 kV:** A Dominion, FirstEnergy Transmission, and Transource (AEP/Evergy) joint venture. Runs from the John Amos plant (Putnam) east toward Frederick Co., MD, with a Hardy Co. substation. Preliminary corridors through 14–20 WV counties. No PSC application yet, and a preferred route is expected early 2027. County commissions opposed: Barbour, Upshur, Lewis, Preston. State Sen. **Robbie Morris** opposes it. Ag Commissioner **Kent Leonhardt** has raised concerns. Ken Burns has publicly opposed it. [WDTV](https://www.wdtv.com/2026/07/17/upshur-county-commission-opposes-valley-north-transmission-project/), [WMRA](https://www.wmra.org/2026-08-25/the-growing-county-government-opposition-to-valley-link), [Cardinal News](https://cardinalnews.org/2026/06/02/valley-link-says-its-new-transmission-line-plan-would-impact-fewer-people-opponents-vow-to-continue-fighting-it/)
- **ApCo/Wheeling Power large-load tariff (PSC Case 24-0611-E-T-PW):** ≥100 MW customers get 12-year contracts with an 80% minimum demand charge. ApCo says it has contracted "more than double" its 540 MW Virginia data-center load in WV. [WVPB](https://wvpublic.org/story/energy-environment/compromise-proposed-in-psc-case-involving-data-centers/), [Cardinal News](https://cardinalnews.org/2026/07/31/appalachian-power-anticipates-explosive-growth-in-large-customers-primarily-data-centers/)
- **PSC HB 2014 coal-capacity rule:** The 69% capacity-factor target was softened to a "goal, not a mandate" (Oct 2026), based partly on joint ApCo / Mon Power amendments. [WV Watch](https://westvirginiawatch.com/2026/10/20/west-virginia-public-service-commission-makes-power-rule-a-goal-not-a-mandate/), [News and Sentinel](https://www.newsandsentinel.com/news/business/2026/10/w-va-public-service-commission-releases-proposed-rules-for-power-plant-capacity/)

---

## 3. Calendar (relative to Nov 3, 2026)

### Upcoming
| Date | Event | Where | Who | Source |
|---|---|---|---|---|
| **Nov 3, 2026** | General Election. HB 2014 and transmission lines are a top issue. Polls 6:30a–7:30p. | Statewide | · | [MetroNews](https://wvmetronews.com/2026/10/30/data-centers-transmission-lines-highlight-issues-driving-voter-turnout-in-west-virginia/) |
| **Nov 4–19, 2026** | Valley Link developer open houses (12 sessions in WV/VA/MD). The first are Nov 4 in Fisher and Hambleton, WV. | Fisher (Hardy), Hambleton (Tucker), others | Valley Link | [Valley North Record](https://valleynorthrecord.substack.com/p/regional-osint-db7) |
| **Nov 23, 2026** | MARL initial briefs / proposed orders due | PSC, Case 26-0075-E-CN | NextEra, intervenors | same |
| **Dec 4, 2026** | MARL reply briefs due | PSC | · | same |
| **Jan 2027** | 2027 Regular Session. Democrats and WVDCAP push HB 2014 reform and local control. | Capitol | · | [WVHC](https://www.wvhighlands.org/?p=15053) |
| **Jan 26, 2027** | WV Rally for Affordable Energy, 10a–12p | State Capitol, South Steps | WV Utility Impact Project, Valley North Opposition Alliance | [Valley North Record](https://valleynorthrecord.substack.com/p/regional-osint-db7) |
| **By Feb 2027** | PSC statutory deadline on Fort Martin gas plant | PSC | Mon Power / Potomac Edison | [Dominion Post](https://www.dominionpost.com/?p=566179) |
| **~Mar 6, 2027** | Anticipated PSC decision on MARL | PSC | · | [Valley North Record](https://valleynorthrecord.substack.com/p/regional-osint-db7) |
| **Pending** | DEP final decision on Monarch air permit R14-0042 | DEP DAQ | Nscale / Monarch Cloud Campus | [WSAZ](https://www.wsaz.com/2026/10/21/data-center-air-pollution-permit-under-public-review/) |
| **Pending** | Tucker United et al. refile of Ridgeline permit appeal (circuit court or SCAWV) | · | Appalachian Mountain Advocates | [WVHC](https://www.wvhighlands.org/?p=15160) |
| **Pending** | Barks v. Silicon Foundation (HB 2014 constitutionality) | Ohio Co. Circuit Court | 12 residents vs. Silicon Foundation; AG intervening | [MetroNews](https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/) |

### Recent (past 90 days)
| Date | Event | Source |
|---|---|---|
| Nov 2 | Stop Valley Link peaceful protest, 2–6p, Barbour County Courthouse, Philippi | [Valley North Record](https://valleynorthrecord.substack.com/p/regional-osint-db7) |
| Oct 31 | NPR national feature on Ridgeline / dark skies | [NPR](https://www.npr.org/2026/10/31/nx-s1-5992790/data-centers-west-virginia-skiing-dark-skies) |
| Oct 30 | Monarch air permit comment deadline. MARL hearings conclude. Nvidia financing report. | [WSAZ](https://www.wsaz.com/2026/10/21/data-center-air-pollution-permit-under-public-review/), [TechCrunch](https://techcrunch.com/2026/10/30/nvidia-weighs-playing-the-cosigner-for-nscales-ai-data-center-in-west-virginia/) |
| Oct 29 | DEP virtual public hearing, Monarch air permit | [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html) |
| Oct 26 | DEP water-permit workshop and hearing, Point Pleasant HS (Monarch). Monroe Co. protest reported (Giles Co., VA). | [WCHS](https://wchstv.com/news/local/public-hearing-input-used-in-massive-data-center-state-waters-application-decision), [WVTF](https://www.wvtf.org/news/2026-10-26/residents-gather-in-giles-to-protest-potential-monroe-county-data-center) |
| Oct 20 | DEP air-permit workshop, Point Pleasant HS (7 speakers) | [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html) |
| Oct 9 | AG McCuskey declines Berkeley County opinion | [MetroNews](https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/) |
| Sep 8 | WV Data Center Accountability Project (WVDCAP) launches, Charleston | [WV CAG](https://wvcag.org/?p=16377) |
| Sep 3 | Monarch and Tamarack certified, Greenbrier Chamber summit | [Herald-Dispatch](https://www.herald-dispatch.com/business/morrisey-hails-state-certifications-for-two-mason-county-data-center-projects/article_924875e0-77b4-45ab-9115-2ff4b193a6ae.html) |
| Aug 26 | ICA dismisses Ridgeline appeals on jurisdiction | [WTAP](https://www.wtap.com/2026/08/26/state-appeals-court-dismisses-environmental-groups-lawsuits-over-tucker-county-data-center-plant/) |
| Aug 25 | Putnam United resolution at County Commission meeting | [Gazette-Mail](https://www.wvgazettemail.com/news/energy_and_environment/monarch-google-data-center-project-environmental-dangers-driving-resident-opposition/article_b35e6ed1-15af-4975-9772-54b89bb5a013.html) |
| Aug 14–15 | WV NAACP convention (Huntington) unanimously demands a ≥2-year moratorium. Signed by President Loretta Young. | [The Fulcrum](https://thefulcrum.us/community/west-virginia-naacp-data-center-moratorium-call) |
| Aug 11 | Governor's Responsible Data Center Development Plan | [WDTV](https://www.wdtv.com/2026/08/11/west-virginia-unveils-20-year-responsible-data-center-development-plan/) |
| Jun 14–16 | Legislative interims at Canaan Valley. Tucker United gathering. Democratic caucus presser at Davis Town Hall. Mountain State Spotlight panel at Davis Fire Hall. | [WVHC](https://www.wvhighlands.org/?p=15053) |
| Jun 2026 | Del. Fluharty town hall, Warwood Veterans Assn. | [WTOV](https://wtov9.com/news/local/warwood-residents-state-delegate-raise-concerns-over-proposed-data-center-at-town-hall-warwood-data-center-local-control-house-bill-2014-shawn-fluharty-health-concerns-environmental-impact-wheeling) |

---

## 4. Who's Who

**State government:** Gov. Patrick Morrisey · AG J.B. McCuskey · House Speaker Roger Hanshaw (R-Clay; Bowles Rice counsel to Fundamental Data) · Sen. Randy Smith (R-Tucker) · Sen. Robbie Morris (opposes Valley Link) · Ag Commissioner Kent Leonhardt · Commerce Deputy Sec. Nick Preservati · Data Economy Office Director Chris Morris · DEP DAQ Director Laura Crowder · DEP's Joe Kessler and Edward Andrews · PSC staff analyst Daniel Egnatoff · Chief Deputy SoS Donald Kersey III · Chief Justice C. Haley Bunn

**Legislators and candidates (critics):** Del. Shawn Fluharty (D-Ohio) · Dels. Evan Hansen, JB Akers, Sean Hornbuckle, Kayla Young, Mike Pushkin (also WV Democratic Party Chair), Anitra Hamilton · candidates Deborah Stiles (Tucker/Grant), Olivia Miller (Monongalia), Chris Claypole (Senate), Paige Reiring (HD-79, Mountain Party) · Congressional: Rep. Riley Moore and Ace Parsi (WV-2, competing federal data-center bills)

**County officials:** Andy Skidmore (Putnam Commission President) · Eddie Gochenour (Berkeley Commission President) · Cara Keys (Jefferson Commissioner) · Sean Sikora (Monongalia Commissioner) · Ben Salango (Kanawha Commission President)

**Courts:** U.S. District Judge Robert Chambers (S.D. W.Va.) · ICA Judges Daniel Greear and Charles Lorensen (recused) · Shawn Nines, Gregory Howard, S. Ryan White (appointed)

**Companies:** Nscale (Daniel Shapiro, William Calhoun, Jason Bechtle) · Anthropic · Microsoft · Nvidia · Fidelis New Energy / AIPCorp / 8090 Industries / Mountaineer GigaSystem · Starwood Digital Ventures (Anthony Balestrieri) · Google / Cumulus Group LLC · Penzance / Bedington Owner LLC · QTS · Ryan Stuart Development · Fundamental Data (Casey Chapman) · Bowles Rice (Roger Hanshaw, William Lorensen, Peter Markham) · TransGas Development Systems (Adam Victor, Adam Victor Jr.) · Hog Lick Aggregates (Brian Redmond) · Silicon Foundation Energy / Stokes Inc. · Appalachian Power / AEP · Mon Power / Potomac Edison / FirstEnergy · NextEra Energy Transmission MidAtlantic · Valley Link (Dominion / FirstEnergy / Transource) · ERM (consultant) · Ernst & Young (Nscale tax study)

**Community and advocacy:** WV Data Center Accountability Project (WVDCAP) · WV Citizen Action Group (Morgan King, Jillian Welsh) · Tucker United (Amy Margolies) · WV Highlands Conservancy (Olivia Miller, Luanne McGovern) · Sierra Club WV (Jim Kotcon) · Putnam United (Heather Ransom, Jessica Lacy, Joseph DeGroff) · Mason WV United (Elaine Matheny) · No Data Centers in the Eastern Panhandle (Rupok Bhuiyan) · WV NAACP (Loretta Young) · Energy Efficient WV (Emmett Pepper) · WV Center on Budget & Policy · Appalachian Mountain Advocates · Stephen P. New & Associates · Environmental Integrity Project · Stop Valley Link · Valley North Opposition Alliance · WV Utility Impact Project · Harvard T.H. Chan Dominici Lab

**Journalists to follow:** Mike Tony (Gazette-Mail) · Chris Schulz and Curtis Tate (WVPB) · Brad McElhinny (MetroNews) · Dan Parks (Country Roads News) · Steve Pearson (Observer)

---

## 5. Open questions / next research pass
- Monarch R14-0042 final determination date.
- Whether Tucker United has refiled, and in which court.
- Barks v. Silicon Foundation: judge, hearing dates.
- Fort Martin PSC case number and order.
- Valley Link's full WV open-house schedule.
- Google air permit public-comment window.
- Data Center Advisory Council roster.
- Nov 3 election outcomes for HB 2014 critics and supporters.
