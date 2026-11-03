"""Check data/*.json before publishing. Run after every edit:

    python3 -I tools/check.py              # structure, references, dates, staleness
    python3 -I tools/check.py --links      # also fetch every source URL (slow; a few minutes)
    python3 -I tools/check.py --today 2026-11-10   # pretend it's another day

ERRORS (exit 1) break the site or the rules: missing fields, bad dates, broken
references, a claim without a source.
WARNINGS (exit 0) are a to-do list for the next update shift: past "next" dates,
stale checks, markers outside their county, ⚠ Verify items still open.
"""
import argparse, datetime, json, re, sys, pathlib, urllib.request, concurrent.futures

ROOT = pathlib.Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--links', action='store_true', help='fetch every source URL and report failures')
ap.add_argument('--today', default=datetime.date.today().isoformat())
ap.add_argument('--stale-days', type=int, default=45, help='warn when a record was last checked longer ago than this')
a = ap.parse_args()
TODAY = a.today
errors, warnings = [], []
err = lambda m: errors.append(m)
warn = lambda m: warnings.append(m)

def load(n):
    try:
        return json.loads((ROOT / 'data' / f'{n}.json').read_text())
    except Exception as e:
        err(f'data/{n}.json: cannot parse ({e})'); return None
P, LINES, DK, EV, ST, PPL, NET, HUBS, DESK, META, GEO = (load(n) for n in ['projects', 'lines', 'docket', 'events', 'standing', 'people', 'network', 'hubs', 'desk', 'meta', 'geo'])
if errors:
    print('\n'.join('ERROR ' + e for e in errors)); sys.exit(1)

DATE = re.compile(r'^\d{4}(-\d{2}(-\d{2})?)?$')
TIME = re.compile(r'^\d{2}:\d{2}$')
STATUSES = {'construction', 'certified', 'contested', 'proposed', 'rumored', 'grid'}
STAGES = {'prefiling', 'open', 'briefing', 'awaiting', 'closed'}
EVTYPES = {'hearing', 'psc', 'court', 'legislature', 'protest', 'community', 'government', 'developer'}
COUNTIES = {c['name'] for c in GEO['counties']}
PIDS = {p['id'] for p in P}
EXTRA = {'marl', 'valleylink', 'hb2014'}
def is_date(s, where):
    if s in ('', None): return True
    if not isinstance(s, str) or not DATE.match(s): err(f'{where}: bad date {s!r} (use YYYY, YYYY-MM or YYYY-MM-DD)'); return False
    try: datetime.date.fromisoformat((s + '-01-01')[:10] if len(s) < 10 else s)
    except ValueError: err(f'{where}: impossible date {s!r}'); return False
    return True
def as_day(s): return (s + '-01-01')[:10] if s and len(s) == 4 else (s + '-01')[:10] if s and len(s) == 7 else s
def sources_ok(lst, where, required=True):
    if not lst:
        (err if required else warn)(f'{where}: no sources'); return
    for s in lst:
        if not isinstance(s, dict) or not s.get('url', '').startswith(('https://', 'http://')) or not s.get('label'):
            err(f'{where}: bad source {s!r}')
def stale(rec, where):
    c = rec.get('checked')
    if c and (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(c)).days > a.stale_days:
        warn(f'{where}: last checked {c}, more than {a.stale_days} days ago')
def ids_unique(lst, name):
    seen = set()
    for x in lst:
        if x['id'] in seen: err(f'{name}: duplicate id {x["id"]!r}')
        seen.add(x['id'])

# ---------------------------------------------------------------- polygon test for markers
def inside(x, y, ring):
    c = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def county_of(lng, lat):
    return [c['name'] for c in GEO['counties'] if any(inside(lng, lat, r) for r in c['rings'])]

# ---------------------------------------------------------------- projects
ids_unique(P, 'projects')
for p in P:
    w = f"projects/{p.get('id')}"
    for k in ['id', 'short', 'name', 'status', 'place', 'counties', 'lat', 'lng', 'developer', 'facts', 'latest', 'history', 'timeline', 'sources', 'checked']:
        if k not in p: err(f'{w}: missing {k}')
    if p.get('status') not in STATUSES: err(f'{w}: unknown status {p.get("status")!r}')
    for c in p.get('counties', []):
        if c not in COUNTIES: err(f'{w}: unknown county {c!r}')
    hit = county_of(p['lng'], p['lat'])
    if not hit: err(f'{w}: marker {p["lat"]},{p["lng"]} is outside West Virginia')
    elif not set(hit) & set(p['counties']): warn(f'{w}: marker falls in {hit[0]} County but counties = {p["counties"]}')
    sources_ok(p.get('sources'), w)
    stale(p, w)
    if not p.get('history'): err(f'{w}: empty history (the map needs at least one dated status)')
    for h in p.get('history', []):
        is_date(h.get('d'), w + '/history')
        if h.get('status') not in STATUSES: err(f'{w}/history: unknown status {h.get("status")!r}')
    if p.get('history') and p['history'][-1]['status'] != p['status']:
        warn(f'{w}: current status {p["status"]!r} differs from the last history entry {p["history"][-1]["status"]!r}')
    for t in p.get('timeline', []):
        is_date(t.get('d'), w + '/timeline')
        if t.get('next') and t.get('d') and len(t['d']) == 10 and t['d'] < TODAY:
            warn(f'{w}: timeline "next" item dated {t["d"]} is in the past: {t["t"][:60]}')
        if not t.get('next') and not t.get('src'):
            warn(f'{w}: timeline item without its own source (falls back to the project sources): {t["t"][:60]}')
    for f in p.get('facts', []):
        if not f.get('k') or not f.get('v'): err(f'{w}: bad fact {f!r}')
    if p.get('verify'): warn(f'{w}: ⚠ Verify still open: {p["verify"][:80]}')

for l in LINES:
    w = f"lines/{l.get('id')}"
    is_date(l.get('appears'), w); sources_ok(l.get('sources'), w)
    for c in l.get('counties', []):
        if c not in COUNTIES: err(f'{w}: unknown county {c!r}')

# ---------------------------------------------------------------- docket
ids_unique(DK, 'docket')
for k in DK:
    w = f"docket/{k.get('id')}"
    for f in ['id', 'body', 'title', 'stage', 'stamp', 'summary', 'projects', 'sources', 'checked']:
        if f not in k: err(f'{w}: missing {f}')
    if k.get('stage') not in STAGES: err(f'{w}: unknown stage {k.get("stage")!r}')
    if k.get('body') not in {'courts', 'psc', 'dep', 'legislature'}: err(f'{w}: unknown body {k.get("body")!r}')
    for pid in k.get('projects', []):
        if pid not in PIDS | EXTRA: err(f'{w}: unknown project {pid!r}')
    sources_ok(k.get('sources'), w); stale(k, w)
    n = k.get('next')
    if n and n.get('d'):
        is_date(n['d'], w + '/next')
        if as_day(n['d']) < TODAY and len(n['d']) == 10:
            warn(f'{w}: next date {n["d"]} ({n["t"]}) has passed. Update the stage, stamp, and next step.')
    if k.get('verify'): warn(f'{w}: ⚠ Verify still open: {k["verify"][:80]}')

# ---------------------------------------------------------------- events + standing
ids_unique(EV, 'events')
for e in EV:
    w = f"events/{e.get('id')}"
    for f in ['id', 'type', 'title']:
        if not e.get(f): err(f'{w}: missing {f}')
    if e.get('type') not in EVTYPES: err(f'{w}: unknown type {e.get("type")!r}')
    if not e.get('tbd'):
        if not e.get('date'): err(f'{w}: no date and not marked tbd')
        is_date(e.get('date'), w); is_date(e.get('end'), w)
    for t in ('start', 'endt'):
        if e.get(t) and not TIME.match(e[t]): err(f'{w}: bad {t} {e[t]!r} (use HH:MM, 24-hour, Eastern)')
    if e.get('county') and e['county'] != 'Statewide' and e['county'] not in COUNTIES: err(f'{w}: unknown county {e["county"]!r}')
    if e.get('project') and e['project'] not in PIDS | EXTRA: err(f'{w}: unknown project {e["project"]!r}')
    sources_ok(e.get('sources'), w, required=False)
    if e.get('flag'): warn(f'{w}: ⚠ Verify still open: {e["flag"][:80]}')
    if e.get('tbd') and e.get('date') and e['date'] < TODAY: warn(f'{w}: marked TBD but has a past date')
for s in ST:
    w = f"standing/{s.get('body')}"
    if s.get('county') not in COUNTIES: err(f'{w}: unknown county {s.get("county")!r}')
    for pid in s.get('projects', []):
        if pid not in PIDS | EXTRA: err(f'{w}: unknown project {pid!r}')
    if not s.get('url', '').startswith('http'): err(f'{w}: missing agenda URL')
    if s.get('verify'): warn(f'{w}: ⚠ Verify still open: {s["verify"][:80]}')
    if s.get('next'): warn(f'{w}: "next posted: {s["next"]}" is a one-off date; confirm or clear it each shift')

# ---------------------------------------------------------------- people + network + hubs + desk
for x in PPL:
    for pid in x.get('projects', []):
        if pid not in PIDS | EXTRA: err(f"people/{x['name']}: unknown project {pid!r}")
    sources_ok(x.get('sources'), f"people/{x['name']}")
nids = {n['id'] for n in NET['nodes']}
if len(nids) != len(NET['nodes']): err('network: duplicate node ids')
for n in NET['nodes']:
    if n.get('project') and n['project'] not in PIDS: err(f"network/{n['id']}: unknown project {n['project']!r}")
for e in NET['edges']:
    w = f"network/{e.get('a')}->{e.get('b')}"
    if e.get('a') not in nids or e.get('b') not in nids: err(f'{w}: unknown node')
    if not e.get('src', '').startswith('http'): err(f'{w}: every connection needs a source URL')
    if not e.get('label'): err(f'{w}: missing label')
deg = {n: 0 for n in nids}
for e in NET['edges']: deg[e['a']] += 1; deg[e['b']] += 1
for n, d in deg.items():
    if d == 0: warn(f'network/{n}: node has no connections')
for h in HUBS:
    for s in h['stories']: sources_ok(s.get('sources'), f"hubs/{h['id']}/{s['title'][:40]}")
for x in DESK:
    is_date(x.get('d'), 'desk')
    if not x.get('src', '').startswith('http'): err(f"desk/{x.get('d')}: missing source")
    if x.get('project') and x['project'] not in PIDS | EXTRA: err(f"desk/{x.get('d')}: unknown project {x['project']!r}")
if META.get('updated', '') < max(x['d'] for x in DESK): warn('meta.updated is older than the newest desk item; bump meta.updated')

# ---------------------------------------------------------------- news (optional; built by tools/fetch_news.py)
news_path = ROOT / 'data' / 'news.json'
if news_path.exists():
    try:
        NEWS = json.loads(news_path.read_text())
        for i in NEWS.get('items', []):
            w = f"news/{i.get('id')}"
            if not i.get('title') or not str(i.get('url', '')).startswith(('https://', 'http://')) or not i.get('source'): err(f'{w}: needs title, url, and source')
            if not re.match(r'^\d{4}-\d{2}-\d{2}T', str(i.get('d', ''))): err(f'{w}: bad timestamp {i.get("d")!r}')
            for pid in i.get('projects', []):
                if pid not in PIDS | EXTRA: err(f'{w}: unknown project tag {pid!r}')
        upd = NEWS.get('updated', '')[:10]
        if upd and upd <= TODAY and (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(upd)).days > 7:
            warn(f'news: last gathered {upd}. Run python3 -I tools/fetch_news.py to refresh the headlines.')
    except Exception as ex:
        err(f'data/news.json: cannot parse ({ex})')

# ---------------------------------------------------------------- optional link check
if a.links:
    urls = set()
    for lst in [*(p['sources'] for p in P), *(k['sources'] for k in DK), *(e.get('sources', []) for e in EV), *(x['sources'] for x in PPL), *(l['sources'] for l in LINES)]:
        urls.update(s['url'] for s in lst)
    urls.update(e['src'] for e in NET['edges']); urls.update(x['src'] for x in DESK); urls.update(s['url'] for s in ST)
    for h in HUBS:
        for s in h['stories']: urls.update(x['url'] for x in s['sources'])
    def fetch(u):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (WV AI Watch link check)'}, method='GET')
            with urllib.request.urlopen(req, timeout=20) as r: return u, r.status
        except Exception as ex: return u, getattr(ex, 'code', None) or type(ex).__name__
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        for u, code in pool.map(fetch, sorted(urls)):
            if code != 200:
                (warn if 'psc.state.wv.us' in u or code in (401, 403, 429) else err)(f'link {code}: {u}')
    print(f'checked {len(urls)} links')

for w in warnings: print('WARN ', w)
for e in errors: print('ERROR', e)
print(f'\n{len(errors)} errors, {len(warnings)} warnings · {len(P)} projects, {len(DK)} docket items, {len(EV)} events, {len(ST)} standing meetings, {len(NET["edges"])} connections · as of {TODAY}')
sys.exit(1 if errors else 0)
