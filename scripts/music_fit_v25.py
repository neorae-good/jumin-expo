# v25: fit "Our Shared Neighborhood" to the film with a longer natural intro.
#   python scripts/music_fit_v25.py   -> audio/bgm_v25.wav
# 1) intro: the 2-bar ambient phrase before the bass (song 2.68-6.95 s) plays two extra times, so the song's own
#    bass entrance lands at ~17.3 s (title) and its drums at ~19.8 s (quilt world) - no instruments are removed.
# 2) body: whole bars repeated at the best-matching beat (harmony + timbre + loudness) so song 112.6 s -> film 133 s.
# 3) the song's last 45 s play untouched (natural ending).
import subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
BEAT = 0.534; BAR = 4 * BEAT
XF = int(0.06 * SR)
src = ROOT / 'scripts' / 'music_fit.py'
code = src.read_text().split("for k in (SONGS")[0]
ns = {'__file__': str(src)}
exec(code, ns)                                   # reuse load / env / feats / best_joint / xcat from music_fit.py
load, best_joint, xcat = ns['load'], ns['best_joint'], ns['xcat']

x = load(ROOT / 'audio' / 'src_v22_4_new.wav')
# 1) intro: [0, 6.95) + 2 x [2.68, 6.95) + [6.95, 11.22)
c_in = 6.95; blk0 = 6.95 - 2 * BAR
j = int(blk0 * SR); ic = int(c_in * SR)
out = x[:ic + XF]
for _ in range(2): out = xcat(out, x[j:ic + XF])
out = xcat(out, x[ic:int(11.22 * SR)])
print(f'intro: song drums 11.22 s -> film {len(out) / SR:.2f} s, bass 8.8 s -> film {8.8 + 4 * BAR:.2f} s')
# 2) body: song 11.22 -> 112.6 must fill film up to 133.0
s0, s1, t1 = 11.22, 112.6, 133.0
need = t1 - len(out) / SR - (s1 - s0)
n = int(round(need / BAR)); D = n * BAR
c, jj, q = best_joint(x, max(28.0 + D, s0 + D + 1.5), s1 - 1.5, D, BEAT)
print(f'body: +{n} bars at {c:.2f} s (match {q:.2f})')
icc = int(c * SR)
body = xcat(xcat(x[int(s0 * SR):icc + XF], x[jj:icc + XF]), x[icc:int(s1 * SR)])
out = xcat(out, body)
print(f'song 112.6 s lands at film {len(out) / SR:.2f} s (target 133.0)')
# 3) untouched ending
out = xcat(out, x[int(112.6 * SR):])
print(f'song end lands at film {len(out) / SR:.2f} s')
N = int(178.0 * SR)
out = out[:N]
if len(out) < N: out = np.pad(out, ((0, N - len(out)), (0, 0)))
with wave.open(str(ROOT / 'audio' / 'bgm_v25.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_v25.wav')
