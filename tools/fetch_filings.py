#!/usr/bin/env python3
"""Money Desk collector: SEC EDGAR filings and figures, plus a few FRED indicators.

Reads data/companies.json (who to watch) and writes data/filings.json (what they filed).
Standard library only. No AI model is involved: this is a plain reader of public government data.

  * SEC EDGAR (https://www.sec.gov/os/accessing-edgar-data): recent filings for every company
    with a CIK, a handful of reported figures from each company's XBRL data (revenue, net income,
    capital spending, cash, long-term debt), and full-text searches for filings that name a
    West Virginia project. The SEC requires automated tools to say who they are, so set
    SEC_USER_AGENT to "Name contact@example.com". It is read from the environment only and is
    never written anywhere. Without it, the SEC part is skipped and the old SEC data is kept.
  * FRED (Federal Reserve Bank of St. Louis): daily series such as the Henry Hub gas price,
    rolled up to monthly averages. No key needed.

Every figure keeps its filing's accession number, so the site can link straight to the filing.
The file is rewritten only when something in it changed, so the scheduled job commits only then.

Usage:
  SEC_USER_AGENT="WV AI Watch you@example.com" python3 -I tools/fetch_filings.py
  python3 -I tools/fetch_filings.py --only nvidia,nscale    # a few companies (debugging)
"""
import json, os, sys, time, csv, io, datetime as dt, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / 'data' / 'companies.json'
OUT = ROOT / 'data' / 'filings.json'
UA = os.environ.get('SEC_USER_AGENT', '').strip()

# Forms worth showing a reader, with plain-English names.
FORMS = {
    '10-K': 'Annual report', '10-K/A': 'Annual report (amended)', '10-Q': 'Quarterly report', '10-Q/A': 'Quarterly report (amended)',
    '8-K': 'Current report', '8-K/A': 'Current report (amended)', '20-F': 'Annual report (foreign issuer)', '6-K': 'Current report (foreign issuer)',
    'S-1': 'IPO registration', 'S-1/A': 'IPO registration (amended)', 'F-1': 'IPO registration (foreign issuer)', 'F-1/A': 'IPO registration (amended)',
    '424B4': 'Final prospectus (offering priced)', '424B1': 'Final prospectus (offering priced)', 'DEF 14A': 'Proxy statement',
}
ITEMS_8K = {
    '1.01': 'material agreement', '1.02': 'agreement ended', '1.03': 'bankruptcy', '2.01': 'deal completed', '2.02': 'results',
    '2.03': 'new debt', '2.04': 'debt trigger', '2.05': 'restructuring', '2.06': 'impairment', '3.01': 'listing notice',
    '3.02': 'unregistered share sale', '4.01': 'auditor change', '4.02': 'restatement', '5.02': 'officer or director change',
    '5.03': 'bylaws change', '5.07': 'shareholder vote', '7.01': 'disclosure', '8.01': 'other event',
}
# XBRL concepts, in order of preference (companies differ in which one they use).
CONCEPTS = {
    'revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax',
                'SalesRevenueNet', 'RegulatedAndUnregulatedOperatingRevenue', 'ElectricUtilityRevenue'],
    'netIncome': ['NetIncomeLoss', 'NetIncomeLossAvailableToCommonStockholdersBasic', 'ProfitLoss'],
    'capex': ['PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', 'PaymentsForCapitalImprovements'],
    'cash': ['CashAndCashEquivalentsAtCarryingValue', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents'],
    'debt': ['LongTermDebtNoncurrent', 'LongTermDebt', 'LongTermDebtAndCapitalLeaseObligations'],
}
INSTANT = {'cash', 'debt'}
FILING_DAYS = 400       # how far back the filing list goes
FILINGS_KEEP = 12       # per company
QUARTERS_KEEP = 9       # enough for a year-over-year comparison and a short trend
FRED_MONTHS = 25
STALE_BEFORE = (dt.date.today() - dt.timedelta(days=550)).isoformat()
REFETCH_DAYS = 1   # if the SEC's XBRL data lags a new 10-Q, look again after this many days

LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s, file=sys.stderr)

def get(url, *, sec=False, tries=3):
    headers = {'User-Agent': UA if sec else 'WV-AI-Watch/1.0 (+https://wvaihub.com)', 'Accept-Encoding': 'identity'}
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            if e.code in (403, 429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(2 * (i + 1) ** 2); continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1: time.sleep(2 * (i + 1) ** 2); continue
            raise
        finally:
            if sec: time.sleep(0.15)   # well under the SEC's 10 requests per second

def days(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days

# ------------------------------------------------------------------ SEC: filings list
def recent_filings(sub):
    r = sub.get('filings', {}).get('recent', {})
    cut = (dt.date.today() - dt.timedelta(days=FILING_DAYS)).isoformat()
    out = []
    for i, form in enumerate(r.get('form', [])):
        if form not in FORMS or r['filingDate'][i] < cut: continue
        items = [x.strip() for x in (r.get('items', [''] * (i + 1))[i] or '').split(',') if x.strip()]
        f = {'form': form, 'd': r['filingDate'][i], 'accn': r['accessionNumber'][i], 'doc': r['primaryDocument'][i]}
        if r.get('reportDate') and r['reportDate'][i]: f['period'] = r['reportDate'][i]
        if items: f['items'] = items
        out.append(f)
    return out[:FILINGS_KEEP]

def latest_periodic(sub):
    r = sub.get('filings', {}).get('recent', {})
    for i, form in enumerate(r.get('form', [])):
        if form in ('10-Q', '10-K', '10-Q/A', '10-K/A', '20-F'): return r['accessionNumber'][i]
    return None

# ------------------------------------------------------------------ SEC: figures from XBRL
def facts_for(facts, names):
    """Pick the concept whose newest value is the most recent (companies switch concepts over time)."""
    best = None
    for name in names:
        c = facts.get('facts', {}).get('us-gaap', {}).get(name)
        if not c: continue
        rows = [x for x in c.get('units', {}).get('USD', []) if x.get('form', '').split('/')[0] in ('10-Q', '10-K', '20-F')]
        if not rows: continue
        newest = max(x['end'] for x in rows)
        if newest < STALE_BEFORE: continue   # a concept the company stopped using years ago
        if best is None or newest > best[2]: best = (name, rows, newest)
    return best

def dedupe(rows):
    by = {}
    for x in rows:
        k = (x.get('start'), x['end'])
        if k not in by or x['filed'] > by[k]['filed']: by[k] = x
    return list(by.values())

def pt(x, v=None, derived=False):
    p = {'end': x['end'], 'v': x['val'] if v is None else v, 'accn': x['accn'], 'form': x['form'], 'filed': x['filed']}
    if x.get('start'): p['start'] = x['start']
    if derived: p['derived'] = True
    return p

def duration_series(rows):
    """Quarterly values, deriving any quarter that is only reported year-to-date (cash-flow items, Q4)."""
    rows = [x for x in dedupe(rows) if x.get('start')]
    q = {}
    for x in rows:
        if 80 <= days(x['start'], x['end']) <= 100: q[x['end']] = pt(x)
    by_start = {}
    for x in rows: by_start.setdefault(x['start'], []).append(x)
    for start, lst in by_start.items():
        lst.sort(key=lambda x: x['end'])
        for a, b in zip(lst, lst[1:]):
            if b['end'] in q: continue
            if 80 <= days(a['end'], b['end']) <= 100:
                q[b['end']] = pt(b, round(b['val'] - a['val'], 2), derived=True) | {'start': a['end']}
    quarters = sorted(q.values(), key=lambda p: p['end'])[-QUARTERS_KEEP:]
    years = sorted([pt(x) for x in rows if 350 <= days(x['start'], x['end']) <= 380], key=lambda p: p['end'])[-3:]
    # Fiscal year to date: the longest period ending on the newest date, but not a trailing-twelve-month
    # figure from a 10-Q (some companies, such as Amazon, report those too).
    ytd = None
    if rows:
        newest = max(x['end'] for x in rows)
        cands = [x for x in rows if x['end'] == newest and (x['form'].startswith('10-K') or x['form'].startswith('20-F') or days(x['start'], x['end']) < 300)]
        if cands: ytd = max(cands, key=lambda x: days(x['start'], x['end']))
    out = {'q': quarters, 'fy': years}
    if ytd: out['ytd'] = pt(ytd)
    return out

def metrics(facts):
    m = {}
    for key, names in CONCEPTS.items():
        hit = facts_for(facts, names)
        if not hit: continue
        name, rows, _ = hit
        if key in INSTANT:
            x = max(dedupe(rows), key=lambda x: (x['end'], x['filed']))
            m[key] = {'concept': name, **pt(x)}
        else:
            m[key] = {'concept': name, **duration_series(rows)}
    return m

def sec_company(cid, cik, old):
    sub = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik}.json', sec=True) or b'{}')
    if not sub: log(f'  {cid}: no submissions for CIK {cik}'); return old
    rec = {'cik': cik, 'name': sub.get('name'), 'tickers': sub.get('tickers', []), 'exchanges': [x for x in sub.get('exchanges', []) if x],
           'filings': recent_filings(sub)}
    periodic = latest_periodic(sub)
    today = dt.date.today().isoformat()
    have = old.get('metrics') and old.get('factsFrom') == periodic
    # The SEC's XBRL data sometimes lags a filing by weeks. If the figures we hold don't include the
    # newest 10-Q/10-K yet, look again (at most once a day) instead of waiting for the next quarter.
    lagging = have and not any(v.get('accn') == periodic or any(p.get('accn') == periodic for p in v.get('q', []))
                               for v in old['metrics'].values())
    if have and not (lagging and days(old.get('factsChecked', '2000-01-01'), today) >= REFETCH_DAYS):
        rec['factsFrom'], rec['metrics'], rec['factsChecked'] = periodic, old['metrics'], old.get('factsChecked', today)
    elif periodic:
        raw = get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', sec=True)
        rec['metrics'] = metrics(json.loads(raw)) if raw else {}
        rec['factsFrom'], rec['factsChecked'] = periodic, today
        log(f'  {cid}: figures refreshed (latest periodic filing {periodic})')
    else:
        rec['metrics'] = {}   # no 10-Q or 10-K yet (for example, an IPO still in registration)
    return rec

def sec_search(q, days_back=365):
    end = dt.date.today(); start = end - dt.timedelta(days=days_back)
    url = 'https://efts.sec.gov/LATEST/search-index?' + urllib.parse.urlencode({'q': f'"{q}"', 'dateRange': 'custom', 'startdt': start.isoformat(), 'enddt': end.isoformat()})
    d = json.loads(get(url, sec=True) or b'{}')
    seen, out = set(), []
    for h in d.get('hits', {}).get('hits', []):
        s = h.get('_source', {}); adsh = s.get('adsh')
        if not adsh or adsh in seen: continue
        seen.add(adsh)
        doc = h.get('_id', '').split(':', 1)[-1]
        cik = (s.get('ciks') or [''])[0]
        out.append({'d': s.get('file_date'), 'form': s.get('form'), 'who': [n.split('  (CIK')[0].strip() for n in s.get('display_names', [])], 'cik': cik, 'accn': adsh, 'doc': doc})
    out.sort(key=lambda x: x['d'] or '', reverse=True)
    return {'total': d.get('hits', {}).get('total', {}).get('value', len(out)), 'hits': out[:10]}

# ------------------------------------------------------------------ FRED
def fred(series):
    start = (dt.date.today().replace(day=1) - dt.timedelta(days=31 * FRED_MONTHS)).isoformat()
    raw = get(f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}')
    if not raw: return None
    rows = [(r[0], float(r[1])) for r in csv.reader(io.StringIO(raw.decode('utf-8'))) if len(r) == 2 and r[1] not in ('', '.') and r[0][:1].isdigit()]
    if not rows: return None
    months = {}
    for d, v in rows: months.setdefault(d[:7], []).append(v)
    monthly = [[m, round(sum(v) / len(v), 3)] for m, v in sorted(months.items())][-FRED_MONTHS:]
    last = rows[-1]
    target = (dt.date.fromisoformat(last[0]) - dt.timedelta(days=365)).isoformat()
    ago = max((r for r in rows if r[0] <= target), default=None, key=lambda r: r[0])
    out = {'last': {'d': last[0], 'v': last[1]}, 'monthly': monthly}
    if ago: out['yearAgo'] = {'d': ago[0], 'v': ago[1]}
    return out

# ------------------------------------------------------------------ main
def main():
    only = None
    if '--only' in sys.argv: only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    cfg = json.loads(CFG.read_text())
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    new = {'sec': dict(old.get('sec', {})), 'search': dict(old.get('search', {})), 'fred': dict(old.get('fred', {}))}

    if UA and '@' in UA:
        log('SEC EDGAR')
        for c in cfg['companies']:
            cik = (c.get('sec') or {}).get('cik')
            if not cik or (only and c['id'] not in only): continue
            try: new['sec'][c['id']] = sec_company(c['id'], cik, old.get('sec', {}).get(c['id'], {}))
            except Exception as e: log(f'  {c["id"]}: kept old data ({e})')
        for s in cfg.get('secSearch', []):
            if only: break
            try: new['search'][s['q']] = sec_search(s['q'])
            except Exception as e: log(f'  search "{s["q"]}": kept old data ({e})')
        keep = {c['id'] for c in cfg['companies'] if (c.get('sec') or {}).get('cik')}
        new['sec'] = {k: v for k, v in new['sec'].items() if k in keep}
        new['search'] = {k: v for k, v in new['search'].items() if k in {s['q'] for s in cfg.get('secSearch', [])}}
    else:
        log('SEC_USER_AGENT is not set (it needs a name and an email), so SEC data was not refreshed.')

    log('FRED')
    for s in cfg.get('signals', []):
        if not s.get('fred') or only: continue
        try:
            got = fred(s['fred'])
            if got: new['fred'][s['fred']] = got
        except Exception as e: log(f'  {s["fred"]}: kept old data ({e})')

    # New filings since last time (for the commit message).
    before = {f['accn'] for v in old.get('sec', {}).values() for f in v.get('filings', [])}
    fresh = [f'{k} {f["form"]}' for k, v in new['sec'].items() for f in v.get('filings', []) if f['accn'] not in before]
    if before and fresh: log('New filings: ' + ', '.join(fresh))
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a') as fh: fh.write(f'new={len(fresh) if before else 0}\n')

    content = {k: new[k] for k in ('sec', 'search', 'fred')}
    if content == {k: old.get(k, {}) for k in ('sec', 'search', 'fred')}:
        log('No changes.'); return
    out = {'updated': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           'about': 'Collected by tools/fetch_filings.py from SEC EDGAR and FRED. Figures are as reported in each filing; '
                    '"derived" quarters are a year-to-date figure minus the previous one. accn is the SEC accession number.',
           **content}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    log(f'Wrote {OUT.relative_to(ROOT)}: {len(new["sec"])} companies, {len(new["search"])} searches, {len(new["fred"])} FRED series.')

if __name__ == '__main__':
    main()
