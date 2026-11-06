"""Gather news headlines about West Virginia's data center and AI power projects.

Reads the feeds and searches in data/news-sources.json, keeps items whose
title or summary matches the beat, tags each with the projects it mentions,
and merges them into data/news.json (newest first, kept for 180 days).
Standard library only. Runs every few hours in .github/workflows/news.yml.

Usage:
    python3 -I tools/fetch_news.py            # fetch and update data/news.json
    python3 -I tools/fetch_news.py --dry-run  # print what would be added

The headlines are the outlets' own words. They are not checked like the rest
of the site; the page says so. Anything worth keeping goes through the normal
update shift (desk log, timeline) with verification.
"""
import argparse, datetime as dt, email.utils, html, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'data' / 'news-sources.json').read_text())
OUT = ROOT / 'data' / 'news.json'
KEEP_DAYS, MAX_ITEMS = 180, 400
UA = 'Mozilla/5.0 (compatible; WVAIWatchNews/1.0; +https://wvaihub.com/#/news)'

ap = argparse.ArgumentParser()
ap.add_argument('--dry-run', action='store_true')
args = ap.parse_args()
now = dt.datetime.now(dt.timezone.utc)

def fetch(url, tries=2):
    """Polite fetch: a pause before every request, and one slow retry if the site says 429."""
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'})
    for n in range(tries):
        time.sleep(2)
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and n + 1 < tries: time.sleep(20); continue
            raise

def text(s):
    s = re.sub(r'<[^>]+>', ' ', html.unescape(s or ''))
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def parse_date(s):
    if not s: return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try: d = dt.datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
        except ValueError: return None
    if d.tzinfo is None: d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)

def clean_url(u):
    """Unwrap Bing redirect links and drop tracking parameters, so links go straight to the publisher."""
    p = urllib.parse.urlparse(u)
    if 'bing.com' in p.netloc and 'apiclick' in p.path:
        q = urllib.parse.parse_qs(p.query).get('url')
        if q: u = q[0]; p = urllib.parse.urlparse(u)
    qs = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith(('utm_', 'fbclid', 'gclid', 'mc_', 'ref'))]
    if p.scheme.lower() not in ('http', 'https') or not p.netloc: return ''  # feeds are untrusted: never keep javascript:, data:, or relative links
    scheme = 'https'
    return urllib.parse.urlunparse((scheme, p.netloc.lower(), p.path, '', urllib.parse.urlencode(qs), ''))

def items_of(xml_bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for it in root.iter():
        tag = it.tag.split('}')[-1]
        if tag not in ('item', 'entry'): continue
        get = lambda name: next((c for c in it if c.tag.split('}')[-1] == name), None)
        link = get('link')
        href = (link.get('href') if link is not None and link.get('href') else (link.text if link is not None else '')) or ''
        src = get('Source') if get('Source') is not None else get('source')  # Bing: News:Source; Google News: source
        out.append({
            'title': text(get('title').text if get('title') is not None else ''),
            'url': href.strip(),
            'summary': text((get('description') if get('description') is not None else get('summary') if get('summary') is not None else get('content')).text if (get('description') is not None or get('summary') is not None or get('content') is not None) else ''),
            'date': parse_date((get('pubDate') if get('pubDate') is not None else get('published') if get('published') is not None else get('updated')).text if (get('pubDate') is not None or get('published') is not None or get('updated') is not None) else None),
            'outlet': text(src.text) if src is not None else None,
        })
    return out

low = lambda s: ' ' + s.lower() + ' '
MATCH = [m.lower() for m in CFG['match']]
ENERGY = [m.lower() for m in CFG.get('energyMatch', [])]  # the coal, gas, utility and grid side; those items are tagged "energy"
COUNTY_NAMES = [c['name'].lower() + ' county' for c in json.loads((ROOT / 'data' / 'geo.json').read_text())['counties']]
WV = [w.lower() for w in CFG['wv']] + COUNTY_NAMES
BLOCK = [b.lower() for b in CFG.get('block', [])]
def relevant(t, wv_outlet=False):
    """On the beat (a match or energy term) and in West Virginia (a WV term, a county, a tracked project,
    or a search limited to a West Virginia outlet)."""
    s = low(t)
    return any(m in s for m in MATCH + ENERGY) and (wv_outlet or any(w in s for w in WV) or bool(projects_of(t)))
def energy_of(t):
    return any(m in low(t) for m in ENERGY)
def projects_of(t):
    s = low(t)
    return [pid for pid, words in CFG['projects'].items() if any(w in s for w in words)]
HOST_NAMES = {f['url'].split('/')[2].replace('www.', ''): f['name'] for f in CFG['feeds']}
def outlet_for(url, given):
    host = urllib.parse.urlparse(url).netloc.replace('www.', '')
    return HOST_NAMES.get(host) or given or host
src_is_google = lambda f: 'news.google.com' in f['url']
norm_title = lambda t: re.sub(r'[^a-z0-9]+', '', t.lower())[:70]

old = json.loads(OUT.read_text()) if OUT.exists() else {'items': []}
by_url = {i['url']: i for i in old['items']}
old_story = {i['url']: i.get('story') for i in old['items']}  # snapshot: cluster() edits items in place
seen_titles = {norm_title(i['title']) for i in old['items']}
added, report = [], []
for src_list, search in ((CFG['feeds'], False), (CFG['searches'], True)):
    for f in src_list:
        try:
            raw = fetch(f['url'])
            if raw.lstrip()[:15].lower().startswith(b'<!doctype html'):  # Bing now and then serves a web page instead of RSS
                time.sleep(5); raw = fetch(f['url'])
            got = items_of(raw)
        except Exception as e:  # one bad feed never stops the run
            report.append(f"FAIL {f['id']}: {type(e).__name__} {str(e)[:80]}"); continue
        kept = 0
        for it in got:
            if not it['title'] or not it['url']: continue
            if src_is_google(f):  # Google News titles end in " - Outlet", and its summary is just the title again
                if it['outlet'] and it['title'].endswith(' - ' + it['outlet']): it['title'] = it['title'][:-len(it['outlet']) - 3].strip()
                it['summary'] = ''
                if f.get('wvOutlet'): it['outlet'] = f['name']
            blob = it['title'] + ' ' + it['summary']
            if not relevant(blob, f.get('wvOutlet', False)): continue
            url = clean_url(it['url'])
            if not url: continue
            if any(b in (url + ' ' + blob).lower() for b in BLOCK): continue
            d = it['date'] or now
            if (now - d).days > KEEP_DAYS or d > now + dt.timedelta(days=1): continue
            nt = norm_title(it['title'])
            if url in by_url or nt in seen_titles: continue
            rec = {'id': re.sub(r'[^a-z0-9]+', '-', urllib.parse.urlparse(url).path.lower()).strip('-')[-60:] or nt[:40],
                   'd': d.strftime('%Y-%m-%dT%H:%M:%SZ'), 'title': it['title'], 'url': url,
                   'source': outlet_for(url, it['outlet'] or f['name']), 'summary': it['summary'][:280],
                   'projects': projects_of(blob), **({'energy': True} if energy_of(blob) else {}), 'via': f['id'], 'seen': now.strftime('%Y-%m-%dT%H:%M:%SZ')}
            by_url[url] = rec; seen_titles.add(nt); added.append(rec); kept += 1
        report.append(f"ok   {f['id']}: {len(got)} items, {kept} new")

# Group coverage of the same story: items within 4 days that share 3+ distinctive title words.
# The lead item is original reporting from a tracked outlet when there is one, never a syndicator.
STOP = set('the a an and or of to in on for with by at from as is are be was were has have that this it its into over after about than more new says said plan plans data center centers centre west virginia county wv w.va project ai could would will may can not but who what why how'.split())
SYND = tuple(CFG.get('syndicators', []))
def words(t): return {w.rstrip('s') for w in re.findall(r"[a-z0-9$]+", t.lower()) if len(w) > 2 and w not in STOP}
PREF = tuple(CFG.get('preferred', [])) + tuple(f['url'].split('/')[2].replace('www.', '') for f in CFG['feeds'])
def rank(i):
    host = urllib.parse.urlparse(i['url']).netloc.replace('www.', '')
    return (host.endswith(SYND), not host.endswith(PREF), i['d'])
def cluster(items):
    groups = []
    for i in sorted(items, key=lambda i: i['d']):
        wi, di = words(i['title']), dt.datetime.fromisoformat(i['d'].replace('Z', '+00:00'))
        home = next((g for g in groups if abs((di - g['d0']).days) <= 4 and len(wi & g['w']) >= 3 and len(wi & g['w']) >= 0.4 * max(1, len(wi))), None)
        if home: home['items'].append(i); home['w'] |= wi
        else: groups.append({'d0': di, 'w': set(wi), 'items': [i]})
    for g in groups:
        lead = min(g['items'], key=rank)
        for i in g['items']: i['story'] = lead['id']
    return items

cutoff = now - dt.timedelta(days=KEEP_DAYS)
items = [i for i in by_url.values() if dt.datetime.fromisoformat(i['d'].replace('Z', '+00:00')) >= cutoff and not any(b in (i['url'] + ' ' + i['title']).lower() for b in BLOCK)]
items.sort(key=lambda i: i['d'], reverse=True)
items = cluster(items[:MAX_ITEMS])
print('\n'.join(report))
print(f'{len(added)} new, {len(items)} total')
for a in sorted(added, key=lambda i: i['d'], reverse=True)[:40]:
    print(f"  + {a['d'][:10]} {a['source'][:22]:22} {'E ' if a.get('energy') else '  '}{a['title'][:90]}  {a['projects']}")
stories = len({i['story'] for i in items})
print(f'{stories} stories after grouping duplicate coverage')
gh = __import__('os').environ.get('GITHUB_OUTPUT')
if gh:
    with open(gh, 'a') as fh: fh.write(f'new={len(added)}\n')
changed = added or len(items) != len(old['items']) or any(i.get('story') != old_story.get(i['url']) for i in items)
if not args.dry_run and changed:
    sources = sorted({f['name'] for f in CFG['feeds']} | {'Bing News search'})
    OUT.write_text(json.dumps({'updated': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'sources': sources, 'items': items}, indent=1, ensure_ascii=False) + '\n')
    print('wrote data/news.json')
