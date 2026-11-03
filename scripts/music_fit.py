# Fit a Suno track to the 178 s film without time-stretching: whole bars are repeated or cut at
# beat-aligned points where the music matches itself, so chosen song moments land on picture moments.
#
#   python scripts/music_fit.py 1_sports      -> audio/bgm_v22_1_sports.wav
#   python scripts/music_fit.py all
#
# ANCHORS: (song second, film second). Between two anchors the song is lengthened (repeat n bars once or
# several times) or shortened (cut n bars) so the next anchor lands within half a bar of its film time.
# Joints sit on beats where the loudness pattern of the two sides matches best; 60 ms crossfades.
import json, subprocess, sys, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
TOTAL = 178.0
SONGS = {
    # beat = measured (16/32-beat onset autocorrelation); anchors chosen from section boundaries
    '1_sports': {'beat': 0.44776, 'anchors': [(0, 0), (123.44, 139.2), (147.96, 178.0)]},
    '2_dawn':   {'beat': 0.48387, 'anchors': [(0, 0), (48.2, 70.0), (96.57, 139.2), (137.6, 178.0)]},
    '3_folk':   {'beat': 0.46020, 'anchors': [(0, 0), (18.76, 19.0), (149.0, 139.2), (192.56, 178.0)]},
}
XF = int(0.06 * SR)


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def env(a, hop=480):
    m = np.abs(a).mean(1); n = len(m) // hop
    return np.log(m[:n * hop].reshape(n, hop).mean(1) + 1e-5)


def best_joint(x, lo, hi, D, beat):
    """beat-aligned point c in [lo, hi] where audio at c matches audio at c-D (jump c-D <-> c is seamless)"""
    best, bc, w = -9, None, int(1.0 * SR)
    for c in np.arange(lo, hi, beat):
        i, j = int(c * SR), int((c - D) * SR)
        if j - w < 0 or i + w > len(x): continue
        r = np.corrcoef(env(x[i - w:i + w]), env(x[j - w:j + w]))[0, 1]
        if r > best: best, bc = r, c
    if bc is None: return None, None, -9
    i = int(bc * SR); ref = x[i:i + int(0.25 * SR)].mean(1)
    lags = list(range(-int(0.015 * SR), int(0.015 * SR) + 1, 4))
    sc = [np.dot(ref, x[int((bc - D) * SR) + l:int((bc - D) * SR) + l + len(ref)].mean(1)) for l in lags]
    return bc, int((bc - D) * SR) + lags[int(np.argmax(sc))], best


def xcat(a, b):
    f = np.linspace(0, 1, XF, dtype=np.float32)[:, None]
    return np.concatenate([a[:-XF], a[-XF:] * (1 - f) + b[:XF] * f, b[XF:]])


def fit(key):
    cfg = SONGS[key]; beat = cfg['beat']; bar = 4 * beat
    x = load(ROOT / 'audio' / f'src_v22_{key}.wav')
    out = x[:1].copy() * 0; err = 0.0; log = []
    A = cfg['anchors']
    for (s0, t0), (s1, t1) in zip(A, A[1:]):
        seg = x[int(s0 * SR):int(s1 * SR)].copy()
        delta = (t1 - t0) - (s1 - s0) - err
        n = int(round(delta / bar))
        if n > 0:
            # repeat a block of nb bars r times (largest block that still fits the segment)
            # whole phrases only (8/4/2 bars), at most 3 repeats; what is left over is carried to the next segment
            cands = [(abs(n - nb * r) + 0.4 * (r - 1) + (0.2 if nb == 2 else 0) + (0.3 if nb == 1 else 0), nb, r)
                     for nb in (8, 4, 2, 1) for r in ((1,) if nb == 1 else (1, 2, 3)) if nb * bar < (s1 - s0) - 4]
            _, nb, r = min(cands); n = nb * r; D = nb * bar
            c, j, q = best_joint(x, s0 + D + 1.5, s1 - 1.0, D, beat)
            if c is None: n = 0
            else:
                ic = int(c * SR)
                head, block, tail = x[int(s0 * SR):ic + XF], x[j:ic + XF], x[ic:int(s1 * SR)]
                body = head
                for _ in range(r): body = xcat(body, block)
                body = xcat(body, np.concatenate([x[ic - XF:ic], tail]) if False else tail)
                seg = body
                log.append(f'{s0:6.1f}-{s1:6.1f}s: +{n} bars ({r}x{nb}) at {c:6.2f}s match {q:.2f}')
        elif n < 0:
            D = -n * bar
            c, j, q = best_joint(x, s0 + D + 1.5, s1 - 1.0, D, beat)
            if c is None: n = 0
            else:
                # play up to the matching point before c, then continue from c (D seconds skipped)
                ic = int(c * SR)
                seg = xcat(x[int(s0 * SR):j + XF], x[ic:int(s1 * SR)])
                log.append(f'{s0:6.1f}-{s1:6.1f}s: -{-n} bars at {c:6.2f}s match {q:.2f}')
        else:
            log.append(f'{s0:6.1f}-{s1:6.1f}s: unchanged')
        out = seg if len(out) <= 1 else xcat(out, seg)
        err = len(out) / SR - t1
        log.append(f'   -> anchor song {s1:.2f}s lands at {len(out) / SR:.2f}s (film {t1}s, off {err:+.2f}s)')
    N = int(TOTAL * SR)
    out = out[:N]
    if len(out) < N: out = np.pad(out, ((0, N - len(out)), (0, 0)))
    fade = int(2.5 * SR); out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)[:, None] ** 1.5
    dst = ROOT / 'audio' / f'bgm_v22_{key}.wav'
    with wave.open(str(dst), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f'== {key}\n' + '\n'.join(log) + f'\n   wrote {dst.name}')


for k in (SONGS if sys.argv[1] == 'all' else [sys.argv[1]]):
    fit(k)
