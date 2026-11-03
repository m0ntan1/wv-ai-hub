"""SUPERSEDED Nov 3, 2026: data/events.json and data/standing.json are now the source of truth
(see docs/update-plan.md). This file is kept as the receipt for the Nov 2026 calendar research;
tools/migrate/migrate_v1.py read it once to create those JSON files.

Originally: single source for the WV AI Watch calendar.
Usage: python3 research/calendar_data.py research/2026-11-calendar.md /tmp/calendar-data.js
Emits the receipts Markdown and the EVENTS/STANDING block that is pasted into index.html.
Times are US Eastern. Fields: id, date (YYYY-MM-DD), end, start/endt (HH:MM 24h), label (display
override), approx (bool: date not exact -> no .ics), tbd (bool), type, title, desc, venue, address,
county, virtual, host, how (how to take part), project, flag (caveat), sources [[label,url]].
"""
import json, pathlib, sys

PSC_DOC = 'https://www.psc.state.wv.us/scripts/WebDocket/ViewDocument.cfm?CaseActivityID='
PSC_CASE = 'https://www.psc.state.wv.us/scripts/WebDocket/viewCaseForWebViewForm.cfm?CaseID='
VL = ['Valley Link: open-house schedule', 'https://vltransmission.com/valley-north/']
VL_PSC = ['How to comment (FP Valley Link 26A)', 'https://www.dominionpost.com/2026/09/16/psc-opens-case-file-for-valley-link-transmission-line-protests/']
VNR = ['Valley North Record', 'https://valleynorthrecord.substack.com/p/regional-osint-db7']
INTERIMS = ['Legislature: interim schedule', 'https://www.wvlegislature.gov/committees/interims/interims.cfm']
CAPITOL = '1900 Kanawha Blvd. E., Charleston, WV 25305'
PSC_HQ = '201 Brooks St., Charleston, WV 25301'
VL_HOW = 'Drop in any time during the window. This is a developer event, not a PSC hearing. To put comments on the official record, file with the PSC under FP Valley Link 26A.'

def vl(id, date, start, endt, town, venue, address, county):
    return dict(id=id, date=date, start=start, endt=endt, type='developer',
                title=f'Valley Link open house: {town}',
                desc='Valley Link (Dominion, FirstEnergy, Transource) shows preliminary route options for the 765 kV Valley North line and takes feedback.',
                venue=venue, address=address, county=county, host='Valley Link Transmission Co.',
                how=VL_HOW, project='valleylink', sources=[VL, VL_PSC])

EVENTS = [
  # ── Upcoming ──────────────────────────────────────────────
  dict(id='election', date='2026-11-03', start='06:30', endt='19:30', type='government',
       title='General Election Day',
       desc='HB 2014 (data-center local control) and high-voltage transmission lines are top issues in legislative races.',
       county='Statewide', host='WV Secretary of State', how='Vote at your assigned polling place, 6:30 a.m. to 7:30 p.m.',
       project='hb2014', sources=[['WV MetroNews', 'https://wvmetronews.com/2026/10/30/data-centers-transmission-lines-highlight-issues-driving-voter-turnout-in-west-virginia/']]),
  dict(vl('vl-fisher', '2026-11-04', '16:00', '19:00', 'Fisher', 'Misty Mountain Event Barn', '430 Misty Mountain Rd., Fisher, WV 26818', 'Hardy'),
       desc='First of 12 sessions on preliminary routes for the 765 kV Valley North line. Four more are out of state: Winchester, VA (Nov 5), Lovettsville, VA (Nov 12), and Brunswick, MD (Nov 19).'),
  vl('vl-hambleton', '2026-11-04', '17:00', '20:00', 'Hambleton', 'Tucker County High School', '116 Mountain Lion Way, Hambleton, WV 26269', 'Tucker'),
  vl('vl-sissonville', '2026-11-05', '17:00', '20:00', 'Sissonville', 'Sissonville Middle School', '100 Middle School Ln., Charleston, WV 25312', 'Kanawha'),
  dict(id='interims-nov', date='2026-11-09', end='2026-11-11', type='legislature',
       title='Legislative interim meetings',
       desc='Joint interim committees meet between sessions. The Rule-Making Review Committee takes up the PSC\'s HB 2014 capacity rule on Nov 10 (see that entry).',
       venue='State Capitol', address=CAPITOL, county='Kanawha', host='WV Legislature',
       how='Open to the public. Agendas are posted on the Legislature\'s interim page.',
       project='hb2014', sources=[INTERIMS]),
  dict(id='rmr-150csr41', date='2026-11-10', start='12:00', endt='17:00', type='legislature',
       title='Rule-Making Review Committee: the PSC\'s HB 2014 capacity rule',
       desc='On the agenda: 150 CSR 41, the PSC\'s rules for generating capacity and economic dispatch, written in Case 26-0633-E-GI. This is the rule that made a 69% coal capacity factor a goal instead of a mandate.',
       venue='Senate Judiciary Committee room, State Capitol', address=CAPITOL, county='Kanawha', host='Legislative Rule-Making Review Committee',
       how='Open to the public. The committee can recommend the rule be approved, amended, or withdrawn before the 2027 session.',
       project='hb2014', sources=[['Interim agenda (Nov 9–11)', 'https://www.wvlegislature.gov/committees/interims/intcomsched_agenda.cfm?day1=11/09/2026'], ['West Virginia Watch', 'https://westvirginiawatch.com/2026/10/20/west-virginia-public-service-commission-makes-power-rule-a-goal-not-a-mandate/']]),
  vl('vl-buckhannon', '2026-11-12', '16:00', '19:00', 'Buckhannon', 'The Event Center at Brushy Fork', '929 Brushy Fork Rd., Buckhannon, WV 26201', 'Upshur'),
  vl('vl-spencer', '2026-11-17', '16:00', '19:00', 'Spencer', 'Spencer Armory', '206 E. Main St., Spencer, WV 25276', 'Roane'),
  vl('vl-capon', '2026-11-17', '16:00', '19:00', 'Capon Bridge', 'Capon Bridge Community Complex (Old Capon Bridge Middle School)', '195 Capon School St., Capon Bridge, WV 26711', 'Hampshire'),
  dict(id='tu-smallbiz', date='2026-11-17', start='17:00', endt='19:00', type='community',
       title='Tucker United small business meeting',
       desc='A meeting for local businesses, hosted by Tucker United and a Thomas business owner.',
       venue='McClumsy', address='Front St., Thomas, WV 26292', county='Tucker', host='Tucker United',
       how='Open to the public.', project='ridgeline', sources=[['Tucker United events', 'https://www.tuckerunited.com/about-7']]),
  vl('vl-roanoke', '2026-11-18', '16:00', '19:00', 'Roanoke', 'Stonewall Resort, Roanoke Event Center', '940 Resort Dr., Roanoke, WV 26447', 'Lewis'),
  vl('vl-ranson', '2026-11-18', '16:00', '19:00', 'Ranson', 'Ranson Civic Center', '432 W. 2nd Ave., Ranson, WV 25438', 'Jefferson'),
  vl('vl-glenville', '2026-11-19', '16:00', '19:00', 'Glenville', 'Gilmer County Recreation Center', '1365 Sycamore Run, Glenville, WV 26351', 'Gilmer'),
  dict(id='marl-briefs', date='2026-11-23', type='psc',
       title='MARL initial briefs due (unconfirmed)',
       desc='Parties in PSC Case 26-0075-E-CN file their initial briefs or proposed orders on NextEra\'s 500 kV line.',
       county='Statewide', host='PSC, Case 26-0075-E-CN', how='Filed by parties. Anyone can read the briefs on the PSC docket.',
       flag='Date from Valley North Record. No briefing order appeared in PSC docket notices through Nov 2.',
       project='marl', sources=[VNR, ['PSC docket', PSC_CASE + '85745']]),
  dict(id='irp-data', date='2026-12-01', type='psc',
       title='Mon Power IRP data due',
       desc='Mon Power and Potomac Edison must file the detailed data behind their Integrated Resource Plan (Case 25-0857-E-IRP), the long-range plan that includes the Fort Martin gas build.',
       county='Statewide', host='PSC, Case 25-0857-E-IRP', how='Filed by the utilities. Read it on the PSC docket.',
       project='fortmartin', sources=[['PSC order, Aug 28, 2026', PSC_DOC + '669562']]),
  dict(id='marl-reply', date='2026-12-04', type='psc',
       title='MARL reply briefs due (unconfirmed)',
       desc='Reply briefs in PSC Case 26-0075-E-CN.', county='Statewide', host='PSC, Case 26-0075-E-CN',
       flag='Date from Valley North Record. Not yet confirmed by a PSC order.',
       project='marl', sources=[VNR]),
  dict(id='interims-dec', date='2026-12-06', end='2026-12-08', type='legislature',
       title='Legislative interim meetings',
       desc='The last interim meetings before the 2027 session.', venue='Location to be announced', county='Statewide', host='WV Legislature',
       how='Open to the public. Agendas are posted about a week ahead.', project='hb2014', sources=[INTERIMS]),
  dict(id='frr-staff', date='2026-12-29', label='~Dec 29', approx=True, type='psc',
       title='PSC Staff recommendation on AEP\'s FRR status',
       desc='Staff\'s recommendation on whether Appalachian Power and Wheeling Power keep supplying their own capacity (Fixed Resource Requirement) instead of buying in PJM\'s data-center-driven capacity auction. Due 60 days after the Oct 30 utility responses.',
       county='Statewide', host='PSC, Case 25-0450-E-GI', project='hb2014',
       sources=[['PSC docket', PSC_CASE + '84852']]),
  dict(id='session-open', date='2027-01-13', start='12:00', endt='14:00', type='legislature',
       title='2027 Regular Session convenes',
       desc='First session of the 88th Legislature, running Jan 13 to Mar 13. Coalition groups, Democratic delegates, and the WV NAACP are pushing to restore local control under HB 2014.',
       venue='State Capitol', address=CAPITOL, county='Kanawha', host='WV Legislature',
       how='Floor sessions and committee meetings are open to the public. Bills can be tracked on wvlegislature.gov.',
       project='hb2014', sources=[['WV Legislature', 'https://home.wvlegislature.gov/']]),
  dict(id='affordable-rally', date='2027-01-26', start='10:00', endt='12:00', type='protest',
       title='WV Rally for Affordable Energy',
       desc='A rally on electricity costs, data-center expansion, energy infrastructure, and environmental concerns.',
       venue='South Steps, State Capitol', address=CAPITOL, county='Kanawha',
       host='WV Utility Impact Project, with the Valley North Opposition Alliance', how='Open to the public.',
       project='valleylink', sources=[VNR]),
  dict(id='fm-deadline', date='2027-02-28', label='By Feb 2027', approx=True, type='psc',
       title='Fort Martin decision deadline',
       desc='The statutory deadline for the PSC to rule on Mon Power\'s 1,200 MW gas plant plus 70 MW of solar (Case 26-0108-E-CN). Briefing closed Sep 14, 2026.',
       county='Statewide', host='PSC, Case 26-0108-E-CN', project='fortmartin',
       flag='The Feb 2027 deadline was reported by the Dominion Post, but we could not open the article to confirm it. Check the PSC docket.',
       sources=[['PSC docket', PSC_CASE + '85785']]),
  dict(id='marl-decision', date='2027-03-06', type='psc',
       title='MARL decision due',
       desc='The decision date for NextEra\'s 500 kV line (Case 26-0075-E-CN), set Mar 18 and reaffirmed when the PSC refused to pause the case on Sep 4.',
       county='Statewide', host='PSC, Case 26-0075-E-CN', project='marl', sources=[['PSC order, Sep 4, 2026', PSC_DOC + '669977']]),
  dict(id='session-end', date='2027-03-13', type='legislature', title='2027 Regular Session ends (Day 60)',
       county='Statewide', host='WV Legislature', project='hb2014', sources=[['MultiState session calendar', 'https://www.multistate.us/resources/2027-legislative-session-dates']]),
  dict(id='mp-rate2', date='2027-06-01', type='psc',
       title='Mon Power rate increase, step 2',
       desc='The second step of Mon Power and Potomac Edison\'s $75.6M base-rate increase (Case 26-0508-E-42T), about $4.11/month for an average residential customer.',
       county='Statewide', host='PSC, Case 26-0508-E-42T', project='fortmartin',
       sources=[['Legal notice', 'https://wvlegals.com/public-service-commission-of-west-virginia-charleston-case-no-26-0508-e-42t-monongahela-power-company-and-the-potomac-edison-company/']]),

  # ── Date TBD ──────────────────────────────────────────────
  dict(id='tbd-monarch', tbd=True, type='hearing', title='Monarch air permit R14-0042: DEP final decision',
       desc='DEP will publish a response-to-comments document and a final determination on the 2.16 GW, 864-engine gas microgrid.',
       county='Mason', host='WV DEP Division of Air Quality', project='monarch',
       sources=[['WSAZ', 'https://www.wsaz.com/2026/10/21/data-center-air-pollution-permit-under-public-review/'], ['Tracker: permit R14-0042', 'https://nearbydatacenters.org/wv/']]),
  dict(id='tbd-ridgeline', tbd=True, type='court', title='Ridgeline air-permit appeal refiled',
       desc='Tucker United, WVHC, and Sierra Club plan to refile in circuit court or the Supreme Court of Appeals after the ICA\'s jurisdictional dismissal.',
       county='Tucker', host='Appalachian Mountain Advocates (counsel)', project='ridgeline',
       sources=[['WVHC', 'https://www.wvhighlands.org/?p=15160']]),
  dict(id='tbd-barks', tbd=True, type='court', title='Barks v. Silicon Foundation: next hearing',
       desc='Twelve Warwood residents are challenging HB 2014\'s constitutionality. The Attorney General has intervened to defend the law.',
       venue='Ohio County Circuit Court', county='Ohio', project='warwood',
       sources=[['WV MetroNews', 'https://wvmetronews.com/2026/10/26/county-wants-more-specifics-on-local-control-of-high-impact-data-centers-but-ag-declines/']]),
  dict(id='tbd-vlapp', tbd=True, type='psc', title='Valley Link files its formal PSC application',
       desc='Expected late 2026 or early 2027, with a preferred route in early 2027. It will get a new E-CN case number. Until then, comments go to FP Valley Link 26A.',
       county='Statewide', host='Valley Link Transmission Co.', project='valleylink', sources=[VL_PSC]),
  dict(id='tbd-council', tbd=True, type='government', title='Data Center Advisory Council launches',
       desc='Promised in the Governor\'s Aug 11 plan to recommend setbacks, noise, and site standards. No roster or start date has been published.',
       county='Statewide', host='Commerce Dept. Data Economy Office', project='hb2014',
       sources=[['Gazette-Mail', 'https://www.wvgazettemail.com/news/energy_and_environment/the-same-story-morrisey-data-center-plan-doubles-down-on-industry-regulation-gaps/article_e22e72d4-4aa9-4696-8396-51e98d4f3e08.html']]),

  # ── Past ──────────────────────────────────────────────────
  dict(id='p-stopvl', date='2026-11-02', start='14:00', endt='18:00', type='protest',
       title='Stop Valley Link peaceful protest', desc='Info table at the gazebo.',
       venue='Barbour County Courthouse', address='26 N. Main St., Philippi, WV 26416', county='Barbour', host='Stop Valley Link',
       project='valleylink', sources=[VNR]),
  dict(id='p-marl-hearing', date='2026-10-26', end='2026-11-02', type='psc',
       title='MARL evidentiary hearing',
       desc='Six hearing days on NextEra\'s 500 kV line. NextEra settled with Lake O\' Woods Club on Oct 23.',
       venue='Howard M. Cunningham Hearing Room, PSC', address=PSC_HQ, county='Kanawha', virtual='Live-streamed', host='PSC, Case 26-0075-E-CN',
       project='marl', sources=[['PSC order, Sep 30', PSC_DOC + '671382']]),
  dict(id='p-monarch-deadline', date='2026-10-30', type='hearing', title='Monarch air permit comment deadline',
       county='Mason', host='WV DEP Division of Air Quality', project='monarch',
       sources=[['WSAZ', 'https://www.wsaz.com/2026/10/21/data-center-air-pollution-permit-under-public-review/']]),
  dict(id='p-monarch-virtual', date='2026-10-29', type='hearing', title='DEP virtual hearing: Monarch air permit R14-0042',
       county='Mason', virtual='Online (registration required)', host='WV DEP Division of Air Quality', project='monarch',
       sources=[['Gazette-Mail', 'https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html']]),
  dict(id='p-digigov', date='2026-10-29', type='government', title='WV Digital Government Summit',
       desc='State and local leaders on AI implementation, digital transformation, and cybersecurity.',
       venue='Charleston', county='Kanawha', host='GovTech', project='hb2014',
       sources=[['GovTech Events', 'https://events.govtech.com/West-Virginia-Digital-Government-Summit']]),
  dict(id='p-monarch-water', date='2026-10-26', start='17:00', endt='20:00', type='hearing',
       title='DEP water-permit workshop and hearing: Monarch',
       venue='Point Pleasant High School', address='280 Scenic Dr., Point Pleasant, WV 25550', county='Mason', host='WV DEP Water & Waste Management',
       project='monarch', sources=[['WCHS', 'https://wchstv.com/news/local/public-hearing-input-used-in-massive-data-center-state-waters-application-decision']]),
  dict(id='p-monroe', date='2026-10-26', label='Reported Oct 26', type='protest',
       title='Monroe County data center protest',
       desc='Residents rallied in Giles County, VA, outside the office of a landowner whose Monroe County land is rumored as a data center site.',
       venue='Giles County, VA', county='Monroe', project='monroe',
       sources=[['WVTF / Radio IQ', 'https://www.wvtf.org/news/2026-10-26/residents-gather-in-giles-to-protest-potential-monroe-county-data-center']]),
  dict(id='p-monarch-air', date='2026-10-20', type='hearing', title='DEP air-permit workshop: Monarch',
       desc='Seven people commented. Most raised health concerns or asked for more time.',
       venue='Point Pleasant High School', address='280 Scenic Dr., Point Pleasant, WV 25550', county='Mason', host='WV DEP Division of Air Quality',
       project='monarch', sources=[['Gazette-Mail', 'https://www.wvgazettemail.com/news/energy_and_environment/health-concerns-aired-during-meeting-on-mason-data-center-permit-request/article_58c63958-762f-4a29-a524-87d3b91ed179.html']]),
  dict(id='p-tu-townhall', date='2026-10-19', start='18:00', endt='20:00', type='community',
       title='Tucker United town hall on Ridgeline',
       venue='Davis Town Hall', address='505 William Ave., Davis, WV 26260', county='Tucker', host='Tucker United',
       project='ridgeline', sources=[['Tucker United events', 'https://www.tuckerunited.com/about-7']]),
  dict(id='p-capitol-protest', date='2026-09-14', type='protest', title='Data center protest at the State Capitol',
       desc='Residents from Tucker, Mason, and Putnam counties protested data center development.',
       venue='State Capitol', address=CAPITOL, county='Kanawha', project='hb2014',
       sources=[['Mountain State Spotlight', 'https://mountainstatespotlight.org/2026/10/28/data-center-opposition/']]),
  dict(id='p-wvdcap', date='2026-09-08', type='community', title='WV Data Center Accountability Project launches',
       desc='A statewide coalition: WV CAG, Tucker United, Putnam United, Mason WV United, Sierra Club WV, WVHC, and No Data Centers in the Eastern Panhandle.',
       venue='Charleston', county='Kanawha', host='WVDCAP', project='hb2014', sources=[['WV CAG release', 'https://wvcag.org/?p=16377']]),
  dict(id='p-marl-order', date='2026-09-04', type='psc', title='PSC refuses to pause or dismiss MARL',
       desc='The Commission denied Staff\'s motion and the NextEra–Staff schedule change, and ordered a study of the existing Gore–Hampshire right-of-way.',
       county='Statewide', host='PSC, Case 26-0075-E-CN', project='marl', sources=[['PSC order', PSC_DOC + '669977']]),
  dict(id='p-greenbrier', date='2026-09-03', type='government', title='Monarch and Tamarack certified at The Greenbrier',
       desc='Gov. Morrisey announced both Mason County certifications at the WV Chamber\'s Annual Meeting & Business Summit.',
       venue='The Greenbrier', address='White Sulphur Springs, WV', county='Greenbrier', host='WV Chamber of Commerce', project='monarch',
       sources=[['Herald-Dispatch', 'https://www.herald-dispatch.com/business/morrisey-hails-state-certifications-for-two-mason-county-data-center-projects/article_924875e0-77b4-45ab-9115-2ff4b193a6ae.html']]),
  dict(id='p-ica', date='2026-08-26', type='court', title='ICA dismisses Ridgeline air-permit appeals',
       desc='Dismissed on jurisdiction, not the merits.', county='Tucker', host='WV Intermediate Court of Appeals', project='ridgeline',
       sources=[['WTAP', 'https://www.wtap.com/2026/08/26/state-appeals-court-dismisses-environmental-groups-lawsuits-over-tucker-county-data-center-plant/']]),
  dict(id='p-putnam-res', date='2026-08-25', start='17:00', endt='19:00', type='community', title='Putnam United resolution at the County Commission',
       desc='Residents asked commissioners for a say in data center decisions.', venue='Putnam County Commission', address='Winfield, WV', county='Putnam', host='Putnam United',
       project='google', sources=[['Gazette-Mail', 'https://www.wvgazettemail.com/news/energy_and_environment/monarch-google-data-center-project-environmental-dangers-driving-resident-opposition/article_b35e6ed1-15af-4975-9772-54b89bb5a013.html']]),
  dict(id='p-naacp', date='2026-08-14', end='2026-08-15', type='community', title='WV NAACP convention calls for a moratorium',
       desc='Delegates unanimously demanded a pause of at least two years on high-impact data centers and microgrids.', venue='Huntington', county='Cabell', host='WV NAACP',
       project='hb2014', sources=[['Black By God', 'https://blackbygod.org/articles/news/wv-naacp-demands-moratorium-on-data-centers-microgrids-opposes-hb-2014/']]),
  dict(id='p-govplan', date='2026-08-11', type='government', title='Governor unveils the Responsible Data Center Development Plan',
       county='Statewide', host='Gov. Patrick Morrisey', project='hb2014',
       sources=[['WDTV', 'https://www.wdtv.com/2026/08/11/west-virginia-unveils-20-year-responsible-data-center-development-plan/']]),
  dict(id='p-fm-hearing', date='2026-07-15', start='17:30', type='psc', title='Fort Martin public comment hearing (virtual and in person)',
       desc='Public comment on Mon Power and Potomac Edison\'s certificate application for the roughly 1,200 MW gas plant.',
       venue='PSC headquarters', address=PSC_HQ, county='Kanawha', host='PSC, Case 26-0108-E-CN', project='fortmartin',
       sources=[['WDTV', 'https://www.wdtv.com/2026/05/15/public-hearing-set-monpowers-proposed-gas-plant-mon-county-solar-site-near-davis/']]),
  dict(id='p-psc-rule-hearing', date='2026-09-28', start='09:30', endt='12:00', type='psc', title='PSC public hearing on HB 2014 generating-capacity rules',
       desc='Public hearing in Case 26-0633-E-GI on the rules that became 150 CSR 41.',
       venue='PSC headquarters', address=PSC_HQ, county='Kanawha', host='PSC, Case 26-0633-E-GI', project='hb2014',
       sources=[['WDTV', 'https://www.wdtv.com/2026/08/20/state-psc-schedules-public-hearing-power-rules-behind-governor-morriseys-data-center-plan/'], ['WVPB', 'https://wvpublic.org/story/energy-environment/public-hearing-on-data-center-power-rules-scheduled/']]),
  dict(id='p-canaan', date='2026-06-14', end='2026-06-16', type='legislature', title='Interims at Canaan Valley, with Tucker United picnic and Davis panel',
       desc='Tucker United held a solidarity picnic and a roadside protest, Democrats held a press event at Davis Town Hall (Jun 15), and Mountain State Spotlight hosted a panel at Davis Fire Hall.',
       venue='Canaan Valley Resort', address='Davis, WV 26260', county='Tucker', host='WV Legislature', project='ridgeline',
       sources=[['WVHC update', 'https://www.wvhighlands.org/?p=15053'], ['Mountain State Spotlight', 'https://mountainstatespotlight.org/2026/06/16/tucker-county-panel-discussion/']]),
  dict(id='p-monarch-sw', date='2026-06-15', start='18:00', endt='20:00', type='hearing', title='DEP hearing: Monarch pipeline stormwater permit (WVR312628)',
       venue='Mason County Courthouse', address='200 Sixth St., Point Pleasant, WV 25550', county='Mason', host='WV DEP Water & Waste Management', project='monarch',
       sources=[['Gazette-Mail', 'https://www.wvgazettemail.com/news/energy_and_environment/new-permits-eyed-for-mason-co-data-center-tied-project-after-eight-figure-wv-support/article_6a2e5e86-a19e-442d-831c-24f1760bbf80.html']]),
  dict(id='p-warwood', date='2026-06-01', label='Jun 2026', approx=True, type='community', title='Warwood town hall with Del. Shawn Fluharty',
       venue='Warwood Veterans Association', address='Wheeling, WV', county='Ohio', project='warwood',
       sources=[['WTOV9', 'https://wtov9.com/news/local/warwood-residents-state-delegate-raise-concerns-over-proposed-data-center-at-town-hall-warwood-data-center-local-control-house-bill-2014-shawn-fluharty-health-concerns-environmental-impact-wheeling']]),
]

# Standing public meetings: rule as published. next = only dates seen posted.
STANDING = [
  dict(body='Berkeley County Commission', county='Berkeley', rule='Weekly on Thursdays (the time is on each agenda)', where='Commission Chambers, 400 W. Stephen St., Suite 205, Martinsburg', next='Nov 5', projects=['penzance', 'qts'], url='https://www.berkeleywv.org/agendacenter'),
  dict(body='Grant County Commission', county='Grant', rule='2nd and 4th Tuesdays (inferred from posted agenda dates)', where='5 Highland Ave., Petersburg', projects=['ridgeline'], verify='The county does not publish a schedule; this pattern is inferred from its posted agendas.', url='https://www.grantcountywv.org/agencies/agendas/CommissionAgendas.php', note='Ridgeline could expand into Grant County.'),
  dict(body='Hampshire County Commission', county='Hampshire', rule='Set at the first meeting of each year. Agendas are posted 3 business days ahead.', where='Romney', projects=['marl', 'valleylink'], url='http://hampshirewv.com/CommAgenda.html'),
  dict(body='Jefferson County Commission', county='Jefferson', rule='1st Thursday 9:30 a.m. and 3rd Thursday 6:00 p.m. (5th Thursday 9:30 a.m.)', where='Charles Town', next='Nov 5 (9:30 a.m.)', projects=['qts', 'summit'], url='https://www.jeffersoncountywv.org/county-government/elected-officials/county-commission/meeting-session-information'),
  dict(body='Marion County Commission', county='Marion', rule='2nd and 4th Wednesdays, 10:00 a.m.', where='J. Harper Meredith Building, 4th floor, Fairmont', projects=['hoglick'], url='https://www.marioncountywv.com/departments/county_commission/index.php'),
  dict(body='Mason County Commission', county='Mason', rule='Thursdays, 4:00 p.m. (dates on the county calendar)', where='Mason County Courthouse, 200 Sixth St., Point Pleasant', projects=['monarch', 'tamarack'], url='https://masoncountywv.gov/calendar/'),
  dict(body='Mineral County Commission', county='Mineral', rule='Usually the 2nd Tuesday at 8:30 a.m. and the 4th Tuesday at 4:30 p.m. (inferred from posted agendas)', where='Administrative Annex, 68 Armstrong St., Keyser. Zoom offered.', projects=['marl'], verify='The county does not publish a schedule; this pattern is inferred from its posted agendas.', url='https://www.mineralwv.gov/agendas-minutes/'),
  dict(body='Mingo County Commission', county='Mingo', rule='Tuesdays, 4:30 p.m. (from a past notice; confirm locally)', where='Room 308-B, 78 E. 2nd Ave., Williamson', projects=['adams-tg', 'adams-h'], url='https://mingocountywv.com/', verify='The county website is under construction, and we could not confirm a current schedule. Call the county clerk before attending.'),
  dict(body='Monongalia County Commission', county='Monongalia', rule='Every Wednesday, 10:00 a.m.', where='County Courthouse, 2nd floor, 243 High St., Morgantown', projects=['fortmartin', 'marl'], url='https://www.monongaliacounty.gov/commission/meeting_schedule/index.php'),
  dict(body='Monroe County Commission', county='Monroe', rule='1st Wednesday, 9:00 a.m.', where='Monroe County Courthouse, Union', next='Nov 4', projects=['monroe'], url='https://www.monroecountywv.gov/commission/meeting-datespress-releasesminutes/60'),
  dict(body='Ohio County Commission', county='Ohio', rule='Tuesdays, 8:00 a.m. (check the county calendar)', where='Room 215, City-County Building, 1500 Chapline St., Wheeling', projects=['warwood'], url='https://www.ohiocountywv.gov/calendar'),
  dict(body='Wheeling City Council', county='Ohio', rule='1st and 3rd Tuesdays, 5:30 p.m.', where='Council Chambers, City-County Building, Wheeling', next='Nov 4 (moved for the election) and Nov 17', projects=['warwood'], url='https://www.wheelingwv.gov/departments/citycouncil/councilmeetings', note='The Warwood project is described as under 90 MW, so the city, not HB 2014, has oversight.'),
  dict(body='Preston County Commission', county='Preston', rule='Tuesdays 9:30 a.m.; the last Tuesday of the month at 6:00 p.m.', where='Suite 202, Kingwood', projects=['marl'], url='https://www.prestoncountywv.gov/197/County-Commission'),
  dict(body='Putnam County Commission', county='Putnam', rule='2nd Tuesday 9:00 a.m. and last Tuesday 5:00 p.m.', where='Putnam County Justice Building, Winfield', projects=['google'], url='https://putnamcountywv.gov/commission/'),
  dict(body='Putnam County Development Authority', county='Putnam', rule='3rd Tuesday, 4:30 p.m.', where='Putnam County', projects=['google'], url='https://pcda.org/meetings/', note='It helped direct Google\'s first round of community investments.'),
  dict(body='Tucker County Commission', county='Tucker', rule='2nd Wednesday 9:00 a.m. and 4th Wednesday 4:00 p.m.', where='Courthouse courtroom, 215 1st St., Parsons', projects=['ridgeline'], url='https://tuckercountycommission.com/county-commission'),
  dict(body='Tucker County Development Authority', county='Tucker', rule='3rd Thursday, 6:00 p.m.', where='National Youth Science Foundation Building, 494 Riverstone Rd., Davis', projects=['ridgeline'], url='https://tuckerwv.com/about-us/meeting-information/'),
]

def main(md_path, js_path):
    # ── JS block
    js = ('// ═══════════════════════════════════════════\n'
          '// CALENDAR DATA (source: research/calendar_data.py, which also writes research/2026-11-calendar.md)\n'
          '// Times are US Eastern. approx/tbd items are excluded from .ics downloads.\n'
          '// ═══════════════════════════════════════════\n'
          'const EVENTS = ' + json.dumps(EVENTS, ensure_ascii=False, indent=1) + ';\n\n'
          'const STANDING = ' + json.dumps(STANDING, ensure_ascii=False, indent=1) + ';\n')
    pathlib.Path(js_path).write_text(js)
    # ── Markdown receipts
    def when(e):
        if e.get('tbd'): return 'TBD'
        if e.get('label'): return e['label']
        d = e['date'] + (f" → {e['end']}" if e.get('end') else '')
        t = f" {e['start']}–{e.get('endt','')}" if e.get('start') else ''
        return d + t
    rows = lambda evs: '\n'.join(
        f"| {when(e)} | {e['type']} | {e['title']}{' ⚠ ' + e['flag'] if e.get('flag') else ''} | "
        f"{', '.join(x for x in [e.get('venue'), e.get('address'), e.get('virtual')] if x) or '-'} | {e.get('county','')} | "
        f"{' · '.join(f'[{l}]({u})' for l, u in e.get('sources', []))} |" for e in evs)
    up = [e for e in EVENTS if not e.get('tbd') and e['date'] >= '2026-11-03']
    tbd = [e for e in EVENTS if e.get('tbd')]
    past = [e for e in EVENTS if not e.get('tbd') and e['date'] < '2026-11-03']
    head = '| When (ET) | Type | Event | Where | County | Sources |\n|---|---|---|---|---|---|\n'
    md = f"""# WV AI Watch Calendar: data and receipts (as of Nov 3, 2026)

This file is generated from the same data that powers the site's Calendar section. Times are US Eastern. "Unconfirmed" items carry a ⚠ note. Items with an approximate date are shown on the site but left out of `.ics` downloads.

**Scope decisions (Nov 3, 2026, per curator):** Bitcoin and freedom-tech meetups are dropped. The Jobs, Education, and Grants panels are removed. Standing meetings cover every county with a mapped project plus the three MARL-only counties (Preston, Mineral, Hampshire). The 14–20 Valley Link corridor counties are not yet included.

**Method.**
- Valley Link schedule: scraped from vltransmission.com.
- Legislature: session dates from wvlegislature.gov and MultiState; interim dates and the Nov 10 Rule-Making Review agenda from the Legislature's interim pages.
- County schedules: county websites, with dates inferred from posted agendas where marked.
- Community events: the Tucker United events page.
- PSC and DEP dates: from the dossier (§3, §4b) and the PSC docket digests.
- Excluded: the Tucker County commissioners' misdemeanor case (Nov 10 pre-trial), which is unrelated to data centers.

## Upcoming ({len(up)})
{head}{rows(up)}

## Date TBD ({len(tbd)})
{head}{rows(tbd)}

## Past ({len(past)})
{head}{rows(past)}

## Standing public meetings ({len(STANDING)})
| Body | County | Schedule (as published) | Where | Next posted | Related | Source |
|---|---|---|---|---|---|---|
""" + '\n'.join(f"| {s['body']} | {s['county']} | {s['rule']} | {s['where']} | {s.get('next','-')} | {', '.join(s['projects'])}{(' · ' + s['note']) if s.get('note') else ''}{(' · ⚠ ' + s['verify']) if s.get('verify') else ''} | [link]({s['url']}) |" for s in STANDING) + """

## Open items
- Hampshire County Commission's 2026 meeting calendar was not found online.
- Mingo County Commission's schedule comes from an older public notice.
- Grant and Mineral schedules are inferred from posted agenda dates.
- The Dec 6–8 interim location has not been announced.
- MARL brief dates (Nov 23 and Dec 4) are not confirmed by a PSC order.
"""
    pathlib.Path(md_path).write_text(md)
    print(f"events={len(EVENTS)} upcoming={len(up)} tbd={len(tbd)} past={len(past)} standing={len(STANDING)}")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
