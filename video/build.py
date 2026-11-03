#!/usr/bin/env python3
"""Builds the Rook video: voice clips + footage + plan + song -> MP4, SRT, and QA frames.

  python3 video/build.py --footage F --voice V --song S.mp3 --work W --out O [--placeholder] [--dump 12,30] [--draft]

  --voice     folder holding one clip per scene, named by scene id: 1a.mp3 1b.mp3 2.mp3 ... 8.mp3
  --placeholder  makes stand-in voice clips (noise bursts shaped like speech) so the visuals can be tested for free
  --dump      write PNG frames at those times (seconds) to <out>/qa instead of encoding
  --draft     half-size, fast encode for checking timing

The script text lives in video/script.json, the shots and callouts in video/plan.json (positions are sentence-based,
so they follow the real pacing of the voice). Everything is deterministic: the same inputs give the same video.
"""
import argparse, json, math, os, re, subprocess, sys, html, textwrap
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent
W, H, FPS, SR = 1920, 1080, 30, 48000
SILVER, CYAN = (201, 206, 214), (0, 212, 255)
FONT_B = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf'
OUTRO_START, OUTRO_LEN, END_CARD_S = 180.0, 23.0, 20.5
INTRO_VOICE_START, DUCK, OUTRO_DUCK = 3.5, 0.25, 0.30
OUTRO_GAIN = 0.6   # the outro section of the song is its loudest; keep it from swelling well past Rook's voice
SAY = {'Nscale': '/ˈɛnskeɪl/', 'House Bill 2014': 'House Bill twenty fourteen'}        # how the voice should say it
SHOW = {'W V A I hub dot com': 'wvaihub.com'}                                        # how captions should write it


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def decode(path, ch=1):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', str(ch), '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    a = np.frombuffer(out, dtype=np.float32).copy()
    return a if ch == 1 else a.reshape(-1, ch)


def split_sentences(t):
    return re.split(r'(?<=[.?!])\s+', t.strip())


def tts_text(t):
    for a, b in SAY.items():
        t = t.replace(a, b)
    return t


def show_text(t):
    for a, b in SHOW.items():
        t = t.replace(a, b)
    return t


# ------------------------------------------------------------------ voice clips
def env_db(a, win=480):
    n = len(a) // win
    r = np.sqrt((a[:n * win].reshape(n, win) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(r)


def prepare_clip(a):
    """Trim silence, level to a steady speech loudness, and find pauses (in seconds, relative to the clip)."""
    e = env_db(a)
    act = np.where(e > -50)[0]
    s, t = max(0, (act[0] - 6)), min(len(e), act[-1] + 7)
    a = a[s * 480:t * 480]
    e = env_db(a)
    loud = e[e > -40]
    rms_db = 20 * np.log10(np.sqrt((10 ** (loud / 10)).mean()) + 1e-9) if len(loud) else -30
    a = a * (10 ** ((-21 - rms_db) / 20))
    e = env_db(a)
    pauses, run = [], None
    for i, v in enumerate(e):
        if v < -42 and run is None: run = i
        if (v >= -42 or i == len(e) - 1) and run is not None:
            if (i - run) * 0.01 >= 0.16 and run > 15 and i < len(e) - 15: pauses.append(((run + i) / 2 * 0.01, (i - run) * 0.01))
            run = None
    return np.clip(a, -0.98, 0.98), pauses


def make_placeholder(script, outdir):
    """Stand-in voice: noise bursts with word-like rhythm. Only for testing the visuals."""
    rng = np.random.default_rng(7)
    outdir.mkdir(parents=True, exist_ok=True)
    for name, text in script:
        sid = name.split(' · ')[0]
        parts = []
        for w in re.findall(r'\S+', text):
            d = 0.07 + 0.045 * len(w)
            n = int(d * SR); x = rng.normal(0, 1, n) * np.hanning(n) * 0.25
            parts += [x, np.zeros(int(0.045 * SR))]
            if w.endswith(('.', '?', '!')): parts.append(np.zeros(int(0.5 * SR)))
            elif w.endswith((',', ':')): parts.append(np.zeros(int(0.22 * SR)))
        a = np.concatenate(parts).astype(np.float32)
        raw = outdir / (sid + '.f32')
        a.tofile(raw)
        sh(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', str(raw), str(outdir / (sid + '.wav'))])
        raw.unlink()


# ------------------------------------------------------------------ timeline
def snap(t, cands, used, tol):
    best = None
    for i, (m, _) in enumerate(cands):
        if i in used: continue
        if abs(m - t) <= tol and (best is None or abs(m - t) < abs(cands[best][0] - t)): best = i
    if best is None: return t
    used.add(best)
    return cands[best][0]


def chunk_words(sentence, maxc=50):
    words, out, cur = sentence.split(), [], []
    for w in words:
        cur.append(w)
        line = ' '.join(cur)
        if (len(line) >= maxc) or (w.endswith((',', ':')) and len(line) >= 24):
            out.append(line); cur = []
    if cur:
        if out and len(' '.join(cur)) < 14: out[-1] += ' ' + ' '.join(cur)
        else: out.append(' '.join(cur))
    return out


def prep_footage(footage):
    """Derived images: the map on the right of a dark 16:9 frame, leaving the left for the title."""
    raw, dst = footage / 'map_hero_raw.png', footage / 'map_hero.png'
    if raw.exists() and not dst.exists():
        m = Image.open(raw).convert('RGB'); h = 1040; w = int(m.width * h / m.height)
        bg = Image.new('RGB', (W, H), (11, 13, 16))
        mask = Image.new('L', (w, h), 0); ImageDraw.Draw(mask).rectangle([90, 70, w - 90, h - 70], fill=255)
        bg.paste(m.resize((w, h), Image.LANCZOS), (W - w - 40, 20), mask.filter(ImageFilter.GaussianBlur(60))); bg.save(dst)


def build_timeline(script, plan, voice_dir):
    clips = {}
    for name, text in script:
        sid = name.split(' · ')[0]
        p = next((voice_dir / f'{sid}{e}' for e in ('.mp3', '.wav') if (voice_dir / f'{sid}{e}').exists()), None)
        if p is None: sys.exit(f'missing voice clip for scene {sid} in {voice_dir}')
        a, pauses = prepare_clip(decode(p))
        clips[sid] = {'text': text, 'a': a, 'pauses': pauses, 'dur': len(a) / SR}
    t1a = INTRO_VOICE_START
    t1b = max(11.0, t1a + clips['1a']['dur'] + 0.6)
    starts = {'1a': t1a, '1b': t1b}
    cursor = t1b + clips['1b']['dur'] + 0.9
    order = ['2', '3', '4', '5', '6', '7', '8']
    for sid in order:
        starts[sid] = cursor
        cursor += clips[sid]['dur'] + 0.9
    end_vo8 = starts['8'] + clips['8']['dur']
    video_end = end_vo8 + END_CARD_S
    prev_end = t1b + clips['1b']['dur']
    vis = {}
    for i, sid in enumerate(order):
        vs = (prev_end + starts[sid]) / 2
        vis[sid] = [vs, None]
        if i: vis[order[i - 1]][1] = vs
        prev_end = starts[sid] + clips[sid]['dur']
    vis['8'][1] = video_end
    # sentence start times and caption chunks, from the real audio
    caps, sent = [], {}
    for sid in ['1a', '1b'] + order:
        c = clips[sid]; sents = split_sentences(c['text']); n = len(sents)
        w = np.array([len(s) for s in sents], float); cum = np.cumsum(w) / w.sum()
        used, b = set(), [0.0]
        for k in range(1, n):
            t = snap(cum[k - 1] * c['dur'], c['pauses'], used, 0.9)
            b.append(max(t, b[-1] + 0.3))
        b.append(c['dur'])
        sent[sid] = [starts[sid] + x for x in b]
        for k, s in enumerate(sents):
            chunks = chunk_words(s); cw = np.array([len(x) for x in chunks], float); cc = np.cumsum(cw) / cw.sum()
            used2, cb = set(), [b[k]]
            for j in range(1, len(chunks)):
                t = b[k] + cc[j - 1] * (b[k + 1] - b[k])
                cb.append(max(snap(t, c['pauses'], used2, 0.5), cb[-1] + 0.4))
            cb.append(b[k + 1])
            for j, ch in enumerate(chunks):
                caps.append({'t0': starts[sid] + cb[j] - 0.04, 't1': min(starts[sid] + cb[j + 1] + 0.12, starts[sid] + c['dur'] + 0.25), 'text': show_text(ch)})
    for i in range(len(caps) - 1): caps[i]['t1'] = min(caps[i]['t1'], caps[i + 1]['t0'] - 0.02)
    return clips, starts, vis, sent, caps, end_vo8, video_end


def coord_time(sid, x, vis, sent):
    n = len(sent[sid]) - 1
    pts = [vis[sid][0]] + [sent[sid][k] for k in range(1, n)] + [vis[sid][1]]
    x = min(max(x, 0), n)
    if x >= n: return pts[-1]
    k = int(x)
    return pts[k] + (x - k) * (pts[k + 1] - pts[k])


def resolve(plan, vis, sent, end_vo8, video_end):
    shots, ovs = [], []
    t2 = vis['2'][0]
    for s in plan['intro']['shots']:
        shots.append({**s, 't0': s['t0'], 't1': t2 if s['t1'] == 'end' else s['t1']})
    for o in plan['intro']['overlays']:
        ovs.append({'id': o['id'], 't0': o['t0'], 't1': t2 + 0.8 if o['t1'] == 'end' else o['t1']})
    for sid, sc in plan['scenes'].items():
        n = len(sent[sid]) - 1
        for s in sc['shots']:
            f, t = s['from'], n if s['to'] == 'end' else s['to']
            shots.append({**{k: v for k, v in s.items() if k not in ('from', 'to')}, 't0': coord_time(sid, f, vis, sent), 't1': coord_time(sid, t, vis, sent)})
        for o in sc['overlays']:
            t = n if o['to'] == 'end' else o['to']
            ovs.append({'id': o['id'], 't0': coord_time(sid, o['from'], vis, sent), 't1': coord_time(sid, t, vis, sent) if o['to'] != 'end' else video_end})
    ovs.append({'id': 'asof', 't0': t2, 't1': video_end})
    shots.sort(key=lambda s: s['t0'])
    return shots, ovs


# ------------------------------------------------------------------ overlays (rendered by Playwright, in the site's fonts)
CHIPS = {
    'chip_13': ('', '13 projects · 4 certified by the state'),
    'chip_verify': ('signal', '⚠ Verify = we could not fully confirm this'),
    'chip_certified': ('', 'Certified: 4 · Monarch’s marker shows “under construction”'),
    'chip_hb2014': ('', 'HB 2014: certified data centers skip county zoning'),
    'chip_docket': ('', '7 PSC dockets · 3 court cases · 50+ public dates'),
    'chip_people': ('', '52 entries · 54 sourced connections'),
    'chip_receipts': ('ok', 'Checked Nov 3, 2026: 183 against linked source · 11 from PSC notices · 8 flagged'),
    'chip_s1': ('', 'Nscale S-1, filed Sep 18, 2026'),
    'chip_fin': ('', 'Revenue $140.6M · Net loss $1,020.1M <small>(first half of 2026, unaudited)</small>'),
    'chip_anthropic': ('', 'Anthropic agreements: up to approximately $44.6B'),
    'chip_watch': ('signal', 'Watch · analysis · middle of three levels'),
    'chip_ai': ('rook', 'AI persona · synthetic voice'),
    'chip_mercer': ('copper', 'Mercer Lang (AI persona) checks every Read'),
    'chip_rick': ('', 'Every Read is approved by Rick Thomas'),
    'chip_notadvice': ('copper', 'Not investment advice. MØNTAN1 and Rick Thomas are not registered investment advisors.'),
    'chip_url': ('', 'wvaihub.com'),
}


def overlay_specs(caps, asof):
    spec = [{'id': k, 'html': f'<div class="chip {c}">{t}</div>', 'width': 1180 if k == 'chip_notadvice' else 0} for k, (c, t) in CHIPS.items()]
    spec += [
        {'id': 'lt_rook', 'html': '<div class="lt"><div class="n">Rook Calloway</div><div class="r">AI PERSONA · SYNTHETIC VOICE</div></div>'},
        {'id': 'bar_disclaimer', 'html': '<div class="bar"><b>◆</b> Analysis for education only. Not investment advice.</div>'},
        {'id': 'asof', 'html': f'<div class="asof">{html.escape(asof)}</div>'},
        {'id': 'title', 'html': '<div class="title"><div class="k">Mapping AI across the Mountain State</div><div class="a">West Virginia\'s</div><div class="b">AI Watch</div></div>'},
        {'id': 'end_card', 'html': '<div class="end"><div class="u">wvaihub<i>.</i>com</div><div class="t">Mountaineers are always free</div><div class="m">Montani semper liberi &middot; West Virginia state motto</div>'
                                   f'<div class="s">Rook is an AI persona. Synthetic voice.<br>{html.escape(asof)}.</div></div>'},
    ]
    for i, c in enumerate(caps):
        spec.append({'id': f'cap{i:03d}', 'html': f'<div class="cap">{html.escape(c["text"])}</div>'})
    return spec


# ------------------------------------------------------------------ frame renderer (runs in worker processes)
G = {}


def init_worker(work, footage):
    G['work'], G['footage'] = Path(work), Path(footage)
    G['tl'] = json.load(open(G['work'] / 'timeline.json'))
    G['scope'] = np.load(G['work'] / 'scope.npy', mmap_mode='r')
    G['ov'] = {}
    G['sizes'] = json.load(open(G['work'] / 'ov' / 'sizes.json'))
    G['img'] = {}
    G['seq'] = {}
    G['font'] = ImageFont.truetype(FONT_B, 22)
    G['mapfonts'] = (ImageFont.truetype(FONT_B, 70), ImageFont.truetype(FONT_B, 40), ImageFont.truetype(FONT_R, 28))
    G['mapcaps'] = None
    m = Image.new('L', (1109, 1000), 0); ImageDraw.Draw(m).rectangle([70, 60, 1109 - 70, 1000 - 60], fill=255)
    G['mapmask'] = m.filter(ImageFilter.GaussianBlur(45))
    g = np.zeros((H, W, 4), np.uint8); a = np.linspace(0, 190, 300)
    g[H - 300:, :, 3] = (a[:, None] * 0.8).astype(np.uint8)
    G['scrim'] = Image.fromarray(g, 'RGBA')


def load_still(name):
    if name not in G['img']:
        if len(G['img']) > 24: G['img'].pop(next(iter(G['img'])))
        G['img'][name] = Image.open(G['footage'] / f'{name}.png').convert('RGB')
    return G['img'][name]


def seq_files(name):
    if name not in G['seq']:
        G['seq'][name] = sorted((G['footage'] / name).glob('*.jpg'))
    return G['seq'][name]


def load_frame(path):
    k = str(path)
    if k not in G['img']:
        if len(G['img']) > 24: G['img'].pop(next(iter(G['img'])))
        G['img'][k] = Image.open(path).convert('RGB')
    return G['img'][k]


def ease(x): return 0.5 - 0.5 * math.cos(math.pi * min(max(x, 0), 1))


def kb_crop(img, kb, p):
    z0, x0, y0, z1, x1, y1 = kb
    e = ease(p)
    z, cx, cy = z0 + (z1 - z0) * e, x0 + (x1 - x0) * e, y0 + (y1 - y0) * e
    cw, ch = W / z, H / z
    l = min(max(cx * W - cw / 2, 0), W - cw); t = min(max(cy * H - ch / 2, 0), H - ch)
    # Page text starts about 54px from the left edge. For gentle zooms (under 1.6x) never start the crop more than
    # 40px in, so a headline is never clipped ("nthropic"); the fade-out keeps the close-up zooms exactly as planned.
    w = min(1.0, max(0.0, (1.6 - z) / 0.2))
    l = l * (1 - w) + min(l, 40.0) * w
    return img.resize((W, H), Image.BICUBIC, box=(l, t, l + cw, t + ch))


def map_composite(frame, cap):
    """The map on the right of a dark frame; the date, count and latest event set in large type on the left."""
    h = 1000; w = int(frame.width * h / frame.height)
    bg = Image.new('RGB', (W, H), (11, 13, 16))
    bg.paste(frame.resize((w, h), Image.BILINEAR), (W - w - 40, 40), G['mapmask'].resize((w, h)) if w != 1109 else G['mapmask'])
    d = ImageDraw.Draw(bg); fl, fc, fd = G['mapfonts']
    label = cap.get('label', '').title().replace('Today · ', 'Today, ')
    d.text((70, 250), label, fill=(237, 232, 220), font=fl)
    text = cap.get('text', '')
    head, _, rest = text.partition('. ')
    if 'on the map' in head:
        d.text((70, 350), head.strip('.'), fill=CYAN, font=fc)
    else:
        rest = text
    rest = rest.replace('Latest: ', '').strip()
    y = 440
    for line in textwrap.wrap(rest, 38)[:6]:
        d.text((70, y), line, fill=(169, 164, 151), font=fd); y += 40
    return bg


def shot_image(s, t):
    p = (t - s['t0']) / max(1e-6, s['t1'] - s['t0'])
    pc = min(max(p, 0), 1)
    if s['src'] == 'black': return Image.new('RGB', (W, H), (11, 13, 16))
    if s['src'].startswith('seq_'):
        files = seq_files(s['src']); r0, r1 = s.get('range', [0, 1]); idx = (r0 + (r1 - r0) * pc) * (len(files) - 1)
        i0 = int(math.floor(idx)); i1 = min(i0 + 1, len(files) - 1); f = idx - i0
        im = load_frame(files[i0])
        # Scroll sequences are shot at the video frame rate: take the nearest real frame (blending two scroll
        # positions double-exposes the text). Only the map and hover sequences, where things fade in place, blend.
        if s['src'] in ('seq_map', 'seq_money_hover'):
            if f > 0.02 and i1 != i0: im = Image.blend(im, load_frame(files[i1]), f)
        elif f >= 0.5: im = load_frame(files[i1])
        if s['src'] == 'seq_map':
            if G['mapcaps'] is None: G['mapcaps'] = json.load(open(G['footage'] / 'seq_map' / 'captions.json'))
            im = map_composite(im, G['mapcaps'][min(len(G['mapcaps']) - 1, int(round(idx)))])
    else:
        im = load_still(s['src'])
    if s.get('kb'): im = kb_crop(im, s['kb'], pc)
    elif not s['src'].startswith('seq_'): im = kb_crop(im, [1.0, 0.5, 0.5, 1.05, 0.5, 0.5], pc)
    if s.get('dim'): im = ImageEnhance.Brightness(im).enhance(1 - s['dim'])
    return im


def base_image(t):
    shots = G['tl']['shots']
    i = next((k for k, s in enumerate(shots) if s['t0'] <= t < s['t1']), len(shots) - 1 if t >= shots[-1]['t1'] else 0)
    s = shots[i]
    if i + 1 < len(shots):
        f = shots[i + 1].get('fade', 0.4)
        if t > s['t1'] - f / 2: return Image.blend(shot_image(s, t), shot_image(shots[i + 1], t), min(1, (t - (s['t1'] - f / 2)) / f))
    f = s.get('fade', 0.4)
    if i > 0 and t < s['t0'] + f / 2:
        return Image.blend(shot_image(shots[i - 1], t), shot_image(s, t), 0.5 + (t - s['t0']) / f)
    return shot_image(s, t)


def overlay_png(oid):
    if oid not in G['ov']:
        G['ov'][oid] = Image.open(G['work'] / 'ov' / f'{oid}.png').convert('RGBA')
    return G['ov'][oid]


def place(base, oid, alpha, x, y):
    if alpha <= 0.01: return
    ov = overlay_png(oid)
    if alpha < 0.99: ov = ov.copy(); ov.putalpha(ov.getchannel('A').point(lambda v: int(v * alpha)))
    base.paste(ov, (int(x), int(y)), ov)


def anchor(oid, w, h, slide):
    if oid.startswith('chip_'): return 70, 790 + slide
    if oid == 'lt_rook': return 0, 760 + slide
    if oid == 'bar_disclaimer': return 0, 0
    if oid == 'asof': return W - w - 48, H - h - 22
    if oid in ('title', 'end_card'): return 0, 250 + slide
    if oid.startswith('cap'): return (W - w) // 2, H - h - 66
    return 0, 0


def scope_frame(img, t, strength):
    """An oscilloscope trace of the actual audio (silver), with a soft glow."""
    if strength <= 0.01: return img
    sc = G['scope']; c = int(t * SR); win = 2400
    seg = np.array(sc[max(0, c - win):c]) if c > 0 else np.zeros(win, np.float32)
    if len(seg) < win: seg = np.pad(seg, (win - len(seg), 0))
    pts = seg[::5][:480]
    amp = 330 * np.clip(pts * 2.6, -1, 1)
    xs = np.linspace(210, W - 210, len(pts))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    xy = [(float(x), float(H / 2 + 20 + a)) for x, a in zip(xs, amp)]
    d.line(xy, fill=SILVER + (255,), width=5, joint='curve')
    glow = layer.filter(ImageFilter.GaussianBlur(10))
    out = img.convert('RGBA')
    for L in (glow, layer):
        if strength < 0.99: L = L.copy(); L.putalpha(L.getchannel('A').point(lambda v: int(v * strength)))
        out.alpha_composite(L)
    return out.convert('RGB')


def bug(img, t):
    """Small silver level meter, bottom left: who is speaking."""
    sc = G['scope']; c = int(t * SR); n, bw, gap = 18, 5, 4
    x0, y0 = 52, H - 52
    pill = Image.new('RGBA', (n * (bw + gap) + 100, 62), (11, 13, 16, 200))
    img.paste(pill, (x0 - 16, y0 - 50), pill)
    d = ImageDraw.Draw(img)
    for i in range(n):
        s = int(max(0, c - (n - i) * 960)); seg = np.array(sc[s:s + 960])
        v = float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0
        h = 4 + min(1, v * 7) * 38
        d.rectangle([x0 + i * (bw + gap), y0 - h, x0 + i * (bw + gap) + bw, y0], fill=SILVER)
    d.text((x0 + n * (bw + gap) + 14, y0 - 24), 'ROOK', fill=SILVER, font=G['font'])
    return img


def render_frame(t):
    tl = G['tl']
    img = base_image(t)
    # intro: static and the scope, then the title hit at the song's drop
    if t < 10.4:
        if t < 3.2:
            n = (np.random.default_rng(int(t * FPS)).random((H // 4, W // 4)) * 255).astype(np.uint8)
            noise = Image.fromarray(n, 'L').resize((W, H), Image.NEAREST)
            a = 0.30 * (1 - t / 3.2)
            img = Image.blend(img, Image.merge('RGB', (noise, noise, noise)), a)
        img = scope_frame(img, t, min(1, t / 0.6) * (1 - min(1, max(0, (t - 9.2) / 0.8))))
    if tl['flash'] <= t < tl['flash'] + 0.4:
        img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), 0.35 * (1 - (t - tl['flash']) / 0.4))
    if t >= 3.0:
        img = img.convert('RGBA'); img.alpha_composite(G['scrim']); img = img.convert('RGB')
    if t >= tl['bug0'] and t <= tl['bug1']: img = bug(img, t)
    for o in tl['ovs']:
        if o['t0'] - 0.01 <= t <= o['t1'] + 0.01:
            fi = 0.25 if o['id'] != 'asof' else 0.6
            a = min(1, (t - o['t0']) / fi) * min(1, (o['t1'] - t) / 0.25)
            w, h = G['sizes'][o['id']]
            x, y = anchor(o['id'], w, h, int((1 - min(1, (t - o['t0']) / fi)) * 22))
            place(img, o['id'], a, x, y)
    if any(c['t0'] <= t <= c['t1'] for c in tl['caps']):
        i = next(k for k, c in enumerate(tl['caps']) if c['t0'] <= t <= c['t1'])
        c = tl['caps'][i]
        a = min(1, (t - c['t0']) / 0.1) * min(1, (c['t1'] - t) / 0.1)
        w, h = G['sizes'][f'cap{i:03d}']
        place(img, f'cap{i:03d}', a, (W - w) // 2, H - h - 66)
    return img


def render_chunk(args):
    f0, f1, out, scale, crf = args
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}' if scale == 1 else f'{int(W * scale)}x{int(H * scale)}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'fast' if scale == 1 else 'ultrafast', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-g', '60', '-bf', '2', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        im = render_frame(f / FPS)
        if scale != 1: im = im.resize((int(W * scale), int(H * scale)), Image.BILINEAR)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
    return out


# ------------------------------------------------------------------ audio
def mix_audio(clips, starts, end_vo8, video_end, song, t1b_end):
    total = int((video_end + 0.5) * SR)
    voice = np.zeros(total, np.float32)
    for sid, c in clips.items():
        s = int(starts[sid] * SR); voice[s:s + len(c['a'])] += c['a']
    music = np.zeros((total, 2), np.float32)
    fade_end = t1b_end + 3.0
    n = int(fade_end * SR); t = np.arange(n) / SR
    env = np.where(t < 10, 1.0, np.where(t < 12, 1 - (1 - DUCK) * (t - 10) / 2, DUCK))
    env = env * np.clip((fade_end - t) / 3.0, 0, 1)
    music[:n] += song[:n] * env[:, None]
    m = int(OUTRO_LEN * SR); seg = song[int(OUTRO_START * SR):int(OUTRO_START * SR) + m]
    seg = np.pad(seg, ((0, m - len(seg)), (0, 0)))
    st = int((video_end - OUTRO_LEN) * SR); tt = st / SR + np.arange(m) / SR
    duck = np.where(tt < end_vo8, OUTRO_DUCK, np.minimum(1.0, OUTRO_DUCK + (1 - OUTRO_DUCK) * (tt - end_vo8) / 1.5))
    fade_in = np.clip(np.arange(m) / SR / 1.5, 0, 1)
    music[st:st + m] += seg * (duck * fade_in * OUTRO_GAIN)[:, None]
    mix = music + voice[:, None]
    return mix.astype(np.float32), voice


def loudnorm_to_m4a(mix, out):
    raw = out.with_suffix('.f32'); mix.tofile(raw)
    base = ['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(raw)]
    # the measurement prints its numbers at info level, so this pass must not use -v error
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(raw), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, check=True)
    j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    af = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    sh(base + ['-af', af, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-y', str(out)])
    raw.unlink()
    return j


def srt_time(s):
    ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--footage', required=True); ap.add_argument('--voice', required=True); ap.add_argument('--song', required=True)
    ap.add_argument('--work', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--placeholder', action='store_true'); ap.add_argument('--draft', action='store_true')
    ap.add_argument('--dump', default=''); ap.add_argument('--no-encode', action='store_true')
    ap.add_argument('--reuse-chunks', action='store_true', help='skip rendering video chunks that already exist in --work (same plan and timing only)')
    a = ap.parse_args()
    work, out, voice_dir = Path(a.work), Path(a.out), Path(a.voice)
    work.mkdir(parents=True, exist_ok=True); out.mkdir(parents=True, exist_ok=True)
    script = json.load(open(HERE / 'script.json')); plan = json.load(open(HERE / 'plan.json'))
    prep_footage(Path(a.footage))
    if a.placeholder: make_placeholder(script, voice_dir)
    clips, starts, vis, sent, caps, end_vo8, video_end = build_timeline(script, plan, voice_dir)
    shots, ovs = resolve(plan, vis, sent, end_vo8, video_end)
    t1b_end = starts['1b'] + clips['1b']['dur']
    print(f'scene starts: ' + ', '.join(f'{k}@{v:.1f}' for k, v in starts.items()) + f' | voice ends {end_vo8:.1f} | video {video_end:.1f}s ({int(video_end // 60)}:{int(video_end % 60):02d})')
    song = decode(a.song, ch=2)
    mix, voice = mix_audio(clips, starts, end_vo8, video_end, song, t1b_end)
    mono = (mix.mean(1)).astype(np.float32); np.save(work / 'scope.npy', mono)
    caps_all = caps
    spec = overlay_specs(caps_all, plan['asof'])
    json.dump(spec, open(work / 'overlays.json', 'w'), ensure_ascii=False)
    sh(['node', str(HERE / 'overlays.js'), str(work / 'overlays.json'), str(work / 'ov')])
    # captions as .srt for YouTube
    with open(out / 'rook-video.srt', 'w') as f:
        for i, c in enumerate(caps_all): f.write(f"{i + 1}\n{srt_time(c['t0'])} --> {srt_time(c['t1'])}\n{c['text']}\n\n")
    tl = {'shots': shots, 'ovs': ovs, 'caps': caps_all, 't2': vis['2'][0], 'flash': 10.0, 'bug0': 11.0, 'bug1': end_vo8 + 0.6}
    json.dump(tl, open(work / 'timeline.json', 'w'))
    json.dump({'starts': starts, 'vis': vis, 'sent': sent, 'end_vo8': end_vo8, 'video_end': video_end}, open(out / 'timing.json', 'w'), indent=1)
    if a.dump:
        init_worker(work, a.footage)
        (out / 'qa').mkdir(exist_ok=True)
        for t in [float(x) for x in a.dump.split(',')]:
            render_frame(t).save(out / 'qa' / f'f_{t:07.2f}.png')
        print('dumped', a.dump); return
    if a.no_encode: return
    scale = 0.5 if a.draft else 1.0; crf = 30 if a.draft else 17
    nf = int(video_end * FPS) + 1
    nproc = 4; per = math.ceil(nf / (nproc * 3))
    jobs = [(i, min(nf, i + per), work / f'chunk{i // per:03d}.mp4', scale, crf) for i in range(0, nf, per)]
    if a.reuse_chunks and all(j[2].exists() for j in jobs):
        done = [j[2] for j in jobs]
    else:
        with Pool(nproc, initializer=init_worker, initargs=(str(work), a.footage)) as pool:
            done = pool.map(render_chunk, jobs, chunksize=1)
    with open(work / 'chunks.txt', 'w') as f:
        for d in done: f.write(f"file '{Path(d).resolve()}'\n")   # absolute: ffmpeg resolves relative paths against the list file
    sh(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(work / 'chunks.txt'), '-c', 'copy', str(work / 'video.mp4')])
    ln = loudnorm_to_m4a(mix, work / 'audio.m4a')
    final = out / ('rook-video-draft.mp4' if a.draft else 'rook-video.mp4')
    sh(['ffmpeg', '-v', 'error', '-y', '-i', str(work / 'video.mp4'), '-i', str(work / 'audio.m4a'), '-c', 'copy', '-shortest', '-movflags', '+faststart', str(final)])
    print('wrote', final, f'{final.stat().st_size / 1e6:.1f} MB', '| loudness before normalizing:', ln['input_i'], 'LUFS')


if __name__ == '__main__':
    main()
