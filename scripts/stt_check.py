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
lines = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))
norm = lambda s: ''.join(c for c in s if c.isalnum())
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
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
