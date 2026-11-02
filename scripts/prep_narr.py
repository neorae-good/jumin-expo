# Turn the chosen takes (narr/v8/picks.json) into the trimmed WAVs that build8.py and mix9.py read:
# narr/v8p/<voice>/Lxx.wav. Only edge silence is trimmed; speech is never time-stretched.
# Prints how much room each line leaves before the next one starts (keep it >= ~1 s).
#
#   python scripts/prep_narr.py            (voice kanika)
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
voice = sys.argv[1] if len(sys.argv) > 1 else 'kanika'
picks = json.load(open(ROOT / 'narr' / 'v8' / 'picks.json'))[voice]
lines = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))
AF = ('silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04,areverse,'
      'silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.08,areverse')
out_dir = ROOT / 'narr' / 'v8p' / voice
out_dir.mkdir(parents=True, exist_ok=True)
for i, x in enumerate(lines):
    src = ROOT / 'narr' / 'v8' / voice / f"{x['id']}{picks[x['id']]}.mp3"
    out = out_dir / f"{x['id']}.wav"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', AF, '-ar', '44100', str(out)], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out)],
                             capture_output=True, text=True).stdout)
    nxt = lines[i + 1]['t'] if i + 1 < len(lines) else 178
    gap = nxt - (x['t'] + d)
    print(f"{x['id']} take {picks[x['id']]} start {x['t']:6.1f}s length {d:4.1f}s room before next {gap:5.1f}s{'  <-- too tight' if gap < 1 else ''}")
