# Check that every narration line is understandable in a finished mix (music included):
# transcribe each line's window with faster-whisper (medium) and compare with narr/script6.json.
#
#   python scripts/stt_check.py audio/master_mix9_less.wav
#
# Known transcription quirks that are NOT errors: "첫 땀"->"첫담", "바꿉니다"->"바꾭니다",
# "함안"->"하만" (same pronunciation), numbers written as "18".
import difflib, json, subprocess, sys
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
mix = Path(sys.argv[1]).resolve()
voice = sys.argv[2] if len(sys.argv) > 2 else 'kanika'
lines = None
norm = lambda s: ''.join(c for c in s if c.isalnum())
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)

# optional per-variant start times (e.g. NARR_T=narr/t_m.json for 3안, where L01/L02 follow the title card)
def _narr_lines(path):
    import json as _j, os as _o
    L = _j.load(open(path, encoding='utf-8'))
    if _o.environ.get('NARR_T'):
        o = _j.load(open(_o.path.join(R if 'R' in globals() else str(ROOT), _o.environ['NARR_T']), encoding='utf-8'))
        for x in L:
            if x['id'] in o: x['t'] = o[x['id']]
    return L
lines = _narr_lines(ROOT / 'narr' / 'script6.json')
model = WhisperModel('medium', device='cpu', compute_type='int8')
tmp = ROOT / 'audio' / '_stt_window.wav'
for x in lines:
    d = dur(ROOT / 'narr' / 'v8p' / voice / f"{x['id']}.wav")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(x['t'] - 0.2), '-t', str(d + 0.6), '-i', str(mix),
                    '-vn', '-ac', '1', '-ar', '16000', str(tmp)], check=True)
    text = ''.join(s.text for s in model.transcribe(str(tmp), language='ko', beam_size=5)[0]).strip()
    r = difflib.SequenceMatcher(None, norm(x.get('tts', x['text'])), norm(text)).ratio()
    print(f"{x['id']} {r:.2f} {text}")
tmp.unlink(missing_ok=True)
