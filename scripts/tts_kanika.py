# Record narration with the chosen voice: ElevenLabs "Kanika" (p9aflnsbBe1o0aDeQa97), model eleven_v4.
# Needs your own ElevenLabs API key in the environment variable ELEVENLABS_API_KEY.
# If the API says the voice is not found, add it once in ElevenLabs > Voice Library ("Add to My Voices").
#
#   python scripts/tts_kanika.py all abc            all 15 lines, takes a/b/c at speed 0.88
#   python scripts/tts_kanika.py L02,L07 de 0.82    re-record rushed lines a little slower
#   python scripts/tts_kanika.py L15 de 0.85        the slogan (read calmly, see CALM)
#   python scripts/tts_kanika.py all fgh 1.05 0.3   faster, more energetic reading (4th argument = stability)
#   python scripts/tts_kanika.py all fgh 1.1 0.3 energetic   v20: 5th argument = eleven_v4 audio tag sent as "[energetic] ..."
#
# NOTE (2026-11-02): eleven_v4 ignores voice_settings.speed (0.7 and 1.2 give the same length).
# The v20 reading is made faster and stronger with the v4 audio tag [energetic] + stability 0.3
# (about 12-14 % shorter than v19). The tag itself is not read aloud (checked with faster-whisper).
#
# Takes go to narr/v8/kanika/<line><take>.mp3 (existing files are skipped).
# Rules learned with the reviewer:
# - commas are sent as "..." so the voice breathes there; never time-stretch afterwards (it sounded mechanical)
# - "!" made the voice shout (+7-10 semitones), so the slogan is read with ", ." while the caption keeps "!"
# - TTS text can differ from the caption: "18개" is read "열여덟 개" (field "tts" in narr/script6.json)
import json, os, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ.get('ELEVENLABS_API_KEY') or sys.exit('set ELEVENLABS_API_KEY first')
VOICE = 'p9aflnsbBe1o0aDeQa97'
CALM = {'L15': '주민의 하나된 힘으로, 경남이 힘차게 도약합니다.'}

lines = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))
only = None if sys.argv[1] == 'all' else sys.argv[1].split(',')
takes = sys.argv[2] if len(sys.argv) > 2 else 'abc'
speed = float(sys.argv[3]) if len(sys.argv) > 3 else 0.88
stability = float(sys.argv[4]) if len(sys.argv) > 4 else 0.4
tag = f'[{sys.argv[5]}] ' if len(sys.argv) > 5 else ''
out_dir = ROOT / 'narr' / 'v8' / 'kanika'
out_dir.mkdir(parents=True, exist_ok=True)
for x in lines:
    if only and x['id'] not in only:
        continue
    text = tag + CALM.get(x['id'], x.get('tts', x['text'])).replace(', ', '... ')
    for k in takes:
        out = out_dir / f"{x['id']}{k}.mp3"
        if out.exists():
            print(out.name, 'exists'); continue
        body = json.dumps({'text': text, 'model_id': 'eleven_v4',
                           'voice_settings': {'stability': stability, 'similarity_boost': 0.75, 'speed': speed}}).encode('utf-8')
        # 192 kbps needs the Creator tier; fall back to 128 kbps on lower plans
        for fmt in ('mp3_44100_192', 'mp3_44100_128'):
            req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format={fmt}',
                                         data=body, method='POST', headers={'xi-api-key': KEY, 'content-type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    out.write_bytes(r.read())
                print(out.name, 'ok', fmt)
                break
            except urllib.error.HTTPError as e:
                msg = e.read()[:300]
                if e.code == 403 and b'output_format_not_allowed' in msg:
                    continue
                sys.exit(f'{out.name} HTTP {e.code} {msg}')
