# v20: faster background music without moving the musical hits off the picture.
#
#   python scripts/music_fast.py            -> audio/bgm4_fast.wav (178 s)
#
# bgm3.wav (116 bpm) is cut at its section changes (ANCHORS, kept at the same seconds as before).
# Inside each section a few whole bars are repeated once, then the section is sped up
# (rubberband, pitch kept) back to its original length. So every section plays ~13-16 % faster
# (about 132 bpm) while the drops at 27.7 / 74.2 / 83.6 / 150 s still land where the picture expects them.
# The quiet thread close-up (74.2-83.6 s) is left untouched.
import subprocess, sys, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
BEAT = 0.51725                # measured (16/32/64-beat autocorrelation of the onset envelope)
BAR = 4 * BEAT
# (start, end, bars to repeat)
SECTIONS = [(0.0, 27.7, 2), (27.7, 74.15, 3), (74.15, 83.6, 0), (83.6, 150.0, 5), (150.0, 178.0, 2)]
XF = int(0.08 * SR)           # crossfade at the repeat joint
SEAM = int(0.03 * SR)         # crossfade between sections


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def stretch(a, tempo):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                        '-af', f'rubberband=tempo={tempo:.6f}:pitchq=quality:transients=mixed:detector=compound',
                        '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-'], input=a.astype(np.float32).tobytes(),
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).reshape(-1, 2).copy()


def env(a, hop=480):
    m = np.abs(a).mean(1)
    n = len(m) // hop
    return np.log(m[:n * hop].reshape(n, hop).mean(1) + 1e-5)


def best_joint(x, a, b, D):
    """pick a cut c in (a+D, b) where the audio at c matches the audio one repeat earlier (c-D)."""
    best, bc = -9, None
    w = int(1.0 * SR)
    for c in np.arange(a + D + 1.5, max(a + D + 2.0, a + 0.6 * (b - a)), BEAT / 2):  # first 60 %: never inside a fade-out
        i, j = int(c * SR), int((c - D) * SR)
        e1, e2 = env(x[i - w:i + w]), env(x[j - w:j + w])
        r = np.corrcoef(e1, e2)[0, 1]
        if r > best:
            best, bc = r, c
    # fine-align the jump target by waveform correlation (+-15 ms)
    i = int(bc * SR)
    ref = x[i:i + int(0.25 * SR)].mean(1)
    lags = range(-int(0.015 * SR), int(0.015 * SR) + 1, 4)
    sc = [np.dot(ref, x[int((bc - D) * SR) + l:int((bc - D) * SR) + l + len(ref)].mean(1)) for l in lags]
    return bc, int((bc - D) * SR) + list(lags)[int(np.argmax(sc))], best


x = load(ROOT / 'audio' / 'bgm3.wav')
N = int(178.0 * SR)
x = np.pad(x, ((0, max(0, N + SR - len(x))), (0, 0)))
out = np.zeros((N, 2), np.float32)
fade = np.linspace(0, 1, XF, dtype=np.float32)[:, None]
for a, b, nb in SECTIONS:
    i0, i1 = int(a * SR), int(b * SR)
    pad = SEAM
    if nb == 0:
        seg = x[i0:i1 + pad]
    else:
        D = nb * BAR
        c, j, r = best_joint(x, a, b, D)
        ic = int(c * SR)
        head = x[i0:ic + XF].copy()
        rep = x[j:ic].copy()                      # one repeat: c-D .. c
        tail = x[ic:i1 + pad].copy()
        # head -> rep joint (crossfade over XF)
        body = np.concatenate([head[:-XF], head[-XF:] * (1 - fade) + rep[:XF] * fade, rep[XF:], tail])
        seg = stretch(body, len(body) / (i1 - i0 + pad))
        print(f'{a:6.1f}-{b:6.1f}s  repeat {nb} bar(s) at {c:6.2f}s (match {r:.2f})  tempo x{len(body) / (i1 - i0 + pad):.3f}')
    seg = seg[:i1 - i0 + pad]
    seg = np.pad(seg, ((0, i1 - i0 + pad - len(seg)), (0, 0)))
    out[i0:i1] = seg[:i1 - i0]
    if i0 > 0:
        # the previous section ran SEAM samples past its end: crossfade it into this section's start
        sf = np.linspace(0, 1, SEAM, dtype=np.float32)[:, None]
        out[i0:i0 + SEAM] = prev_tail * (1 - sf) + seg[:SEAM] * sf
    prev_tail = seg[i1 - i0:i1 - i0 + SEAM]
# the old track's last-3-second fade is preserved because the outro section ends at 178 s
dst = ROOT / 'audio' / 'bgm4_fast.wav'
with wave.open(str(dst), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok', dst)
