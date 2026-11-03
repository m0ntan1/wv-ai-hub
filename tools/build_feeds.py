"""Build the files the site publishes from data/*.json.

  calendar.ics          subscribable calendar of every dated event (Google/Apple/Outlook)
  feed.json             JSON Feed 1.1 of the desk log (what changed, newest first)
  assets/qr/<county>.svg  QR codes for the printable county sheets (needs `segno`)
  assets/sitemap.xml    sitemap with today's lastmod

Usage: python3 -I tools/build_feeds.py            (run from the repo root after editing data/)
QR codes need the small pure-Python `segno` package: pip install segno
Without it, the QR step is skipped with a warning and everything else still builds.
"""
import json, re, sys, datetime, pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
load = lambda n: json.loads((DATA / f'{n}.json').read_text())
meta, events, desk, projects, lines, standing = load('meta'), load('events'), load('desk'), load('projects'), load('lines'), load('standing')
SITE = meta['site'].rstrip('/')
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

# ---------------------------------------------------------------- calendar.ics
VTZ = ['BEGIN:VTIMEZONE', 'TZID:America/New_York', 'BEGIN:DAYLIGHT', 'TZOFFSETFROM:-0500', 'TZOFFSETTO:-0400', 'TZNAME:EDT', 'DTSTART:19700308T020000',
       'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU', 'END:DAYLIGHT', 'BEGIN:STANDARD', 'TZOFFSETFROM:-0400', 'TZOFFSETTO:-0500', 'TZNAME:EST',
       'DTSTART:19701101T020000', 'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU', 'END:STANDARD', 'END:VTIMEZONE']
def ics_esc(s): return str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
def fold(line):
    out = []
    while len(line.encode()) > 74:
        cut = 74
        while len(line[:cut].encode()) > 74: cut -= 1
        out.append(line[:cut]); line = ' ' + line[cut:]
    out.append(line)
    return '\r\n'.join(out)
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
vevents = []
for e in events:
    if not e.get('date') or e.get('tbd') or e.get('approx'):
        continue
    d = e['date'].replace('-', '')
    L = ['BEGIN:VEVENT', f"UID:{e['id']}@wvaihub.com", f'DTSTAMP:{stamp}']
    if e.get('start'):
        end_t = e.get('endt') or f"{min(int(e['start'][:2]) + 2, 23):02d}:{e['start'][3:]}"
        L += [f"DTSTART;TZID=America/New_York:{d}T{e['start'].replace(':', '')}00",
              f"DTEND;TZID=America/New_York:{(e.get('end') or e['date']).replace('-', '')}T{end_t.replace(':', '')}00"]
    else:
        end = datetime.date.fromisoformat(e.get('end') or e['date']) + datetime.timedelta(days=1)
        L += [f'DTSTART;VALUE=DATE:{d}', f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}"]
    L.append('SUMMARY:' + ics_esc(e['title']))
    loc = ', '.join(x for x in [e.get('venue'), e.get('address'), e.get('virtual')] if x)
    if loc: L.append('LOCATION:' + ics_esc(loc))
    desc = '\n'.join(x for x in [e.get('desc'), e.get('how') and 'How to take part: ' + e['how'], e.get('flag') and 'Note: ' + e['flag'],
                                 *[f"{s['label']}: {s['url']}" for s in e.get('sources', [])], f"Via WV AI Watch: {SITE}/#/calendar?e={e['id']}"] if x)
    L.append('DESCRIPTION:' + ics_esc(desc))
    if e.get('sources'): L.append('URL:' + e['sources'][0]['url'])
    L.append('END:VEVENT')
    vevents.append('\r\n'.join(fold(x) for x in L))
ics = '\r\n'.join(['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//WV AI Watch//Calendar//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
                   'X-WR-CALNAME:WV AI Watch', 'X-WR-CALDESC:Hearings\\, meetings\\, deadlines\\, and protests in West Virginia\'s data center and grid fights.',
                   'X-WR-TIMEZONE:America/New_York', 'REFRESH-INTERVAL;VALUE=DURATION:PT12H', 'X-PUBLISHED-TTL:PT12H', *VTZ, *vevents, 'END:VCALENDAR']) + '\r\n'
(ROOT / 'calendar.ics').write_text(ics, newline='')
print(f'calendar.ics: {len(vevents)} events')

# ---------------------------------------------------------------- feed.json
by = {p['id']: p for p in projects}
items = []
for x in sorted(desk, key=lambda x: x['d'], reverse=True):
    pid = x.get('project')
    items.append({'id': f"{x['d']}-{slug(x['t'])[:48]}", 'url': f"{SITE}/#/project/{pid}" if pid in by else SITE + '/',
                  'external_url': x['src'], 'title': x['t'], 'content_text': x['t'] + ' Source: ' + x['src'],
                  'date_published': x['d'] + 'T12:00:00-05:00', 'tags': [pid] if pid else []})
feed = {'version': 'https://jsonfeed.org/version/1.1', 'title': 'WV AI Watch: on the desk', 'home_page_url': SITE + '/', 'feed_url': SITE + '/feed.json',
        'description': "Dated, sourced updates on West Virginia's data center and AI power projects.", 'language': 'en-US', 'items': items}
(ROOT / 'feed.json').write_text(json.dumps(feed, indent=1, ensure_ascii=False) + '\n')
print(f'feed.json: {len(items)} items')

# ---------------------------------------------------------------- QR codes for county sheets
counties = set()
for p in projects: counties.update(p['counties'])
for l in lines: counties.update(l.get('counties', []))
for s in standing: counties.add(s['county'])
for e in events:
    if e.get('county') and e['county'] != 'Statewide': counties.add(e['county'])
try:
    import segno
    qd = ROOT / 'assets' / 'qr'; qd.mkdir(parents=True, exist_ok=True)
    for c in sorted(counties):
        segno.make(f'{SITE}/#/county/{slug(c)}', error='m').save(str(qd / f'{slug(c)}.svg'), scale=4, border=2, dark='#000', light='#fff', xmldecl=False, svgns=True)
    print(f'assets/qr: {len(counties)} county QR codes')
except ImportError:
    print('WARNING: segno not installed; skipped QR codes (pip install segno)', file=sys.stderr)

# ---------------------------------------------------------------- sitemap
lm = meta['updated']
urls = [('/', '1.0', 'weekly'), ('/calendar.ics', '0.6', 'daily'), ('/feed.json', '0.5', 'daily'), ('/data/projects.json', '0.4', 'weekly'),
        ('/data/events.json', '0.4', 'daily'), ('/data/docket.json', '0.4', 'weekly'),
        ('/data/companies.json', '0.4', 'weekly'), ('/data/filings.json', '0.3', 'daily'), ('/data/reads.json', '0.4', 'daily')]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for u, pr, cf in urls:
    sm.append(f'  <url><loc>{escape(SITE + u)}</loc><lastmod>{lm}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority>'
              + ('<image:image><image:loc>' + SITE + '/assets/og-image.png</image:loc><image:title>West Virginia\'s AI Watch</image:title></image:image>' if u == '/' else '') + '</url>')
sm.append('</urlset>')
(ROOT / 'assets' / 'sitemap.xml').write_text('\n'.join(sm) + '\n')
print('assets/sitemap.xml written')
