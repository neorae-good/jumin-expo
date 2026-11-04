# v25 recordings (ElevenLabs eleven_v4; commas kept, "!" sent as "."; existing files skipped).
#   python scripts/tts_v25.py strong juanS 8lidWTlnwgjObqCImnE2      "힘찬": same pace, more force (3 takes)
#   python scripts/tts_v25.py title  juan24 8lidWTlnwgjObqCImnE2     stronger 15 s title into an existing voice dir
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ['ELEVENLABS_API_KEY']
mode, name, voice = sys.argv[1], sys.argv[2], sys.argv[3]
CALM = {'L15': '주민의 하나된 힘으로, 경남이 힘차게 도약합니다.'}
STRONG = {  # no [energetic] (it speeds the reading up); force comes from confident/proud cues
    'L01': ('[warm][confident] ', 0.4), 'L02': ('[warm][confident] ', 0.4),
    'LT': ('[proud][confident] ', 0.35),
    'L03': ('[proud][confident] ', 0.4), 'L08': ('[proud][confident] ', 0.4),
    'L12': ('[proud][confident] ', 0.35), 'L13': ('[proud][confident] ', 0.4), 'L14': ('[proud][confident] ', 0.4),
    'L15': ('[proud][powerful] ', 0.4),
}
STRONG_PLAIN = ('[confident] ', 0.4)
TITLE = [('[proud][confident] ', 0.35, 'ef'), ('[confident][emphatic] ', 0.4, 'gh')]


def tts(text, st, f):
    if f.exists(): return
    body = json.dumps({'text': text, 'model_id': 'eleven_v4',
                       'voice_settings': {'stability': st, 'similarity_boost': 0.75, 'speed': 1.0}}).encode()
    r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128',
                               data=body, method='POST', headers={'xi-api-key': KEY, 'content-type': 'application/json'})
    try:
        f.write_bytes(urllib.request.urlopen(r, timeout=120).read())
    except urllib.error.HTTPError as e:
        sys.exit(f'{f.name} HTTP {e.code} {e.read()[:200]}')


out = ROOT / 'narr' / 'v8' / name; out.mkdir(parents=True, exist_ok=True)
lines = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))
if mode == 'title':
    for cue, st, takes in TITLE:
        for k in takes: tts(cue + '한 조각씩, 하나의 천으로.', st, out / f'LT{k}.mp3')
else:
    for x in lines:
        cue, st = STRONG.get(x['id'], STRONG_PLAIN)
        text = cue + CALM.get(x['id'], x.get('tts', x['text'])).replace('!', '.')
        for k in 'abc': tts(text, st, out / f"{x['id']}{k}.mp3")
print(mode, name, 'done', len(list(out.glob('*.mp3'))))
