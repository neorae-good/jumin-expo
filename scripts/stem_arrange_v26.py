# v26: music arranged to the producer's timeline (2026-11-04), from Demucs stems of audio/bgm_v25.wav.
#   python scripts/stem_arrange_v26.py   -> audio/bgm_v26_arr.wav
#   0:00-0:17 calm | 0:17-1:15 as the song | 1:15-1:23 quiet | 1:24-2:10 lifted again | 2:10-2:13 slightly quieter
#   2:13-2:42 most lifted | 2:42-end quiet, fade at the end
import subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
STEMS = ROOT / 'audio' / 'stems' / 'htdemucs' / 'bgm_v25'
OFF = -60
KEYS = {  # (film second, dB) with smooth ramps between points
    'drums': [(0, OFF), (16.5, OFF), (18.0, -3), (19.5, 0),
              (74.6, 0), (75.6, OFF), (83.4, OFF), (84.0, 2),
              (129.5, 2), (130.5, -3), (132.5, -3), (133.2, 3.5),
              (161.5, 3.5), (163.5, -10), (166.0, OFF)],
    'bass':  [(0, OFF), (16.0, OFF), (18.0, 0),
              (74.6, 0), (75.8, OFF), (83.4, OFF), (84.0, 1.5),
              (129.5, 1.5), (130.5, -2), (132.5, -2), (133.2, 2.5),
              (161.5, 2.5), (164.0, -6)],
    'other': [(0, -5), (15.5, -5), (17.5, 0),
              (74.6, 0), (75.6, -3), (83.4, -3), (84.0, 1),
              (129.5, 1), (130.5, -1.5), (132.5, -1.5), (133.2, 2),
              (161.5, 2), (164.0, -3)],
    'vocals': [(0, 0)],
}
FADE = (174.0, 178.0)


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def curve(keys, n):
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
    mix += np.pad(x, ((0, N - len(x)), (0, 0))) * curve(keys, N)
i0, i1 = int(FADE[0] * SR), int(FADE[1] * SR)
mix[i0:i1] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, i1 - i0)))[:, None].astype(np.float32)
mix[i1:] = 0
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak               # the lifted sections must not clip
with wave.open(str(ROOT / 'audio' / 'bgm_v26_arr.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_v26_arr.wav peak', round(float(peak), 3))
