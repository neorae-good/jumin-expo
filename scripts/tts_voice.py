# Record the narration with any ElevenLabs voice, same "힘차게" settings as the approved test (2026-11-03):
# eleven_v4, "[energetic] " tag, stability 0.3, similarity 0.75, commas sent as "...", "!" sent as "."
# L15 (the slogan) is read without the tag (CALM text), as with Kanika: the tag made the slogan shout.
#
#   python scripts/tts_voice.py yohan 4JJwo477JUAx3HV0T7n7 all abc
#   python scripts/tts_voice.py david v1jVu1Ky28piIPEJqRrm L03,L08 de
#
# Takes go to narr/v8/<name>/<line><take>.mp3; existing files are skipped (safe to re-run after an interruption).
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ.get('ELEVENLABS_API_KEY') or sys.exit('set ELEVENLABS_API_KEY first')
name, voice = sys.argv[1], sys.argv[2]
only = None if sys.argv[3] == 'all' else sys.argv[3].split(',')
takes = sys.argv[4] if len(sys.argv) > 4 else 'abc'
CALM = {'L15': '주민의 하나된 힘으로, 경남이 힘차게 도약합니다.'}
lines = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))
out_dir = ROOT / 'narr' / 'v8' / name
out_dir.mkdir(parents=True, exist_ok=True)
for x in lines:
    if only and x['id'] not in only:
        continue
    if x['id'] in CALM:
        text = CALM[x['id']].replace(', ', '... ')
    else:
        text = '[energetic] ' + x.get('tts', x['text']).replace(', ', '... ').replace('!', '.')
    for k in takes:
        out = out_dir / f"{x['id']}{k}.mp3"
        if out.exists():
            print(out.name, 'exists'); continue
        body = json.dumps({'text': text, 'model_id': 'eleven_v4',
                           'voice_settings': {'stability': 0.3, 'similarity_boost': 0.75, 'speed': 1.1}}).encode('utf-8')
        for fmt in ('mp3_44100_192', 'mp3_44100_128'):
            req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format={fmt}',
                                         data=body, method='POST', headers={'xi-api-key': KEY, 'content-type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    out.write_bytes(r.read())
                print(out.name, 'ok', fmt); break
            except urllib.error.HTTPError as e:
                msg = e.read()[:300]
                if e.code == 403 and b'output_format_not_allowed' in msg:
                    continue
                sys.exit(f'{out.name} HTTP {e.code} {msg}')
