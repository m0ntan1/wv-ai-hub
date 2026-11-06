#!/usr/bin/env python3
"""Voice a cleared Rook's Read with ElevenLabs (phase 2 of the Money Desk).

The audio is made from a SPOKEN SCRIPT, not from the page text: audio/rook/<id>.script.md, written by
Rook for the ear and checked against the cleared Read (see .claude/skills/rooks-read/SKILL.md, step 6).
Each "## name" section is voiced as its own clip, with the sections on either side sent as context so
the delivery flows. The clips are joined with short pauses and normalized to -16 LUFS with ffmpeg.

Then every section is transcribed (ElevenLabs speech-to-text) and compared with the script:
  * every quotation in the script must be heard word for word;
  * the section's words must match the script closely (MIN_MATCH).
A section that fails is re-voiced, up to MAX_RETAKES times, and the best take is kept. If a quotation
still fails, the audio is written anyway but the receipt lists it under "needs_ear_check", the script
exits with status 3, and the pull request must say so. Nothing publishes until the editor merges.

Writes audio/rook/<id>.mp3, sets the Read's "audio" field, and writes a receipt to
audio/rook/<id>.voice.json (model, takes, match scores, credits used). Standard library plus ffmpeg.

Environment (never commit these; in the cloud they live in the environment's settings):
  ELEVENLABS_API_KEY   required
  ROOK_VOICE_ID        required: the saved voice for Rook (made once in ElevenLabs Voice Design)
  ELEVENLABS_MODEL     optional, default eleven_v4. On this account v4 bills about 0.22 credits per
                       character (flash about 0.11): a 3,900-character script is roughly 860 credits.

Usage:
  python3 -I tools/voice_read.py --dry-run [id]   # parse and check the script; no API calls
  python3 -I tools/voice_read.py [id]             # voice one Read (default: newest cleared Read with no audio)
  python3 -I tools/voice_read.py --test           # voice one short line to /tmp; touches nothing in the repo
Only Reads that Mercer has CLEARED are voiced.
"""
import json, os, re, sys, shutil, subprocess, tempfile, uuid, difflib, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READS = ROOT / 'data' / 'reads.json'
AUDIO = ROOT / 'audio' / 'rook'
API = 'https://api.elevenlabs.io/v1'
MIN_MATCH = 0.90          # word-level similarity a section's transcript must reach
MAX_RETAKES = 2           # extra takes per failing section
PAUSE_AFTER_INTRO, PAUSE = 0.9, 0.8
TEST_LINE = ("Up in Barbour County, folks spent Monday telling a transmission company what they think of a power line "
             "that doesn't have a route yet. I'm Rook Calloway, and this is a test of Rook's Read.")


# ------------------------------------------------------------------ script
def parse_script(path):
    """Sections of a spoken script: [(name, text)]. Everything after a line '---' is notes, not spoken."""
    txt = re.split(r'^---\s*$', path.read_text(), maxsplit=1, flags=re.M)[0]
    secs = [(n, b.strip()) for n, b in re.findall(r'^## (\S+)[^\n]*\n(.*?)(?=^## |\Z)', txt, re.S | re.M)]
    return [(n, b) for n, b in secs if b]

def quotes(text):
    return [q.strip() for q in re.findall(r'["“]([^"”]{3,})["”]', text)]

def words(t):
    return re.sub(r'[^a-z0-9 ]', ' ', t.lower().replace('-', ' ').replace('’', "'").replace("'", '')).split()

def squash(t):
    return ''.join(words(t))

def check_script(r, secs):
    """Problems that stop a run before any credits are spent."""
    probs = []
    names = [n for n, _ in secs]
    if not secs: probs.append('the script has no "## name" sections')
    if names and names[-1] != 'outro': probs.append('the last section must be "outro" (the spoken disclaimer)')
    spoken = ' '.join(b for _, b in secs)
    if 'not investment advice' not in spoken.lower(): probs.append('the outro must say "not investment advice"')
    if 'synthetic voice' not in spoken.lower(): probs.append('the script must say Rook has a synthetic voice')
    if r.get('anthropic') and 'anthropic' not in spoken.lower(): probs.append('anthropic is true: the spoken script must disclose the conflict')
    page = ' '.join(r['body'])
    for q in quotes(page):
        if squash(q) not in squash(spoken): probs.append(f'quotation from the page is not verbatim in the script: "{q}"')
    for n, b in secs:
        if len(b) > 4500: probs.append(f'section {n} is {len(b)} characters; split it (limit 4,500)')
    return probs


# ------------------------------------------------------------------ ElevenLabs
def key():
    k, v = os.environ.get('ELEVENLABS_API_KEY'), os.environ.get('ROOK_VOICE_ID')
    if not k or not v: sys.exit('Set ELEVENLABS_API_KEY and ROOK_VOICE_ID first.')
    return k, v

def call(req, what):
    try:
        with urllib.request.urlopen(req, timeout=300) as resp: return resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs {what} returned {e.code}: {e.read()[:300]!r}')
    except urllib.error.URLError as e:
        sys.exit(f'ElevenLabs {what} failed: {e.reason}')

def tts(text, model, prev=None, nxt=None):
    k, v = key()
    body = {'text': text, 'model_id': model}
    if prev: body['previous_text'] = prev
    if nxt: body['next_text'] = nxt
    req = urllib.request.Request(f'{API}/text-to-speech/{v}?output_format=mp3_44100_128', data=json.dumps(body).encode(),
                                 headers={'xi-api-key': k, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'}, method='POST')
    return call(req, 'text-to-speech')

def stt(mp3):
    k, _ = key()
    b = uuid.uuid4().hex
    body = (f'--{b}\r\nContent-Disposition: form-data; name="model_id"\r\n\r\nscribe_v1\r\n'
            f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="clip.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n').encode() \
           + mp3 + f'\r\n--{b}--\r\n'.encode()
    req = urllib.request.Request(f'{API}/speech-to-text', data=body, method='POST',
                                 headers={'xi-api-key': k, 'Content-Type': f'multipart/form-data; boundary={b}'})
    return json.loads(call(req, 'speech-to-text')).get('text', '')

def credits_used():
    try:
        k, _ = key()
        req = urllib.request.Request(f'{API}/user/subscription', headers={'xi-api-key': k})
        return json.loads(urllib.request.urlopen(req, timeout=60).read())['character_count']
    except Exception:
        return None


# ------------------------------------------------------------------ checking a take
def score(text, heard):
    a, b = words(text), words(heard)
    ratio = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
    missed = [q for q in quotes(text) if squash(q) not in squash(heard)]
    return ratio, missed

def good(ratio, missed):
    return ratio >= MIN_MATCH and not missed


# ------------------------------------------------------------------ audio assembly
def join(clips, out):
    if not shutil.which('ffmpeg'): sys.exit('ffmpeg is not installed.')
    ins, fc, cat = [], '', ''
    for j, c in enumerate(clips):
        pad = PAUSE_AFTER_INTRO if j == 0 else (0.3 if j == len(clips) - 1 else PAUSE)
        ins += ['-i', str(c)]
        fc += f'[{j}:a]aresample=44100,apad=pad_dur={pad}[a{j}];'
        cat += f'[a{j}]'
    fc += f'{cat}concat=n={len(clips)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[out]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', fc, '-map', '[out]', '-ac', '1', '-ar', '44100',
                    '-c:a', 'libmp3lame', '-b:a', '96k', str(out)], check=True)
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out)],
                       capture_output=True, text=True, check=True).stdout.strip()
    return round(float(d), 1)


# ------------------------------------------------------------------ main
def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    model = os.environ.get('ELEVENLABS_MODEL', 'eleven_v4')
    log = lambda *m: print(*m, file=sys.stderr)

    if '--test' in sys.argv:
        out = Path(tempfile.gettempdir()) / 'rook-voice-test.mp3'
        out.write_bytes(tts(TEST_LINE, model))
        log(f'Wrote {out} ({out.stat().st_size // 1024} KB, {len(TEST_LINE)} characters, model {model}).')
        return

    data = json.loads(READS.read_text())
    cleared = [r for r in data['reads'] if r.get('mercer', {}).get('status') == 'CLEARED']
    if args: r = next((x for x in cleared if x['id'] == args[0]), None)
    else: r = next((x for x in sorted(cleared, key=lambda x: x['d'], reverse=True) if not x.get('audio')), None)
    if not r: sys.exit('No cleared Read to voice (check the id, or every cleared Read already has audio).')

    sp = AUDIO / f'{r["id"]}.script.md'
    if not sp.exists(): sys.exit(f'No spoken script at {sp.relative_to(ROOT)}. Write it first (rooks-read skill, step 6).')
    secs = parse_script(sp)
    probs = check_script(r, secs)
    chars = sum(len(b) for _, b in secs)
    log(f'Read {r["id"]}: {len(secs)} sections, {chars} characters, model {model}.')
    if probs:
        for p in probs: log('  SCRIPT: ' + p)
        sys.exit('Fix the spoken script before voicing it. No credits spent.')
    if dry:
        for n, b in secs: log(f'  {n:8} {len(b):5} chars  {len(quotes(b))} quote(s)')
        return

    before = credits_used()
    work = Path(tempfile.mkdtemp(prefix='rook-voice-'))
    clips, receipt, ear = [], [], []
    for i, (n, b) in enumerate(secs):
        prev = secs[i - 1][1] if i else None
        nxt = secs[i + 1][1] if i + 1 < len(secs) else None
        takes = []
        for t in range(1 + MAX_RETAKES):
            mp3 = tts(b, model, prev, nxt)
            ratio, missed = score(b, stt(mp3))
            takes.append((ratio, missed, mp3))
            log(f'  {n:8} take {t + 1}: match {ratio:.3f}' + (f', MISSED QUOTE {missed}' if missed else ''))
            if good(ratio, missed): break
        best = max(takes, key=lambda x: (not x[1], x[0]))
        p = work / f'{i:02d}-{n}.mp3'; p.write_bytes(best[2]); clips.append(p)
        receipt.append({'section': n, 'chars': len(b), 'takes': len(takes), 'match': round(best[0], 3), 'missed_quotes': best[1]})
        if not good(best[0], best[1]): ear.append({'section': n, 'match': round(best[0], 3), 'missed_quotes': best[1]})

    out = AUDIO / f'{r["id"]}.mp3'
    out.parent.mkdir(parents=True, exist_ok=True)
    dur = join(clips, out)
    shutil.rmtree(work, ignore_errors=True)
    after = credits_used()
    r['audio'] = f'audio/rook/{r["id"]}.mp3'
    READS.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    rec = {'id': r['id'], 'model': model, 'voice_id': os.environ['ROOK_VOICE_ID'], 'script': f'audio/rook/{r["id"]}.script.md',
           'characters': chars, 'duration_s': dur, 'sections': receipt, 'needs_ear_check': ear,
           'credits_used': (after - before) if before is not None and after is not None else None,
           'note': 'credits_used is the account counter before and after; it can lag by a minute.'}
    (AUDIO / f'{r["id"]}.voice.json').write_text(json.dumps(rec, indent=1) + '\n')
    m, s = divmod(int(dur), 60)
    log(f'Wrote {out.relative_to(ROOT)} ({m}:{s:02d}, {out.stat().st_size // 1024} KB), set the Read\'s audio field, '
        f'and wrote the receipt. Credits used: {rec["credits_used"]}.')
    if ear:
        log('NEEDS EAR CHECK: ' + '; '.join(f'{e["section"]} (match {e["match"]}, missed {e["missed_quotes"]})' for e in ear))
        sys.exit(3)

if __name__ == '__main__':
    main()
