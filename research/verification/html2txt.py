import sys, re, html, pathlib
from html.parser import HTMLParser
class T(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style','noscript','svg'): s.skip+=1
        if t in ('p','br','div','li','h1','h2','h3','h4','tr','td'): s.out.append(' ')
    def handle_endtag(s,t):
        if t in ('script','style','noscript','svg') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
d = pathlib.Path(sys.argv[1])
for f in d.glob('*.html'):
    raw = f.read_bytes().decode('utf-8','replace')
    t = T();
    try: t.feed(raw)
    except Exception: pass
    txt = re.sub(r'\s+',' ', html.unescape(' '.join(t.out)))
    # also keep JSON-LD/meta text which carries article body on some CMSs
    meta = ' '.join(re.findall(r'"(?:articleBody|description)"\s*:\s*"([^"]{40,})"', raw))
    meta += ' ' + ' '.join(re.findall(r'<meta[^>]+content="([^"]{40,})"', raw))
    f.with_suffix('.txt').write_text(txt + ' ' + html.unescape(meta))
print('ok')
