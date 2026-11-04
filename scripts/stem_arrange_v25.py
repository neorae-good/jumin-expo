# v25 arrangement from Demucs stems of audio/bgm_v25.wav (film timeline).
#   python -m demucs -n htdemucs -d cpu -o audio/stems audio/bgm_v25.wav
#   python scripts/stem_arrange_v25.py   -> audio/bgm_v25_arr.wav
# - opening: untouched (the song's own intro, stretched in music_fit_v25.py, brings bass ~17.3 s and drums ~19.8 s)
# - thread close-up 74.6-83.3 s: drums and bass rest, back on the 83.3 s hit
# - cloth throw 139.2 s: drums/bass +1.5 dB (peak), then from the end photos (149.6 s) they settle down
#   (drums -6 dB, bass -3 dB by the title at 162.4 s); the song's own ending follows; long 4 s fade at the end
import subprocess, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
STEMS = ROOT / 'audio' / 'stems' / 'htdemucs' / 'bgm_v25'
OFF = -60
KEYS = {
    'drums': [(0, 0), (74.6, 0), (75.8, OFF), (82.9, OFF), (83.3, 0), (138.4, 0), (139.2, 1.5), (149.6, 1.5), (162.4, -6)],
    'bass':  [(0, 0), (74.6, 0), (76.0, OFF), (82.9, OFF), (83.3, 0), (138.4, 0), (139.2, 1.5), (149.6, 1.5), (162.4, -3)],
    'other': [(0, 0)],
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
with wave.open(str(ROOT / 'audio' / 'bgm_v25_arr.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_v25_arr.wav')
