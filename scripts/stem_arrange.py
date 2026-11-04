# v24: scene-aware arrangement from Demucs stems (htdemucs: drums / bass / other / vocals) of the fitted song.
#   python -m demucs -n htdemucs -d cpu -o audio/stems audio/bgm_v22_4_new.wav
#   python scripts/stem_arrange.py            -> audio/bgm_v24_arr.wav
# Each stem follows gain keyframes (film seconds, dB; -60 = off) with smooth cosine ramps between them.
import subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
STEMS = ROOT / 'audio' / 'stems' / 'htdemucs' / 'bgm_v22_4_new'
OFF = -60
KEYS = {
    # dawn + sweat drop (L01, L02): melody only, a little lower; title (15.2 s) opens up; quilt world (19 s) full band
    # thread close-up (74.6-83.3 s): drums and bass rest; second half (83.3 s) everything back
    'drums':  [(0, OFF), (18.3, OFF), (19.0, 0), (74.6, 0), (75.8, OFF), (82.9, OFF), (83.3, 0)],
    'bass':   [(0, OFF), (15.2, OFF), (19.0, 0), (74.6, 0), (76.0, OFF), (82.9, OFF), (83.3, 0)],
    'other':  [(0, -4), (15.2, -4), (17.5, 0)],
    'vocals': [(0, 0)],
}


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def curve(keys, n):
    t = np.arange(n) / SR
    db = np.full(n, float(keys[0][1]))
    for (t0, d0), (t1, d1) in zip(keys, keys[1:]):
        i0, i1 = int(t0 * SR), int(t1 * SR)
        if i1 <= i0: continue
        u = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, i1 - i0))
        db[i0:i1] = d0 + (d1 - d0) * u
        db[i1:] = d1
    g = 10 ** (db / 20); g[db <= OFF + 0.01] = 0.0
    return g.astype(np.float32)[:, None]


N = int(178.0 * SR)
mix = np.zeros((N, 2), np.float32)
for s, keys in KEYS.items():
    x = load(STEMS / f'{s}.wav')[:N]
    x = np.pad(x, ((0, N - len(x)), (0, 0)))
    mix += x * curve(keys, N)
dst = ROOT / 'audio' / 'bgm_v24_arr.wav'
with wave.open(str(dst), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok', dst.name)
