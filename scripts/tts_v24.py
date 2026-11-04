# v24: narration with a designed intonation curve (calm opening -> lifted roll calls -> climax -> strongest slogan).
#   python scripts/tts_v24.py juan24 8lidWTlnwgjObqCImnE2
#   python scripts/tts_v24.py henry24 0emXFRrt8HxjqJpgeQtr
# Commas stay commas (fewer breaths), "!" is sent as "." (avoids shouting). 4 takes per line; existing files skipped.
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ['ELEVENLABS_API_KEY']
name, voice = sys.argv[1], sys.argv[2]
# (cue, stability) per line; plain lines get a lower stability for livelier natural intonation
STYLE = {
    'L01': ('[warm] ', 0.4), 'L02': ('[warm] ', 0.4),
    'LT':  ('[warm][proud] ', 0.45),                              # title: firm
    'L03': ('[warm][proud] ', 0.45), 'L08': ('[warm][proud] ', 0.45),  # roll calls: lifted
    'L12': ('[proud][excited] ', 0.45),                           # climax: strongest before the slogan
    'L13': ('[warm][proud] ', 0.5), 'L14': ('[warm][proud] ', 0.5),
    'L15': ('[proud] ', 0.45),                                    # slogan: strongest
}
PLAIN = ('', 0.35)
CALM = {'L15': '주민의 하나된 힘으로, 경남이 힘차게 도약합니다.'}
out = ROOT / 'narr' / 'v8' / name
out.mkdir(parents=True, exist_ok=True)
for x in json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8')):
    lid = x['id']
    tag, st = STYLE.get(lid, PLAIN)
    text = tag + CALM.get(lid, x.get('tts', x['text'])).replace('!', '.')
    for k in 'abcd':
        f = out / f'{lid}{k}.mp3'
        if f.exists(): continue
        body = json.dumps({'text': text, 'model_id': 'eleven_v4',
                           'voice_settings': {'stability': st, 'similarity_boost': 0.75, 'speed': 1.0}}).encode()
        r = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128',
                                   data=body, method='POST', headers={'xi-api-key': KEY, 'content-type': 'application/json'})
        try:
            f.write_bytes(urllib.request.urlopen(r, timeout=120).read())
        except urllib.error.HTTPError as e:
            sys.exit(f'{f.name} HTTP {e.code} {e.read()[:200]}')
print(name, 'done', len(list(out.glob('*.mp3'))))
