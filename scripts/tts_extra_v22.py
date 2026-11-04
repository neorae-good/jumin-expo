# v22b: title read at 15 s ("한 조각씩, 하나의 천으로", no caption) and a stronger final slogan (L15), all three male voices.
# Two delivery variants x 2 takes each; files go to narr/v22b/<voice>_<line>_<variant><take>.mp3 (existing files skipped).
import json, os, sys, urllib.error, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ['ELEVENLABS_API_KEY']
V = {'yohan': '4JJwo477JUAx3HV0T7n7', 'dennis': 'KlgjGxt7IJPLKAwBQbVn', 'david': 'v1jVu1Ky28piIPEJqRrm'}
JOBS = {
    'LT':  {'p': ('[proud] 한 조각씩... 하나의 천으로.', 0.45), 'q': ('[slowly, with gravitas] 한 조각씩... 하나의 천으로.', 0.5)},
    'L15': {'p': ('[powerful] 주민의 하나된 힘으로... 경남이 힘차게 도약합니다.', 0.4), 'q': ('[energetic] 주민의 하나된 힘으로... 경남이 힘차게, 도약합니다.', 0.45)},
}
out = ROOT / 'narr' / 'v22b'
for vn, vid in V.items():
    for lid, vs in JOBS.items():
        for var, (text, st) in vs.items():
            for k in 'ab':
                f = out / f'{vn}_{lid}_{var}{k}.mp3'
                if f.exists(): continue
                body = json.dumps({'text': text, 'model_id': 'eleven_v4', 'voice_settings': {'stability': st, 'similarity_boost': 0.75, 'speed': 1.0}}).encode()
                r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128', data=body, method='POST',
                                           headers={'xi-api-key': KEY, 'content-type': 'application/json'})
                try:
                    f.write_bytes(urllib.request.urlopen(r, timeout=120).read()); print(f.name, 'ok')
                except urllib.error.HTTPError as e:
                    sys.exit(f'{f.name} HTTP {e.code} {e.read()[:200]}')
