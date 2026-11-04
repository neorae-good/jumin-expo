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
    # v22b: the last 45 s of every song play untouched (natural ending, no joint after 2:13);
    # all lengthening/shortening happens in the body, never inside the intro (MINJ = earliest allowed repeat start)
    '1_sports': {'beat': 0.44776, 'minj': 34.0, 'anchors': [(0, 0), (103.0, 133.0), (147.96, 178.0)]},
    '2_dawn':   {'beat': 0.48387, 'minj': 20.0, 'anchors': [(0, 0), (92.6, 133.0), (137.6, 178.0)]},
    '3_folk':   {'beat': 0.46020, 'minj': 30.0, 'anchors': [(0, 0), (18.76, 19.0), (147.56, 133.0), (192.56, 178.0)]},
    # v24: "Our Shared Neighborhood" (Suno, 112 BPM, 157.6 s) for the Juan / Henry versions
    '4_new':    {'beat': 0.53400, 'minj': 28.0, 'anchors': [(0, 0), (112.6, 133.0), (157.6, 178.0)]},
}
XF = int(0.06 * SR)


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def env(a, hop=480):
    m = np.abs(a).mean(1); n = len(m) // hop
    return np.log(m[:n * hop].reshape(n, hop).mean(1) + 1e-5)


_FEAT = {}
def feats(x):
    """chroma (harmony) + MFCC (timbre) per frame, for judging whether two moments of the song can be joined"""
    k = id(x)
    if k not in _FEAT:
        import librosa
        y = x.mean(1)[::2].astype(np.float32); sr = SR // 2; hop = 512
        C = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
        M = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=20)[1:]
        C = C / (np.linalg.norm(C, axis=0) + 1e-9)
        M = (M - M.mean(1, keepdims=True)) / (M.std(1, keepdims=True) + 1e-9); M = M / (np.linalg.norm(M, axis=0) + 1e-9)
        _FEAT[k] = (C, M, sr / hop)
    return _FEAT[k]


def best_joint(x, lo, hi, D, beat):
    """beat-aligned point c in [lo, hi] where the song at c sounds like the song at c-D (same harmony and timbre,
    similar loudness), so jumping between them is not heard"""
    C, M, fr = feats(x)
    best, bc, w = -9, None, int(1.0 * SR)
    n = int(1.5 * fr)
    for c in np.arange(lo, hi, beat):
        i, j = int(c * SR), int((c - D) * SR)
        a, b = int(c * fr), int((c - D) * fr)
        if j - w < 0 or i + w > len(x) or b - n < 0 or a + n > C.shape[1]: continue
        h = 0.5 * (C[:, a - n:a + n] * C[:, b - n:b + n]).sum(0).mean() + 0.5 * (M[:, a - n:a + n] * M[:, b - n:b + n]).sum(0).mean()
        e = np.corrcoef(env(x[i - w:i + w]), env(x[j - w:j + w]))[0, 1]
        r = 0.7 * h + 0.3 * e
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
    cfg = SONGS[key]; beat = cfg['beat']; bar = 4 * beat; minj = cfg['minj']
    x = load(ROOT / 'audio' / f'src_v22_{key}.wav')
    out, err, log = None, 0.0, []
    A = cfg['anchors']
    for (s0, t0), (s1, t1) in zip(A, A[1:]):
        delta = (t1 - t0) - (s1 - s0) - err
        n = int(round(delta / bar))
        edits = []                                  # (c, j, D, reps) in song samples; reps=0 means cut
        if n != 0 and (s1 - s0) > 20:
            parts = []
            if n > 0:
                big = 8 if n >= 8 else (4 if n >= 4 else n)
                r = min(2, n // big); parts.append((big, r)); rem = n - big * r
                if rem: parts.append((rem, 1))
            else:
                parts.append((-n, 0))
            used = []
            for nb, r in parts:
                D = nb * bar
                lo, hi = max(s0 + D + 1.5, minj + D), s1 - 1.5
                best = (-9, None, None)
                for c in np.arange(lo, hi, beat):
                    if any(abs(c - u) < D + 6 for u in used): continue
                    cc, jj, q = best_joint(x, c, c + beat * 0.5, D, beat)
                    if cc is not None and q > best[0]: best = (q, cc, jj)
                q, c, j = best
                if c is None: log.append(f'  no joint for {nb} bars'); continue
                used.append(c); edits.append((int(c * SR), j, int(D * SR), r))
                log.append(f'{s0:6.1f}-{s1:6.1f}s: {"+" if r else "-"}{nb * max(r, 1)} bars ({max(r,1)}x{nb}) at {c:6.2f}s match {q:.2f}')
        seg, pos = None, int(s0 * SR)
        for c, j, D, r in sorted(edits):
            if r:
                piece = x[pos:c + XF]; seg = piece if seg is None else xcat(seg, piece)
                for _ in range(r): seg = xcat(seg, x[j:c + XF])
                pos = c
            else:
                piece = x[pos:j + XF]; seg = piece if seg is None else xcat(seg, piece)
                pos = c
        tail = x[pos:int(s1 * SR)]
        seg = tail if seg is None else xcat(seg, np.concatenate([x[pos - XF:pos], tail]) if False else tail)
        if not edits: log.append(f'{s0:6.1f}-{s1:6.1f}s: unchanged')
        out = seg if out is None else xcat(out, seg)
        err = len(out) / SR - t1
        log.append(f'   -> song {s1:.2f}s lands at {len(out) / SR:.2f}s (film {t1}s, off {err:+.2f}s)')
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
