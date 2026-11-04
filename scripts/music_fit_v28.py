# v28: "Shared Dreams" lengthened with ONE edit only: the song plays in its own order, and right after its short
# break (~2:00) one whole chorus (a full section, start to end) comes back once, then the song's own climax and
# outro follow. The two cut points are chosen like a DJ jump: what is heard after each jump must sound like what the
# song itself would have played there, before AND after the cut. Equal-power 0.25 s crossfades.
#   python scripts/music_fit_v28.py   -> audio/bgm_v28.wav
import wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
src = ROOT / 'scripts' / 'music_fit.py'
ns = {'__file__': str(src)}
exec(src.read_text().split("for k in (SONGS")[0], ns)
load, feats, env = ns['load'], ns['feats'], ns['env']
x = load(ROOT / 'audio' / 'src_v22_5_dreams.wav')
C, M, fr = feats(x)
BEAT = 0.52566


def sim_win(a, b, w):
    """similarity of the w seconds starting at a and at b (negative w = the w seconds before)"""
    n = int(abs(w) * fr)
    if w > 0: i0, j0 = int(a * fr), int(b * fr)
    else: i0, j0 = int(a * fr) - n, int(b * fr) - n
    i1, j1 = i0 + n, j0 + n
    h = 0.5 * (C[:, i0:i1] * C[:, j0:j1]).sum(0).mean() + 0.5 * (M[:, i0:i1] * M[:, j0:j1]).sum(0).mean()
    e = np.corrcoef(env(x[int(min(a, a + w) * SR):int(max(a, a + w) * SR)]), env(x[int(min(b, b + w) * SR):int(max(b, b + w) * SR)]))[0, 1]
    return 0.7 * h + 0.3 * e


def jump_score(frm, to):
    """jumping from song time `frm` to song time `to`: before the cut we hear x[..frm], after it x[to..].
    Natural if x[to..] sounds like x[frm..] (what would have followed) and x[..frm] like x[..to]."""
    return 0.5 * (sim_win(frm, to, 2.0) + sim_win(frm, to, -2.0))


best = None
for a in np.arange(121.6, 124.4, BEAT / 2):          # exit of the break (song's own restart ~122.9 s)
    for b0 in np.arange(52.0, 55.5, BEAT / 2):        # start of the returning chorus (~53.5 s)
        j1 = jump_score(a, b0)
        for b1 in np.arange(b0 + 23.0, min(b0 + 28.0, 80.4), BEAT / 2):   # whole chorus, ends near its own end (~79.9 s)
            j2 = jump_score(b1, a)
            s = min(j1, j2)
            if best is None or s > best[0]: best = (s, a, b0, b1, j1, j2)
s, a, b0, b1, j1, j2 = best
print(f'jump 1: song {a:.2f} s -> {b0:.2f} s  naturalness {j1:.2f}')
print(f'jump 2: song {b1:.2f} s -> {a:.2f} s  naturalness {j2:.2f}')
# reference: how the earlier failed joints score with the same measure
for frm, to, tag in [(64.56, 83.5, 'v27 1:34'), (52.98, 122.9, 'v27 2:32'), (132.34, 132.34 - 4 * 4 * BEAT / 4 * 4 / 4 * 1, 'loop')]:
    try: print(f'  (reference {tag}: {jump_score(frm, to):.2f})')
    except Exception: pass
XF = int(0.25 * SR)


def join(p, q):
    t = np.linspace(0, np.pi / 2, XF, dtype=np.float32)[:, None]
    return np.concatenate([p[:-XF], p[-XF:] * np.cos(t) + q[:XF] * np.sin(t), q[XF:]])


h = XF // 2
out = x[:int(a * SR) + h]
out = join(out, x[int(b0 * SR) - h:int(b1 * SR) + h])
out = join(out, x[int(a * SR) - h:])
print(f'film: break at {119.8:.1f}-{a:.1f} s, chorus returns {a:.1f}-{a + b1 - b0:.1f} s, '
      f'song climax from {a + b1 - b0:.1f} s, outro (song 132.4) at {132.4 + b1 - b0:.1f} s, end {len(out) / SR:.1f} s')
N = int(178.0 * SR)
out = out[:N]
if len(out) < N: out = np.pad(out, ((0, N - len(out)), (0, 0)))
with wave.open(str(ROOT / 'audio' / 'bgm_v28.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_v28.wav')
