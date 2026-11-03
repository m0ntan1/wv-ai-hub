#!/usr/bin/env python3
"""Voice a cleared Rook's Read with ElevenLabs text-to-speech (phase 2 of the Money Desk).

Reads data/reads.json, builds a spoken script from one Read (title, body without the [n] source
markers, and a short spoken disclaimer), asks ElevenLabs for an MP3, saves it to
audio/rook/<id>.mp3, and sets that Read's "audio" field. Standard library only.

Environment (never commit these; in the cloud they live in the environment's secrets):
  ELEVENLABS_API_KEY   required
  ROOK_VOICE_ID        required: the saved voice for Rook (made once in ElevenLabs Voice Design)
  ELEVENLABS_MODEL     optional, default eleven_flash_v2_5 (about half the credits per character
                       of the multilingual model). An 850-word Read is roughly 5,000 characters.

Usage:
  python3 -I tools/voice_read.py --dry-run            # print the script and its length; no API call
  python3 -I tools/voice_read.py                      # voice the newest cleared Read that has no audio
  python3 -I tools/voice_read.py 2026-11-04           # voice one Read by id
Only Reads that Mercer has CLEARED are voiced.
"""
import json, os, re, sys, urllib.request, urllib.error, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READS = ROOT / 'data' / 'reads.json'
SPOKEN_DISCLAIMER = ('This has been Rook\'s Read: analysis and opinion, for education only, and not investment advice. '
                     'Sources and Mercer\'s review are on the page at W V A I hub dot com.')

def script(r):
    day = dt.date.fromisoformat(r['d'])
    body = '\n\n'.join(re.sub(r'\s*\[\d+\]', '', p).strip() for p in r['body'])
    conflict = ' Rook runs on Claude, made by Anthropic, which is Monarch\'s anchor tenant.' if r.get('anthropic') else ''
    return f"Rook's Read for {day.strftime('%A, %B')} {day.day}. {r['title']}.\n\n{body}\n\n{SPOKEN_DISCLAIMER}{conflict}"

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    data = json.loads(READS.read_text())
    cleared = [r for r in data['reads'] if r.get('mercer', {}).get('status') == 'CLEARED']
    r = next((x for x in cleared if x['id'] == args[0]), None) if args else next((x for x in sorted(cleared, key=lambda x: x['d'], reverse=True) if not x.get('audio')), None)
    if not r: sys.exit('No cleared Read to voice (check the id, or every cleared Read already has audio).')
    text = script(r)
    model = os.environ.get('ELEVENLABS_MODEL', 'eleven_flash_v2_5')
    print(f'Read {r["id"]}: {len(text)} characters with model {model}.', file=sys.stderr)
    if dry:
        print(text); return
    key, voice = os.environ.get('ELEVENLABS_API_KEY'), os.environ.get('ROOK_VOICE_ID')
    if not key or not voice: sys.exit('Set ELEVENLABS_API_KEY and ROOK_VOICE_ID first.')
    req = urllib.request.Request(
        f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_64',
        data=json.dumps({'text': text, 'model_id': model}).encode(),
        headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=300) as resp: mp3 = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs returned {e.code}: {e.read()[:300]!r}')
    out = ROOT / 'audio' / 'rook' / f'{r["id"]}.mp3'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(mp3)
    r['audio'] = f'audio/rook/{r["id"]}.mp3'
    READS.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
    print(f'Wrote {out.relative_to(ROOT)} ({len(mp3) // 1024} KB) and set the Read\'s audio field.', file=sys.stderr)

if __name__ == '__main__':
    main()
