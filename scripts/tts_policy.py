# 생활공감정책 참여단 intro: "normal but with emphasis" narration (same calm pace, livelier stresses), 3 takes per line.
#   python scripts/tts_policy.py kyle RU7aSi6lT4uQBXMLgDxK   -> narr/policy/kyle/P01a.mp3 ...
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ['ELEVENLABS_API_KEY']
name, voice = sys.argv[1], sys.argv[2]
STYLE = {  # (cue, stability): lower stability = livelier stresses; no [energetic] (it speeds up and goes high)
    'P01': ('[warm] ', 0.4), 'P02': ('[warm] ', 0.38),
    'P03': ('[thoughtful] ', 0.38),            # the inner question
    'P04': ('[warm] ', 0.38), 'P05': ('[warm] ', 0.4),
    'P06': ('[warm][confident] ', 0.45),       # closing line: firm
}
PDIR = os.environ.get('PDIR', 'policy')   # PDIR=policy2: scene-2 history narration
out = ROOT / 'narr' / PDIR / name
out.mkdir(parents=True, exist_ok=True)
for x in json.load(open(ROOT / 'narr' / PDIR / 'script.json', encoding='utf-8')):
    tag, st = STYLE.get(x['id'], ('[warm][confident] ', 0.45) if x['id'] in ('Q10b', 'R08') else ('[warm] ', 0.4))
    text = tag + x['text'].replace('"', '')
    for k in 'abc':
        f = out / f"{x['id']}{k}.mp3"
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
