# v23: Juan, average pace. Plain lines: no tag, stability 0.5, 3 takes. Accent lines: light emphasis cue, 4 takes.
# Commas are sent as commas (the "..." trick made ElevenLabs insert breaths); "!" is sent as "." (it made voices shout).
import json, os, sys, urllib.error, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ['ELEVENLABS_API_KEY']; VID = '8lidWTlnwgjObqCImnE2'
ACCENT = {'L03': '[confident] ', 'L08': '[confident] ', 'L12': '[confident] ', 'LT': '[confident] ', 'L15': '[powerful] '}
CALM = {'L15': '주민의 하나된 힘으로, 경남이 힘차게 도약합니다.'}
out = ROOT / 'narr' / 'v8' / 'juan'; out.mkdir(parents=True, exist_ok=True)
for x in json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8')):
    lid = x['id']
    base = CALM.get(lid, x.get('tts', x['text'])).replace('!', '.')
    jobs = [('', 0.5, 'abc')] if lid not in ACCENT else [(ACCENT[lid], 0.5, 'abcd')]
    for tag, st, takes in jobs:
        for k in takes:
            f = out / f'{lid}{k}.mp3'
            if f.exists(): continue
            body = json.dumps({'text': tag + base, 'model_id': 'eleven_v4', 'voice_settings': {'stability': st, 'similarity_boost': 0.75, 'speed': 1.0}}).encode()
            r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VID}?output_format=mp3_44100_128', data=body, method='POST',
                                       headers={'xi-api-key': KEY, 'content-type': 'application/json'})
            try: f.write_bytes(urllib.request.urlopen(r, timeout=120).read())
            except urllib.error.HTTPError as e: sys.exit(f'{f.name} HTTP {e.code} {e.read()[:200]}')
print('done', len(list(out.glob('*.mp3'))))
