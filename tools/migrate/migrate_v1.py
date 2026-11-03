"""One-time migration: old single-file site -> data/*.json for the Watch Desk revamp.

Ran once on Nov 3, 2026 against index.html at commit a3f9076. Kept for the
record (receipts), not for re-running: after this, data/*.json is the source
of truth and is edited directly (see docs/update-plan.md).

Inputs
  --old-html   the old index.html (git show a3f9076:index.html)
  --old-data   JSON dump of the old inline JS arrays (tools/migrate/dump_old_js.js)
  --verify     verify_final.json from the Nov 2026 verification pass
Also imports research/calendar_data.py (EVENTS, STANDING).

What is new here (not in the old site) is written out literally below, each
item with its source: project timelines and status history (for the map's
time slider), scale units, redactions, docket stages and stamps, the
connections web, and the desk log. All of it comes from
research/2026-11-wv-ai-watch-dossier.md and the old site's own sources.
"""
import argparse, json, re, sys, importlib.util, pathlib
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument('--old-html', required=True)
ap.add_argument('--old-data', required=True)
ap.add_argument('--verify', required=True)
args = ap.parse_args()

OLD = json.loads(pathlib.Path(args.old_data).read_text())
SOUP = BeautifulSoup(pathlib.Path(args.old_html).read_text(), 'html.parser')
VER = json.loads(pathlib.Path(args.verify).read_text())
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
CHECKED = '2026-11-03'

def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + '\n')
    print(f'wrote data/{name}: {len(obj) if isinstance(obj, (list, dict)) else ""}')

def inner(tag):
    """Inner HTML of a tag, with links reduced to text (sources are kept separately)."""
    html = ''.join(str(c) for c in tag.contents)
    html = re.sub(r'<a [^>]*class="story-source"[^>]*>.*?</a>', '', html, flags=re.S)
    html = re.sub(r'\s+', ' ', html).strip()
    return html

def src(label, url):
    return {'label': label, 'url': url}

# ---------------------------------------------------------------- sources used below
GM_LEGAL = 'https://www.wvgazettemail.com/news/energy_and_environment/wv-data-center-project-pushback-from-state-and-citizens-runs-into-legal-obstacles/article_b7a4f8f7-4fae-4dab-b808-cb8d0b0c1c94.html'
GM_PERMITS = 'https://www.wvgazettemail.com/news/energy_and_environment/new-permits-eyed-for-mason-co-data-center-tied-project-after-eight-figure-wv-support/article_6a2e5e86-a19e-442d-831c-24f1760bbf80.html'
GM_VIOL = 'https://www.wvgazettemail.com/news/energy_and_environment/monarch-google-data-center-project-environmental-dangers-driving-resident-opposition/article_b35e6ed1-15af-4975-9772-54b89bb5a013.html'
GM_OCT20 = 'https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html'
TC_NVDA = 'https://techcrunch.com/2026/10/30/nvidia-weighs-playing-the-cosigner-for-nscales-ai-data-center-in-west-virginia/'
HD_CERT = 'https://www.herald-dispatch.com/business/morrisey-hails-state-certifications-for-two-mason-county-data-center-projects/article_924875e0-77b4-45ab-9115-2ff4b193a6ae.html'
BTB = 'https://www.banthebots.org/explainers/ai-data-centers-in-west-virginia'
TRACKER = 'https://nearbydatacenters.org/wv/'
CAG = 'https://wvcag.org/?p=16377'
WTAP_ICA = 'https://www.wtap.com/2026/08/26/state-appeals-court-dismisses-environmental-groups-lawsuits-over-tucker-county-data-center-plant/'
POWER_SITE = 'https://www.powermag.com/contested-5-gw-ridgeline-gas-solar-and-data-center-complex-in-west-virginia-clears-site-control-question/'
NPR = 'https://www.npr.org/2026/10/31/nx-s1-5992790/data-centers-west-virginia-skiing-dark-skies'
WVPB_REDACT = 'https://wvpublic.org/story/energy-environment/citizen-groups-appeal-for-information-on-tucker-county-data-center/'
CRN = 'https://countryroads.substack.com/p/data-center-story-archive'
GM_HEALTH = 'https://www.wvgazettemail.com/news/energy_and_environment/new-report-projects-up-to-35m-in-health-damages-from-expected-tucker-co-data-center/article_0e44b758-b9d7-4040-92fa-ddf7db274333.html'
WVW_MINGO = 'https://westvirginiawatch.com/2025/12/05/mingo-county-residents-file-federal-lawsuit-against-company-building-power-plants-data-center-in-wv/'
GEM = 'https://www.gem.wiki/Adams_Fork_Data_Center_Energy_Campus'
GOV_PENZ = 'https://governor.wv.gov/article/governor-morrisey-announces-4-billion-private-investment-west-virginias-first-high-impact'
OBS_PENZ = 'https://observerwv.com/bedington-data-center-project-seeks-construction-permit/'
MN_AG = 'https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/'
OBS_QTS = 'https://observerwv.com/plan-for-data-center-complex-near-kearneysville-approved'
WDTV_HL = 'https://www.wdtv.com/2026/05/05/local-company-proposes-data-center-marion-county/'
JLL_HL = 'https://res.cloudinary.com/jll-global-sandbox/image/upload/v1755553007/MyListing/public/prod/property-875565/hog-lick-appalachian-mega-site-data-center-08-13-2025.pdf'
WTOV_TH = 'https://wtov9.com/news/local/warwood-residents-state-delegate-raise-concerns-over-proposed-data-center-at-town-hall-warwood-data-center-local-control-house-bill-2014-shawn-fluharty-health-concerns-environmental-impact-wheeling'
WTOV_50 = 'https://wtov9.com/news/local/officials-say-revised-warwood-data-center-would-draw-river-water-no-discharge-or-rate-hikes-warwood-data-center-silicon-foundation-closed-loop-river-water-no-discharge-utility-rates-shawn-fluharty'
HS_STOKES = 'https://www.heraldstaronline.com/news/local-news/2026/06/company-official-warwood-facility-will-build-modules-for-data-centers/'
WVPB_WW = 'https://wvpublic.org/story/energy-environment/states-sixth-data-center-announced-near-wheeling/'
WVTF = 'https://www.wvtf.org/news/2026-10-26/residents-gather-in-giles-to-protest-potential-monroe-county-data-center'
MM = 'https://mountainmessenger.com/?p=100074'
WVPB_FM = 'https://wvpublic.org/story/energy-environment/application-to-convert-coal-fired-fort-martin-to-gas-submitted-to-psc/'
SC_FM = 'https://www.sierraclub.org/press-releases/2026/06/sierra-club-west-virginia-files-testimony-mon-power-s-248-billion-gas-plant'
PSC_FM = 'https://www.psc.state.wv.us/scripts/WebDocket/viewCaseForWebViewForm.cfm?CaseID=85785'
PSC_MARL = 'https://www.psc.state.wv.us/scripts/WebDocket/viewCaseForWebViewForm.cfm?CaseID=85745'
VNR = 'https://valleynorthrecord.substack.com/p/regional-osint-db7'
GOV_GOOG = 'https://governor.wv.gov/article/governor-morrisey-announces-google-data-center-project-putnam-county'
MN_GOOG_A = 'https://wvmetronews.com/2026/04/14/putnam-county-residents-speak-out-about-proposed-google-data-center-near-buffalo/'
MN_GOOG_B = 'https://wvmetronews.com/2026/03/29/googles-proposed-data-center-in-buffalo-draws-both-support-and-concern/'
WSAZ_TAM = 'https://www.wsaz.com/2026/09/04/total-shocker-residents-react-second-data-center-coming-mason-county/'
WVW_TAM = 'https://westvirginiawatch.com/2026/09/08/new-data-center-project-coming-to-mason-county-wv-spearheaded-by-florida-based-real-estate-group/'
WOWK_TAM = 'https://www.wowktv.com/news/west-virginia/mason-county-wv/second-mason-co-data-center-will-land-in-west-columbia/'
BBG_NAACP = 'https://blackbygod.org/articles/news/wv-naacp-demands-moratorium-on-data-centers-microgrids-opposes-hb-2014/'
DP_SIKORA = 'https://www.dominionpost.com/2026/08/17/data-centers-in-monongalia-county-unlikely/'
HB2014_BILL = 'https://bills.wvlegislature.gov/bill/history/2025/rs/HB2014'
WVPOLICY = 'https://wvpolicy.org/five-ways-hb-2014-harms-communities-local-governments-and-schools/'
GM_4983 = 'https://www.wvgazettemail.com/news/legislative_session/wv-house-passes-data-center-enticement-bill-that-would-keep-project-details-hidden/article_d93196ac-1291-4a25-8f34-629ca46f2604.html'
PLAN_PDF = 'https://westvirginia.gov/wp-content/uploads/2026/08/Data-Center-Principles-August-2026-FINAL-8-26.pdf'
OBS_KEYS = 'https://observerwv.com/state-proposes-rule-for-fast-tracking-data-center-projects/'

# ---------------------------------------------------------------- projects
COUNTIES = {
    'monarch': ['Mason'], 'tamarack': ['Mason'], 'google': ['Putnam'], 'ridgeline': ['Tucker', 'Grant'],
    # adams-h: Holden sits just over the line in Logan; sources say 'near the Mingo-Logan county line'.
    'adams-tg': ['Mingo'], 'adams-h': ['Mingo', 'Logan'], 'penzance': ['Berkeley'], 'qts': ['Berkeley', 'Jefferson'],
    'summit': ['Jefferson'], 'hoglick': ['Marion'], 'warwood': ['Ohio'], 'monroe': ['Monroe'], 'fortmartin': ['Monongalia'],
}
# Status history drives the map's time slider. Dates are the first sourced public date.
HISTORY = {
    'monarch':   [('2026-03', 'proposed', 'Nscale buys AIPCorp; the Mason County site becomes an AI campus'), ('2026-05-05', 'construction', 'Site work under way: DEP dust warning')],
    'tamarack':  [('2026-09-03', 'certified', 'Certified at the WV Chamber summit')],
    'google':    [('2026-03-27', 'certified', 'Announced and certified')],
    'ridgeline': [('2025-05', 'proposed', 'Davis Town Council votes 5-0 to oppose'), ('2026-03-12', 'contested', 'Groups appeal the air permit')],
    'adams-tg':  [('2025-10', 'proposed', 'DEP issues air permits'), ('2025-12-03', 'contested', 'Residents file a federal suit')],
    'adams-h':   [('2025-10', 'proposed', 'DEP issues air permits'), ('2025-12-03', 'contested', 'Residents file a federal suit')],
    'penzance':  [('2026-02', 'certified', 'First certification under HB 2014')],
    'qts':       [('2025-03', 'proposed', 'Berkeley planners approve the concept plan')],
    'summit':    [('2026-04-29', 'proposed', 'Presentation to the Charles Town Utility Board reported')],
    'hoglick':   [('2026-05-05', 'proposed', 'Feasibility study announced')],
    'warwood':   [('2026-06', 'contested', 'Town halls; residents challenge HB 2014 in court')],
    'monroe':    [('2026-02', 'rumored', 'County says authority now sits with the state')],
    'fortmartin':[('2026-02', 'grid', 'Mon Power files at the PSC')],
}
T = lambda d, t, kind='event', s=None, next_=False, verify=None: {k: v for k, v in dict(d=d, t=t, kind=kind, src=s, next=next_ or None, verify=verify).items() if v}
TIMELINE = {
    'monarch': [
        T('2023', 'The WV EDA approves a forgivable $62.5M loan to Fidelis subsidiary Mountaineer GigaSystem LLC for an earlier hydrogen plan on the site. $25M was paid out and the second tranche was waived.', 'money', GM_PERMITS),
        T('2026-03', 'Nscale acquires AIPCorp (American Intelligence & Power Corp.), a Fidelis New Energy / 8090 Industries affiliate.', 'company', GM_PERMITS),
        T('2026-04-20', 'Air permit R14-0042 application filed with the DEP.', 'permit', GM_PERMITS),
        T('2026-05-05', 'DEP dust warning.', 'violation', GM_VIOL),
        T('2026-05-23', 'A silt-fence failure floods about 6 homes in Meadowlands Estates and on University Lane (May 23–24).', 'violation', GM_VIOL),
        T('2026-06-15', 'Hearing on stormwater permit WVR312628 for a 556.5-acre pipeline disturbance in Putnam and Mason.', 'permit', GM_PERMITS),
        T('2026-08-11', 'Particulate violation letter from DAQ Director Laura Crowder.', 'violation', GM_VIOL),
        T('2026-09-03', 'Certified as a High Impact Data Center at the WV Chamber summit at The Greenbrier.', 'certified', HD_CERT),
        T('2026-09-18', "Nscale's IPO filing shows a $44.6B Anthropic contract for the first 460 MW building.", 'company', TC_NVDA),
        T('2026-10-20', 'DEP air-permit workshop at Point Pleasant High School.', 'hearing', GM_OCT20),
        T('2026-10-29', 'DEP virtual public hearing on the air permit.', 'hearing', GM_OCT20),
        T('2026-10-30', 'Comment period closes. Nvidia is reported in talks to guarantee construction debt.', 'company', TC_NVDA),
        T('', 'DEP final decision on air permit R14-0042.', 'permit', next_=True),
    ],
    'tamarack': [
        T('2026-03', "A Delaware board upholds the denial of Starwood's 1.2 GW \"Project Washington.\"", 'context', WVW_TAM),
        T('2026-09-03', 'Certified as a High Impact Data Center at The Greenbrier.', 'certified', HD_CERT),
        T('2026-09-04', 'Residents call it a "total shocker."', 'community', WSAZ_TAM),
        T('', 'Construction timeline. None has been released.', 'permit', next_=True),
    ],
    'google': [
        T('2026-03-27', 'Gov. Morrisey announces the Google campus, already certified after six-plus months of closed-door meetings (revealed later by a Gazette-Mail FOIA).', 'certified', GOV_GOOG),
        T('2026-03-29', 'Support and concern; the site sits next to a 765 kV ApCo line.', 'community', MN_GOOG_B),
        T('2026-04-14', 'Putnam County residents speak out.', 'community', MN_GOOG_A),
        T('2026-07-22', 'DEP air permit application: 288 diesel emergency generators and 128 cooling towers.', 'permit', GM_VIOL),
        T('2026-08-25', 'Putnam United brings a resolution to the County Commission asking for resident input.', 'community', GM_VIOL),
        T('', 'DEP decision on the air permit application.', 'permit', next_=True),
    ],
    'ridgeline': [
        T('2025-05', 'Davis Town Council votes 5-0 to oppose the project.', 'community', CRN),
        T('2025-10', 'Groups appeal for emissions data and design details blacked out of the air permit application.', 'redaction', WVPB_REDACT),
        T('2026-02-05', 'The Air Quality Board upholds the air permit.', 'permit', GM_LEGAL),
        T('2026-03-12', 'Tucker United, WV Highlands Conservancy, and Sierra Club appeal to the Intermediate Court of Appeals.', 'court', GM_LEGAL),
        T('2026-03-16', 'House Speaker Roger Hanshaw (Bowles Rice) becomes counsel to Fundamental Data.', 'people', GM_LEGAL),
        T('2026-04-20', 'ICA Judges Daniel Greear and Charles Lorensen recuse. Chief Justice C. Haley Bunn appoints three replacements.', 'court', GM_LEGAL),
        T('2026-06-03', "The Supreme Court of Appeals denies Fundamental Data's bid to skip the ICA.", 'court', GM_LEGAL),
        T('2026-06-18', 'Commerce issues a notice that the company missed the certification deadline. It is rescinded Jul 1–2.', 'government', GM_LEGAL),
        T('2026-08-17', 'The DEP accepts a redacted purchase agreement as proof of site control.', 'redaction', POWER_SITE),
        T('2026-08-26', 'The ICA dismisses both appeals on jurisdiction, not on the merits. The groups say they will refile.', 'court', WTAP_ICA),
        T('2026-10-31', 'NPR national feature on dark skies, ski areas, and the Monongahela National Forest.', 'media', NPR),
        T('', 'Appeals refiled in circuit court or at the Supreme Court of Appeals.', 'court', next_=True),
    ],
    'adams-tg': [
        T('2025-10', 'DEP issues air permits R13-3714 / R13-3715 for two gas plants with 117 engines each.', 'permit', GEM),
        T('2025-12-03', 'Ten residents sue TransGas, the Army Corps, Fish & Wildlife, and FERC in federal court.', 'court', WVW_MINGO),
        T('2026-03', 'Judge Robert Chambers dismisses the claims against TransGas.', 'court', GM_LEGAL),
        T('2026-06-22', 'The agency claims are dismissed without prejudice. Plaintiffs can refile.', 'court', GM_LEGAL),
        T('', 'New suits under EPCRA, which attorney Stephen New says he plans.', 'court', next_=True),
    ],
    'adams-h': [
        T('2025-10', 'DEP issues the paired air permits R13-3714 / R13-3715.', 'permit', GEM),
        T('2025-12-03', 'Residents sue in federal court over the project.', 'court', WVW_MINGO),
        T('2026-06-22', 'The suit is dismissed without prejudice.', 'court', GM_LEGAL),
    ],
    'penzance': [
        T('2026-02', 'Gov. Morrisey announces WV\'s first certified "High Impact" data center: $4B, 548 acres, 600 MW.', 'certified', GOV_PENZ),
        T('2026-07-29', 'The DEP accepts the stormwater construction permit application as complete (Jul 29–30).', 'permit', OBS_PENZ),
        T('2026-09-18', 'Berkeley County asks the Attorney General how HB 2014 affects its stormwater duties.', 'government', MN_AG),
        T('2026-10-09', 'AG J.B. McCuskey declines, citing the pending Barks lawsuit.', 'government', MN_AG),
    ],
    'qts': [
        T('2025-03', 'The Berkeley County Planning Commission approves the concept plan.', 'permit', OBS_QTS),
        T('', 'Any Jefferson County filing. None found as of Nov 2026.', 'permit', next_=True),
    ],
    'summit': [
        T('2026-04-29', 'A developer presentation to the Charles Town Utility Board is reported.', 'company', TRACKER, verify='Single tracker source; no filing or news story found.'),
    ],
    'hoglick': [
        T('2025-08', 'A company sales listing advertises about 300 acres and power options up to 1 GW.', 'company', JLL_HL),
        T('2026-05-05', 'Hog Lick Aggregates announces a feasibility study for a 277-acre site in White Hall.', 'company', WDTV_HL),
    ],
    'warwood': [
        T('2026-06', 'Del. Shawn Fluharty holds a town hall at the Warwood Veterans Association. Stokes Inc. says the site will build modules for data centers.', 'community', WTOV_TH),
        T('', 'Twelve residents file Barks v. Silicon Foundation in Ohio County Circuit Court, challenging HB 2014 (filing date not confirmed).', 'court', MN_AG),
        T('', 'The project is revised to 50 MW, under the 90 MW HB 2014 line, so the City of Wheeling keeps review.', 'company', WTOV_50),
        T('2026-10-09', "The AG's office cites Barks in declining Berkeley County's opinion request.", 'court', MN_AG),
    ],
    'monroe': [
        T('2026-02', 'The County Commission says authority now sits with the state and refers residents to legislators.', 'government', MM),
        T('2026-10-26', 'Residents protest outside the Giles County, VA law office of landowner Jason Buckland.', 'protest', WVTF),
    ],
    'fortmartin': [
        T('2026-02', 'Mon Power / Potomac Edison file PSC Case 26-0108-E-CN: 1,200 MW gas plus 70 MW solar, $2.48B.', 'psc', WVPB_FM),
        T('2026-06', 'Sierra Club WV files testimony contesting cost recovery.', 'psc', SC_FM),
        T('2026-07-15', 'Public comment hearing.', 'hearing', PSC_FM),
        T('2026-08-28', 'Ten parties file initial briefs.', 'psc', PSC_FM),
        T('2026-09-14', 'Reply briefs close. The case is fully briefed.', 'psc', PSC_FM),
        T('2027-02', 'Decision deadline reported by the Dominion Post.', 'psc', next_=True, verify='Reported by the Dominion Post, but we could not open the article to confirm it. Check the PSC docket.'),
    ],
}
SCALE = {
    'monarch': {'n': 864, 'unit': 'reciprocating gas engines', 'color': 'gas', 'extra': {'n': 12, 'unit': 'diesel generators', 'color': 'alarm'},
                'caption': 'Each orange dot is one gas engine in the 2.16 GW off-grid microgrid. The 12 red dots are its diesel generators.', 'src': GM_PERMITS,
                'bars': {'title': 'Projected emissions, tons per year', 'rows': [['CO', 1043], ['VOC', 900], ['NOx', 506], ['PM2.5', 38]], 'src': GM_PERMITS}},
    'google': {'n': 288, 'unit': 'diesel emergency generators', 'color': 'alarm', 'extra': {'n': 128, 'unit': 'cooling towers', 'color': 'grid'},
               'caption': 'Each red dot is one 2,750 kW diesel emergency generator in the DEP air application. Blue dots are its 128 cooling towers.', 'src': GM_VIOL},
    'ridgeline': {'n': 30, 'unit': 'million gallons of diesel storage', 'color': 'gas', 'big': True,
                  'caption': 'Each block is 1 million gallons of diesel storage: three 10-million-gallon tanks backing a 785 MW gas plant.', 'src': POWER_SITE},
    'adams-tg': {'n': 117, 'unit': 'gas engines at this plant', 'color': 'gas', 'caption': 'Each dot is one of the 117 engines in the Twisted Gun plant. The Harless plant has another 117.', 'src': GM_LEGAL},
    'adams-h': {'n': 117, 'unit': 'gas engines at this plant', 'color': 'gas', 'caption': 'Each dot is one of the 117 engines in the Harless plant. The Twisted Gun plant has another 117.', 'src': GM_LEGAL},
}
REDACTIONS = {
    'monarch': [{'label': 'Certification petition', 'why': 'Confidential under HB 4983 (2026).', 'src': GM_4983}],
    'tamarack': [{'label': 'Certification petition', 'why': 'Confidential under HB 4983 (2026).', 'src': GM_4983}],
    'google': [{'label': 'Certification petition', 'why': 'Confidential under HB 4983 (2026).', 'src': GM_4983}],
    'penzance': [{'label': 'Certification petition', 'why': 'Confidential under HB 4983 (2026).', 'src': GM_4983}],
    'ridgeline': [
        {'label': 'Air permit application: emissions data and design details', 'why': 'Blacked out by the company. Citizen groups appealed for their release (Oct 2025).', 'src': WVPB_REDACT},
        {'label': 'Purchase agreement used as proof of site control', 'why': 'Accepted by the DEP in redacted form on Aug 17, 2026.', 'src': POWER_SITE},
    ],
}
FACT_VERIFY = {('fortmartin', 'PSC'): 'The Feb 2027 deadline was reported by the Dominion Post, but we could not open the article to confirm it. Check the PSC docket.'}

projects = []
for p in OLD['PROJECTS']:
    pid = p['id']
    q = {
        'id': pid, 'short': p['short'], 'name': p['name'], 'status': p['status'],
        'place': p['county'], 'counties': COUNTIES[pid], 'lat': p['lat'], 'lng': p['lng'],
        'developer': p['developer'],
        'facts': [{'k': k, 'v': v, **({'verify': FACT_VERIFY[(pid, k)]} if (pid, k) in FACT_VERIFY else {})} for k, v in p['facts']],
        'latest': p['latest'],
        'history': [{'d': d, 'status': s, 't': t} for d, s, t in HISTORY[pid]],
        'timeline': TIMELINE.get(pid, []),
        'sources': [src(l, u) for l, u in p['sources']],
        'checked': CHECKED,
    }
    if p.get('verify'): q['verify'] = p['verify']
    if pid in SCALE: q['scale'] = SCALE[pid]
    if pid in REDACTIONS: q['redactions'] = REDACTIONS[pid]
    projects.append(q)
write('projects.json', projects)

lines = []
LINE_META = {
    'marl': dict(short='MARL 500 kV', status='psc', appears='2026-01', appears_note='Early 2026: PSC Case 26-0075-E-CN opened (date from the case number).',
                 counties=['Monongalia', 'Preston', 'Mineral', 'Hampshire'], sources=[src('PSC docket', PSC_MARL), src('Valley North Record', VNR)]),
    'valleylink': dict(short='Valley Link 765 kV', status='prefiling', appears='2026-09-14', appears_note='Sep 14, 2026: the PSC opens comment file FP Valley Link 26A.',
                       counties=['Putnam', 'Kanawha', 'Roane', 'Gilmer', 'Lewis', 'Upshur', 'Barbour', 'Preston', 'Tucker', 'Grant', 'Hardy', 'Hampshire'],
                       sources=[src('Valley North Record', VNR), src('Dominion Post, Sep 16, 2026', 'https://www.dominionpost.com/2026/09/16/psc-opens-case-file-for-valley-link-transmission-line-protests/'), src('WMRA (county opposition)', 'https://www.wmra.org/2026-08-25/the-growing-county-government-opposition-to-valley-link')]),
}
for l in OLD['LINES']:
    lines.append({'id': l['id'], 'name': l['name'], 'note': l['note'], 'pts': l['pts'], **LINE_META[l['id']]})
write('lines.json', lines)

# ---------------------------------------------------------------- docket (parsed from the old HTML)
BODY = {'01': 'courts', '02': 'psc', '03': 'dep', '04': 'legislature'}
# stage: prefiling | open | briefing | awaiting | closed
DOCKET_META = {
    'Barks v. Silicon Foundation': dict(id='barks', stage='open', stamp='Pending', tone='legal', projects=['warwood']),
    'Tucker United, WVHC & Sierra Club v. DEP (Ridgeline air permit)': dict(id='ridgeline-appeal', stage='closed', stamp='Dismissed · refiling', tone='alarm', projects=['ridgeline'], next={'t': 'Appeals refiled', 'd': ''}),
    'Mingo County residents v. TransGas, Army Corps, USFWS & FERC': dict(id='mingo-suit', stage='closed', stamp='Dismissed w/o prejudice', tone='dim', projects=['adams-tg', 'adams-h']),
    'Possible county challenge to HB 2014': dict(id='county-challenge', stage='prefiling', stamp='Under discussion', tone='dim', projects=['google', 'fortmartin'], counties=['Putnam', 'Monongalia']),
    'MARL 500 kV line (NextEra Energy Transmission MidAtlantic)': dict(id='marl', stage='briefing', stamp='Decision due Mar 6, 2027', tone='cyan', projects=['marl'], next={'t': 'PSC decision due', 'd': '2027-03-06'}),
    'Fort Martin 1,200 MW gas plant + 70 MW solar ($2.48B)': dict(id='fortmartin', stage='awaiting', stamp='Fully briefed', tone='signal', projects=['fortmartin'], next={'t': 'Decision deadline (reported)', 'd': '2027-02', 'verify': True}),
    'Appalachian Power / Wheeling Power large-load tariff': dict(id='apco-tariff', stage='closed', stamp='In effect', tone='ok', projects=['tamarack', 'warwood']),
    'PJM capacity market investigation: AEP\'s "FRR" status and Mon Power bidding': dict(id='frr', stage='open', stamp='Staff rec ~Dec 29', tone='signal', projects=['hb2014'], next={'t': 'PSC Staff recommendation', 'd': '2026-12-29'}),
    'Mon Power / Potomac Edison Integrated Resource Plan': dict(id='irp', stage='open', stamp='Data due Dec 1', tone='signal', projects=['fortmartin'], next={'t': 'IRP data due', 'd': '2026-12-01'}),
    'HB 2014 generating-capacity rules: 69% coal capacity factor becomes "a goal, not a mandate"': dict(id='capacity-rule', stage='open', stamp='At Legislature · Nov 10', tone='signal', projects=['hb2014'], next={'t': 'Rule-Making Review Committee', 'd': '2026-11-10'}),
    'Valley Link 765 kV: protests before the formal application': dict(id='valleylink', stage='prefiling', stamp='Pre-filing', tone='grid', projects=['valleylink']),
    'Monarch Cloud Campus LLC: 2.16 GW, 864 gas engines': dict(id='monarch-air', stage='awaiting', stamp='Awaiting decision', tone='signal', projects=['monarch'], next={'t': 'DEP final decision', 'd': ''}),
    'Monarch violations: sediment, flooding, dust': dict(id='monarch-enforcement', stage='open', stamp='Enforcement', tone='alarm', projects=['monarch']),
    'Buffalo campus: 288 diesel generators, 128 cooling towers': dict(id='google-air', stage='open', stamp='Application filed Jul 22', tone='signal', projects=['google']),
    'TransGas Adams Fork plants, Mingo County': dict(id='adams-air', stage='closed', stamp='Issued Oct 2025', tone='dim', projects=['adams-tg', 'adams-h']),
    'Power Generation and Consumption Act': dict(id='hb2014', stage='closed', stamp='Law · 2025', tone='dim', projects=['hb2014']),
    'Certification rule + confidentiality': dict(id='hb4983', stage='closed', stamp='Law · 2026', tone='dim', projects=['hb2014']),
    'Responsible Data Center Development Plan': dict(id='gov-plan', stage='closed', stamp='Adopted Aug 11', tone='dim', projects=['hb2014']),
    'Repeal or amend HB 2014': dict(id='reform', stage='prefiling', stamp='2027 session', tone='legal', projects=['hb2014'], next={'t': '2027 Regular Session convenes', 'd': '2027-01-13'}),
}
docket = []
for col in SOUP.select('#docket .docket-col'):
    num = col.select_one('.docket-title .num').get_text(strip=True)
    for it in col.select('.docket-item'):
        meta = it.select_one('.docket-meta')
        pill = meta.select_one('.pill')
        where = meta.get_text(' ', strip=True).replace(pill.get_text(strip=True), '', 1).strip()
        title = it.select_one('.docket-name').get_text(strip=True)
        p = it.select_one('p')
        vfy = p.select_one('.vfy') if p else None
        verify = vfy.get('title') if vfy else None
        if vfy: vfy.decompose()
        m = DOCKET_META[title]
        case = re.search(r'(Case \S+|Air permits? \S+(?: / \S+)?|FP Valley Link 26A|HB \d+)', where)
        docket.append({
            'id': m['id'], 'body': BODY[num], 'title': title, 'where': where, 'case': case.group(1) if case else '',
            'status': pill.get_text(strip=True), 'stage': m['stage'], 'stamp': m['stamp'], 'tone': m['tone'],
            'summary': inner(p) if p else '', 'projects': m['projects'], 'counties': m.get('counties', []),
            'next': m.get('next'), 'sources': [src(a.get_text(strip=True).rstrip(' →'), a['href']) for a in it.select('a.story-source')],
            **({'verify': verify} if verify else {}), 'checked': CHECKED,
        })
write('docket.json', docket)

# ---------------------------------------------------------------- people (directory)
PEOPLE_PROJECTS = [  # name substring -> project ids, for case-file "People" tabs
    ('Morrisey', ['hb2014', 'penzance', 'google', 'monarch', 'tamarack']), ('McCuskey', ['warwood', 'penzance', 'hb2014']),
    ('Hanshaw', ['ridgeline']), ('Preservati', ['ridgeline']), ('Crowder', ['monarch']), ('Kessler', ['monarch']),
    ('Chris Morris', ['hb2014']), ('Randy Smith', ['ridgeline']), ('Robbie Morris', ['valleylink']), ('Leonhardt', ['valleylink']),
    ('Fluharty', ['warwood', 'hb2014']), ('Pushkin', ['hb2014']), ('Riley Moore', ['hb2014']), ('Skidmore', ['google']),
    ('Gochenour', ['penzance']), ('Cara Keys', ['summit', 'qts']), ('Sikora', ['fortmartin', 'marl']), ('Salango', ['valleylink']),
    ('Chambers', ['adams-tg', 'adams-h']), ('Greear', ['ridgeline']), ('Lorensen', ['ridgeline']), ('Egnatoff', ['marl']),
    ('Nscale', ['monarch']), ('Anthropic', ['monarch']), ('Nvidia', ['monarch']), ('Fidelis', ['monarch']), ('Starwood', ['tamarack']),
    ('Google', ['google']), ('Penzance', ['penzance']), ('Fundamental Data', ['ridgeline']), ('TransGas', ['adams-tg', 'adams-h']),
    ('Silicon Foundation', ['warwood']), ('Hog Lick', ['hoglick']), ('QTS', ['qts', 'summit']), ('Bowles Rice', ['ridgeline', 'monarch']),
    ('Fort Martin intervenors', ['fortmartin']), ('Utilities', ['fortmartin', 'marl', 'valleylink']), ('Accountability Project', ['hb2014']),
    ('Citizen Action', ['hb2014', 'fortmartin']), ('Tucker United', ['ridgeline']), ('Highlands Conservancy', ['ridgeline']),
    ('Sierra Club', ['ridgeline', 'fortmartin']), ('Putnam United', ['google']), ('Mason WV United', ['monarch', 'tamarack']),
    ('Eastern Panhandle', ['penzance', 'qts']), ('NAACP', ['hb2014']), ('Energy Efficient', ['fortmartin']), ('MARL intervenors', ['marl']),
    ('Appalachian Mountain Advocates', ['ridgeline', 'adams-tg', 'adams-h']), ('Stop Valley Link', ['valleylink']), ('Reporters', []),
]
people = []
for col in SOUP.select('#people .people-col'):
    group = col.select_one('.people-head').get_text(strip=True)
    for li in col.select('li'):
        ps = li.select_one('.psrc')
        sources = [src(a.get_text(strip=True).rstrip(' ↗'), a['href']) for a in ps.select('a')] if ps else []
        if ps: ps.decompose()
        name = li.select_one('strong').get_text(strip=True)
        li.select_one('strong').decompose()
        role = re.sub(r'\s+', ' ', ''.join(str(c) for c in li.contents)).strip()
        proj = next((v for k, v in PEOPLE_PROJECTS if k in name), [])
        people.append({'id': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:40], 'group': group, 'name': name, 'role': role, 'projects': proj, 'sources': sources})
write('people.json', people)

# ---------------------------------------------------------------- connections web
N = lambda id, label, kind, sub='', project=None: {k: v for k, v in dict(id=id, label=label, kind=kind, sub=sub, project=project).items() if v}
nodes = [
    N('bowles-rice', 'Bowles Rice', 'firm', 'Charleston law firm'), N('hanshaw', 'Roger Hanshaw', 'person', 'House Speaker (R-Clay)'),
    N('w-lorensen', 'William Lorensen', 'person', 'attorney'), N('c-lorensen', 'Judge Charles Lorensen', 'person', 'ICA judge'),
    N('greear', 'Judge Daniel Greear', 'person', 'ICA chief judge'), N('markham', 'Peter Markham', 'person', 'attorney'),
    N('fundamental', 'Fundamental Data', 'company'), N('ridgeline', 'Ridgeline', 'project', 'Tucker Co.', 'ridgeline'),
    N('ica', 'ICA appeal (Ridgeline)', 'case', 'dismissed Aug 26'), N('tucker-united', 'Tucker United', 'group', 'Amy Margolies'),
    N('wvhc', 'WV Highlands Conservancy', 'group'), N('sierra', 'Sierra Club WV', 'group'), N('ama', 'Appalachian Mountain Advocates', 'firm', 'public-interest law'),
    N('preservati', 'Nick Preservati', 'person', 'Commerce Deputy Secretary'), N('mgs', 'MGS CNP 1 LLC', 'company', 'Fidelis affiliate'),
    N('fidelis', 'Fidelis New Energy', 'company'), N('aipcorp', 'AIPCorp', 'company', 'American Intelligence & Power'),
    N('nscale', 'Nscale', 'company', 'UK'), N('monarch', 'Monarch', 'project', 'Mason Co.', 'monarch'), N('anthropic', 'Anthropic', 'company'),
    N('nvidia', 'Nvidia', 'company'), N('crowder', 'Laura Crowder', 'person', 'DEP air quality director'),
    N('mason-united', 'Mason WV United', 'group', 'Elaine Matheny'), N('morrisey', 'Gov. Patrick Morrisey', 'person'),
    N('tamarack', 'Project Tamarack', 'project', 'Mason Co.', 'tamarack'), N('starwood', 'Starwood Digital Ventures', 'company', 'CEO Anthony Balestrieri'),
    N('google-proj', 'Google Buffalo campus', 'project', 'Putnam Co.', 'google'), N('cumulus', 'Google / Cumulus Group LLC', 'company'),
    N('putnam-united', 'Putnam United', 'group'), N('skidmore', 'Andy Skidmore', 'person', 'Putnam Commission president'),
    N('county-suit', 'Possible county suit over HB 2014', 'case', 'not filed'), N('sikora', 'Sean Sikora', 'person', 'Monongalia commissioner'),
    N('penzance', 'Penzance Bedington', 'project', 'Berkeley Co.', 'penzance'), N('penzance-co', 'Penzance / Bedington Owner LLC', 'company'),
    N('stephen-new', 'Stephen New', 'person', 'attorney, Beckley'), N('mingo-suit', 'Mingo residents v. TransGas', 'case', 'dismissed w/o prejudice'),
    N('chambers', 'Judge Robert Chambers', 'person', 'U.S. District Court'), N('transgas', 'TransGas Development Systems', 'company', 'CEO Adam Victor'),
    N('adams', 'Adams Fork campuses', 'project', 'Mingo Co.', 'adams-tg'), N('qts', 'QTS Kearneysville', 'project', 'Berkeley / Jefferson', 'qts'),
    N('mccuskey', 'AG J.B. McCuskey', 'person'), N('barks', 'Barks v. Silicon Foundation', 'case', 'pending'),
    N('silicon', 'Silicon Foundation Energy', 'company'), N('warwood', 'Centre Foundry / Warwood', 'project', 'Wheeling', 'warwood'),
    N('fluharty', 'Del. Shawn Fluharty', 'person', 'D-Ohio'), N('monpower', 'Mon Power / FirstEnergy', 'company'),
    N('fortmartin', 'Fort Martin gas addition', 'project', 'Monongalia Co.', 'fortmartin'), N('hb2014', 'HB 2014', 'law', '2025'),
    N('naacp', 'WV NAACP', 'group', 'Loretta Young'),
]
E = lambda a, b, label, url, note='': {k: v for k, v in dict(a=a, b=b, label=label, src=url, note=note).items() if v}
edges = [
    E('hanshaw', 'bowles-rice', 'attorney at', GM_LEGAL), E('w-lorensen', 'bowles-rice', 'attorney at', GM_LEGAL), E('markham', 'bowles-rice', 'attorney at', GM_PERMITS),
    E('hanshaw', 'fundamental', 'counsel since Mar 16, 2026', GM_LEGAL), E('fundamental', 'ridgeline', 'developer', GM_LEGAL),
    E('w-lorensen', 'ica', 'on the case', GM_LEGAL), E('c-lorensen', 'w-lorensen', 'father of', GM_LEGAL), E('c-lorensen', 'ica', 'recused', GM_LEGAL),
    E('greear', 'ica', 'recused', GM_LEGAL), E('ica', 'ridgeline', 'air permit appeal', WTAP_ICA),
    E('tucker-united', 'ica', 'appellant', GM_LEGAL), E('wvhc', 'ica', 'appellant', GM_LEGAL), E('sierra', 'ica', 'appellant', GM_LEGAL),
    E('ama', 'ica', 'counsel for appellants', GM_LEGAL), E('preservati', 'fundamental', 'notice issued, then rescinded', GM_LEGAL),
    E('markham', 'mgs', 'wrote to the DEP for', GM_PERMITS, 'Told the DEP the project had shifted from hydrogen to data centers.'),
    E('mgs', 'fidelis', 'affiliate of', GM_PERMITS), E('aipcorp', 'fidelis', 'affiliate of', BTB), E('mgs', 'monarch', 'site became', GM_PERMITS),
    E('nscale', 'aipcorp', 'acquired Mar 2026', GM_PERMITS), E('nscale', 'monarch', 'developer', HD_CERT),
    E('anthropic', 'monarch', '$44.6B contract, first 460 MW building', TC_NVDA), E('nvidia', 'nscale', 'debt guarantee talks', TC_NVDA),
    E('crowder', 'monarch', 'signed Aug 11 violation letter', GM_VIOL), E('mason-united', 'monarch', 'residents organizing', CAG),
    E('mason-united', 'tamarack', 'residents organizing', CAG), E('starwood', 'tamarack', 'developer', WOWK_TAM),
    E('morrisey', 'monarch', 'announced certification', HD_CERT), E('morrisey', 'tamarack', 'announced certification', HD_CERT),
    E('morrisey', 'penzance', 'announced certification', GOV_PENZ), E('morrisey', 'google-proj', 'announced project', GOV_GOOG),
    E('morrisey', 'hb2014', 'championed', HD_CERT), E('cumulus', 'google-proj', 'developer', GM_VIOL), E('putnam-united', 'google-proj', 'residents organizing', CAG),
    E('skidmore', 'county-suit', 'says Putnam discussed suing', GM_VIOL), E('sikora', 'county-suit', 'says the law takes county rights', DP_SIKORA),
    E('county-suit', 'hb2014', 'would challenge', GM_VIOL), E('penzance-co', 'penzance', 'developer', GOV_PENZ),
    E('stephen-new', 'mingo-suit', 'counsel for residents', GM_LEGAL), E('chambers', 'mingo-suit', 'dismissed', GM_LEGAL),
    E('mingo-suit', 'transgas', 'defendant', WVW_MINGO), E('transgas', 'adams', 'developer', GM_LEGAL),
    E('stephen-new', 'penzance', 'named as a future target', GM_LEGAL), E('stephen-new', 'qts', 'named as a future target', GM_LEGAL),
    E('mccuskey', 'barks', 'defends HB 2014', MN_AG), E('barks', 'hb2014', 'challenges', MN_AG), E('barks', 'warwood', 'residents vs. developer', MN_AG),
    E('silicon', 'warwood', 'developer', HS_STOKES), E('fluharty', 'warwood', 'held town halls', WTOV_TH),
    E('monpower', 'fortmartin', 'applicant, PSC 26-0108', WVPB_FM), E('sierra', 'fortmartin', 'intervenor', SC_FM),
    E('naacp', 'hb2014', 'demands moratorium', BBG_NAACP), E('monarch', 'hb2014', 'certified under', HD_CERT), E('penzance', 'hb2014', 'certified under', GOV_PENZ),
]
ids = {n['id'] for n in nodes}
assert all(e['a'] in ids and e['b'] in ids for e in edges), [e for e in edges if e['a'] not in ids or e['b'] not in ids]
write('network.json', {'nodes': nodes, 'edges': edges, 'checked': CHECKED})

# ---------------------------------------------------------------- hubs ("the other AI story")
hubs = []
for sec in SOUP.select('section.city-section'):
    stories = []
    for s in sec.select('.story-item .story-text'):
        title = s.select_one('strong').get_text(strip=True)
        sources = [src(a.get_text(strip=True).replace('Source: ', '').rstrip(' →'), a['href']) for a in s.select('a.story-source')]
        s.select_one('strong').decompose()
        stories.append({'title': title, 'html': inner(s), 'sources': sources})
    hubs.append({'id': sec['data-city'], 'name': sec.select_one('.city-name').get_text(strip=True), 'tag': sec.select_one('.city-tag').get_text(strip=True), 'major': True, 'stories': stories})
for card in SOUP.select('.future-hub-card'):
    stories = []
    for s in card.select('.future-hub-story'):
        title = s.select_one('strong').get_text(strip=True)
        sources = [src(a.get_text(strip=True).replace('Source: ', '').rstrip(' →'), a['href']) for a in s.select('a.story-source')]
        s.select_one('strong').decompose()
        stories.append({'title': title, 'html': inner(s), 'sources': sources})
    name = card.select_one('.future-hub-name').get_text(strip=True)
    hubs.append({'id': re.sub(r'[^a-z]+', '-', name.lower()).strip('-'), 'name': name, 'tag': card.select_one('.future-hub-tag').get_text(strip=True),
                 'pop': card.select_one('.future-hub-pop').get_text(strip=True), 'major': False, 'stories': stories})
coords = {h['id']: (h['lat'], h['lng']) for h in OLD['HUBS']}
coords.update({re.sub(r'[^a-z]+', '-', h['name'].lower()).strip('-'): (h['lat'], h['lng']) for h in OLD['EMERGING_HUBS']})
coords['tucker-county'] = (39.128, -79.465)  # Davis, WV (the old site had no marker for this card)
for h in hubs:
    c = coords.get(h['id']) or coords.get(h['name'].lower())
    if c: h['lat'], h['lng'] = c
write('hubs.json', hubs)

# ---------------------------------------------------------------- calendar (from research/calendar_data.py)
sys.argv = ['calendar_data']
spec = importlib.util.spec_from_file_location('calendar_data', ROOT / 'research' / 'calendar_data.py')
cd = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(cd)
except SystemExit:
    pass
def ev(e):
    e = dict(e)
    e['sources'] = [src(l, u) for l, u in e.get('sources', [])]
    return e
write('events.json', [ev(e) for e in cd.EVENTS])
write('standing.json', [dict(s) for s in cd.STANDING])

# ---------------------------------------------------------------- desk log (front-page ticker + "On the desk")
desk = [
    dict(d='2026-11-02', t='Stop Valley Link peaceful protest at the Barbour County Courthouse in Philippi.', project='valleylink', src=VNR),
    dict(d='2026-10-31', t="NPR takes Ridgeline's dark-sky and ski-area fight national.", project='ridgeline', src=NPR),
    dict(d='2026-10-30', t="Nvidia is in talks to guarantee billions in construction debt for Monarch's Anthropic building.", project='monarch', src=TC_NVDA),
    dict(d='2026-10-30', t='The DEP closes comments on Monarch air permit R14-0042. A final decision is pending.', project='monarch', src=GM_OCT20),
    dict(d='2026-10-26', t='MARL evidentiary hearing opens at the PSC.', project='marl', src=PSC_MARL),
    dict(d='2026-10-26', t='Monroe County residents protest a potential data center outside a landowner\'s law office in Giles County, VA.', project='monroe', src=WVTF),
    dict(d='2026-10-09', t="AG J.B. McCuskey declines Berkeley County's request for an HB 2014 opinion, citing the Barks case.", project='penzance', src=MN_AG),
    dict(d='2026-09-18', t="Nscale's IPO filing shows a $44.6B Anthropic contract for Monarch's first 460 MW building.", project='monarch', src=TC_NVDA),
    dict(d='2026-09-03', t='Monarch and Tamarack are certified at The Greenbrier. Mason County now hosts two High Impact Data Centers.', project='monarch', src=HD_CERT),
    dict(d='2026-08-26', t='The ICA dismisses the Ridgeline air-permit appeals on jurisdiction. The groups say they will refile.', project='ridgeline', src=WTAP_ICA),
]
write('desk.json', desk)

# ---------------------------------------------------------------- receipts (verification pass, Nov 3, 2026)
from collections import Counter
rows = [{'sec': r['sec'], 'title': r['title'], 'status': r['status'], 'note': r.get('note', ''), 'urls': r['urls'], 'method': r.get('method', [])} for r in VER]
write('receipts.json', {'checked': CHECKED, 'summary': dict(Counter(r['status'] for r in rows)), 'rows': rows,
                        'log': 'research/2026-11-verification-log.md'})

write('meta.json', {'updated': CHECKED, 'version': '2.0.0', 'site': 'https://wvaihub.com',
                    'repo': 'https://github.com/m0ntan1/WV-AI-HUB', 'note': 'Data as of Nov 3, 2026. See docs/update-plan.md for how this is kept current.',
                    'stats': [
                        {'v': '2.16 GW', 'l': "Monarch's off-grid gas microgrid, Mason County", 'src': GM_PERMITS, 'srcLabel': 'Gazette-Mail: permits'},
                        {'v': '864', 'l': 'reciprocating gas engines in that microgrid', 'src': GM_PERMITS, 'srcLabel': 'Gazette-Mail: permits'},
                        {'v': '2,000+', 'l': 'protest signatures and letters filed against the MARL line at the PSC', 'src': PSC_MARL, 'srcLabel': 'PSC Case 26-0075 (via docket digests)'},
                        {'v': '{events}', 'l': 'public dates on the calendar, with addresses'},
                    ]})
