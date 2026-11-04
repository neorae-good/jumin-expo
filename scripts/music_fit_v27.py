# v27: fit "Shared Dreams" (Suno, ~114 BPM, 152.8 s) so its own quiet spots land on the producer's timeline.
#   python scripts/music_fit_v27.py   -> audio/bgm_v27.wav
#   song 0-83.5 s plays as is (calm intro until 17.5 s, its own dip at ~80-84 s sits at the thread close-up)
#   song 83.5-119.8 s + 5 repeated bars -> film 83.3-130 s; the song's short break 119.8-122.9 s -> film 2:10-2:13
#   song 122.9-132.4 s climax, then an earlier climax phrase (song ~100-119 s) is inserted -> film 2:13-2:41
#   song 132.4 s outro -> film ~2:41-2:42; last part fades at 2:58
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
BEAT = 0.52566; BAR = 4 * BEAT
src = ROOT / 'scripts' / 'music_fit.py'
ns = {'__file__': str(src)}
exec(src.read_text().split("for k in (SONGS")[0], ns)
load, best_joint, xcat, feats, env = ns['load'], ns['best_joint'], ns['xcat'], ns['feats'], ns['env']
XF = int(0.06 * SR)
x = load(ROOT / 'audio' / 'src_v22_5_dreams.wav')
C, M, fr = feats(x)


def sim(a, b):
    """how alike the song sounds around second a and second b (harmony, timbre, loudness)"""
    n = int(1.5 * fr); i, j = int(a * fr), int(b * fr)
    h = 0.5 * (C[:, i - n:i + n] * C[:, j - n:j + n]).sum(0).mean() + 0.5 * (M[:, i - n:i + n] * M[:, j - n:j + n]).sum(0).mean()
    w = int(SR); e = np.corrcoef(env(x[int(a * SR) - w:int(a * SR) + w]), env(x[int(b * SR) - w:int(b * SR) + w]))[0, 1]
    return 0.7 * h + 0.3 * e


S = lambda a, b: x[int(a * SR):int(b * SR) + XF]
# part 1: as is up to 83.5 s
out = x[:int(83.5 * SR) + XF]
# part 2: 83.5 -> 119.8 with +5 bars repeated at the best point
D = 5 * BAR
c, j, q = best_joint(x, 83.5 + D + 1.5, 118.5, D, BEAT)
out = xcat(out, x[int(83.5 * SR):int(c * SR) + XF]); out = xcat(out, x[j:int(c * SR) + XF]); out = xcat(out, x[int(c * SR):int(119.8 * SR) + XF])
print(f'part2: +5 bars at {c:.2f}s (match {q:.2f}); song 119.8 s lands at {len(out) / SR:.2f} s (target 130.0)')
# part 3: the break 119.8-122.9 and the climax 122.9-132.4
out = xcat(out, x[int(119.8 * SR):int(132.4 * SR) + XF])
t_out = len(out) / SR
# part 4: insert an earlier climax phrase [p, p+L) so the outro (song 132.4 s) starts near film 161.4 s
# the climax's last 4 bars play two extra times (keeps the energy up for 2:13-2:42; best-matching loop point)
D = 4 * BAR
c4, j4, q4 = best_joint(x, 122.9 + D + 0.5, 132.4, D, BEAT)
out = out[:len(out) - int((132.4 - c4) * SR) - XF] if c4 < 132.4 else out
out = out[:int(len(out))]
for _ in range(2): out = xcat(out, x[j4:int(c4 * SR) + XF])
out = xcat(out, x[int(c4 * SR):int(132.4 * SR) + XF])
print(f'part4: climax 4 bars x2 looped at {c4:.2f}s (match {q4:.2f}); outro starts at film {len(out) / SR:.2f} s')
out = xcat(out, x[int(132.4 * SR):])
print(f'song end lands at film {len(out) / SR:.2f} s')
N = int(178.0 * SR)
out = out[:N]
if len(out) < N: out = np.pad(out, ((0, N - len(out)), (0, 0)))
with wave.open(str(ROOT / 'audio' / 'bgm_v27.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_v27.wav')
