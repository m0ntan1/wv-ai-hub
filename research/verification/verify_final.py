"""Final verification pass: every item on the page vs. its linked sources.
Status: ok (all key facts found in source text) | psc (PSC docket notices; site blocks bots) | verify (shown with ⚠ Verify on site) | gap (needs attention)
Method: page (direct fetch) | extract (Firecrawl extract) | psc-notice
"""
import json, re, sys, pathlib, hashlib
sp = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(sp/'tools'))
from verify_spec import S as OLD
old_inv = json.loads((sp/'inventory_v1.json').read_text())
inv = json.loads((sp/'inventory.json').read_text())

def key(x):  # stable key: section + title (people: first 30 chars of title)
    t = x['title']
    return x['sec'] + '|' + (t[:30] if x['sec'] == 'people' else t)
OLDBY = {key(x): OLD.get(i, dict(facts=[])) for i, x in enumerate(old_inv)}

NEW = {  # facts for retitled / rewritten items
 'hub:Morgantown|Anurag Srivastava leads WVU cyber-power research.': ['power chair professor', '66m', 'darpa'],
 'hub:Charleston|Morrisey closes 2026 session: 12 vetoes, 10 bills unsigned.': ['12 vetoes', '4983'],
 "hub:Huntington|Marshall University's AI governance.": ['presidential task force', '2023', 'steering committee', '6,000+'],
 "hub:Huntington|Marshall's first gBETA cohort.": ['farmerztool', 'get2there', 'monarch learning labs', 'stitch ai', 'huntington national'],
 'hub:Huntington|Generation WV AI workforce panel.': ['ai is the priority', 'must-have', 'alpha innovations'],
 'hub:Berkeley County|$4 billion Penzance data center announced.': ['548', '1.9 million', '600 megawatts', 'no state funding', 'falling waters'],
 'hub:Berkeley County|Microgrid revenue reinvestment.': ['50 percent', '30 percent to the host county', '10 percent', 'electric grid stabilization', 'economic enhancement grant'],
 'hub:Berkeley County|Nscale takes over Monarch; Anthropic signs on.': ['nscale', '44.6', '460', ['american intelligence', 'aipcorp'], '2.16'],
 'hub:Parkersburg|WVU-P Innovation and Technology Center opens.': ['nearly $35 million', '159', 'cyber'],
 'hub:Weirton|Weirton plant targets 500 MW a year by 2028.': ['500 megawatts by 2028'],
 'hub:Princeton|State guidance brings AI into classrooms.': ['mercer county schools', 'guidance'],
 'hub:Princeton|Mercer County trains teachers on AI.': ['mercer county', 'ai'],
 'hub:Clarksburg|TekSynap acquires JBA, strengthening FBI tech support.': ['jba', 'clarksburg', 'cjis'],
 'hub:Clarksburg|FBI CJIS Division in Clarksburg.': ['986-acre', '3,500', 'biometric technology center'],
 'hub:Tucker County|Harvard study projects $19M to $35M in health damages.': ['dominici', '35', '19'],
 'hub:Tucker County|Groups appeal for blacked-out Ridgeline permit data.': ['blacked out', 'emissions data'],
 'project|Hog Lick Data Center & Microgrid': ['277', '350 acres', '1gw', 'geothermal', 'redmond'],
 'project|Adams Fork Energy Campus · Harless': ['harless', 'without prejudice'],
 'project|Penzance Bedington Campus': ['548', '1.9 million', '600 megawatts', '1,000', '125', 'bedington owner', 'gochenour', 'mccuskey', 'rupok bhuiyan'],
 'event|Fort Martin public comment hearing (virtual and in person)': ['july 15', '5:30'],
 'event|PSC public hearing on HB 2014 generating-capacity rules': ['september 28', '9:30', '26-0633'],
 'event|WV NAACP convention calls for a moratorium': ['moratorium', 'huntington', 'august 14'],
 'standing|Berkeley County Commission': ['november 5, 2026'],
 'standing|Monroe County Commission': ['first wednesday', '9:00'],
 'standing|Wheeling City Council': ['first and third tuesday', '5:30'],
 'standing|Putnam County Commission': ['second tuesday', '9:00', 'last tuesday', 'justice building'],
 'standing|Tucker County Development Authority': ['third thursday', '494 riverstone'],
 'hub:Weirton|Form Energy lands $1B Google deal.': ['google', ['$1 billion','$1b','1 billion'], '30 gigawatt', ['100-hour','100 hours'], 'minnesota'],
 'project|Project Tamarack': ['balestrieri', ['$12 billion','12 billion'], '2.16', 'project washington', 'total shocker', 'not going up', 'quarter of a mile', '300'],
 'event|Data center protest at the State Capitol': [['sept.14','sept. 14']],
 'people|Chris Morris Director, Commerc': ['christopher morris', 'data economy office'],
 'docket|Possible county challenge to HB 2014': ['skidmore', 'monongalia', 'sikora'],
 'docket|HB 2014 generating-capacity rules: 69% coal capacity factor becomes "a goal, not a mandate"': ['26-0633', 'aspirational', 'joint proposed amendments', 'rule-making review'],
 'people|Rep. Riley Moore · Ace Parsi WV-': ['riley moore', 'parsi', 'ratepayer protection act', 'neighbors, not servers'],
 'people|Eddie Gochenour Berkeley County': ['gochenour', 'very optimistic'],
 'people|Cara Keys Jefferson County Comm': ['cara keys'],
 'people|Sean Sikora Monongalia County C': ['sikora'],
 'people|WV NAACP President Loretta Youn': ['loretta young'],
}
# Items shown with ⚠ Verify on the site (honest flags)
VERIFY = {
 'project|Summit Point Site': 'Single secondary source (tracker); no filing or news confirmation found.',
 'event|Fort Martin decision deadline': 'Feb 2027 deadline reported by Dominion Post; article not retrievable.',
 'event|MARL initial briefs due (unconfirmed)': 'Date from Valley North Record; no PSC briefing order seen.',
 'event|MARL reply briefs due (unconfirmed)': 'Date from Valley North Record; no PSC briefing order seen.',
 'docket|Fort Martin 1,200 MW gas plant + 70 MW solar ($2.48B)': 'Briefs verified via PSC notices; the Feb 2027 deadline is flagged ⚠ Verify.',
 'standing|Mingo County Commission': 'County website under construction; schedule from an old notice.',
 'standing|Grant County Commission': 'Schedule inferred from posted agenda dates.',
 'standing|Mineral County Commission': 'Schedule inferred from posted agenda dates.',
}
log = {}
for line in (sp/'fetchlog.txt').read_text().splitlines():
    c, h, u = line.split(' ', 2); log[u] = (c, h)
norm = lambda t: re.sub(r'\s+', ' ', t.lower().replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"').replace('–', '-').replace('—', '-').replace('\xa0', ' '))
def text(u):
    h = hashlib.sha1(u.encode()).hexdigest()[:12]
    ex = sp/'extracts'/f'{h}.txt'
    parts, method = [], []
    if ex.exists(): parts.append(ex.read_text()); method.append('extract')
    c, hh = log.get(u, ('?', None))
    f = sp/'pages'/f'{hh}.txt'
    if c == '200' and hh and f.exists(): parts.append(f.read_text()); method.append('page')
    return (norm(' '.join(parts)) if parts else None), method

rows = []
for x in inv:
    k = key(x)
    facts = NEW.get(k) or OLDBY.get(k, {}).get('facts')
    psc = OLDBY.get(k, {}).get('psc', False) or (x['sec'] == 'event' and x['title'] in ('Mon Power IRP data due', "PSC Staff recommendation on AEP's FRR status", 'MARL decision due', 'MARL evidentiary hearing', 'PSC refuses to pause or dismiss MARL'))
    texts = [text(u) for u in x['urls']]
    methods = sorted({m for _, ms in texts for m in ms})
    missing = []
    if facts is None:
        status = 'gap'; missing = ['NO SPEC']
    else:
        for f in facts:
            alts = f if isinstance(f, list) else [f]
            if not any(t and norm(a) in t for t, _ in texts for a in alts): missing.append(alts[0])
        status = 'ok' if not missing else 'gap'
    if psc: status, methods = 'psc', ['psc-notice'] + methods
    if k in VERIFY: status = 'verify'
    rows.append(dict(sec=x['sec'], title=x['title'][:90], status=status, missing=missing, method=methods, urls=x['urls'], note=VERIFY.get(k, '')))
(sp/'verify_final.json').write_text(json.dumps(rows, indent=1))
from collections import Counter
print(Counter(r['status'] for r in rows))
for r in rows:
    if r['status'] == 'gap': print('GAP', r['sec'], '|', r['title'][:70], '| missing', r['missing'])
