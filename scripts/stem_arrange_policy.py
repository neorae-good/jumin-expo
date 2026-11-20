# 생활공감정책 film: the same song (Demucs stems of audio/bgm_v29.wav), arranged for THIS film's flow, no cuts.
#   python scripts/stem_arrange_policy.py [total_s]   -> audio/bgm_policy_arr.wav
#   0:00-0:17 calm intro (as the expo) | 0:30-2:06 history: steady, no dips | 2:06-2:33 scene 3 builds to the
#   song's own climax | the song's drums/bass end by themselves at ~2:35, so the melody is lifted for the closing
#   line (~2:42) and the music fades over the end card.
import os, subprocess, sys, wave
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
STEMS = ROOT / 'audio' / 'stems' / 'htdemucs' / 'bgm_v29'
TOTAL = float(sys.argv[1]) if len(sys.argv) > 1 else 171.2
OFF = -60
KEYS = {
    'drums': [(0, OFF), (16.5, OFF), (18.0, -3), (19.5, 0), (126.0, 0), (134.0, 1.5), (145.0, 2.5), (155.0, 2.5)],
    'bass':  [(0, OFF), (16.0, OFF), (18.0, 0), (126.0, 0), (134.0, 1.0), (145.0, 2.0), (155.0, 2.0)],
    'other': [(0, -5), (15.5, -5), (17.5, 0), (126.0, 0), (145.0, 1.5), (155.0, 1.5), (158.0, 3.0), (TOTAL, 3.0)],
    'vocals': [(0, 0)],
}
FADE = (TOTAL - float(os.environ.get('FADE_S', '3.2')), TOTAL)   # FADE_S: shorter fade when a second song takes over


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def curve(keys, n):
    db = np.full(n, float(keys[0][1]))
    for (t0, d0), (t1, d1) in zip(keys, keys[1:]):
        i0, i1 = int(t0 * SR), min(n, int(t1 * SR))
        if i1 <= i0: continue
        u = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, i1 - i0))
        db[i0:i1] = d0 + (d1 - d0) * u
        db[i1:] = d1
    g = 10 ** (db / 20); g[db <= OFF + 0.01] = 0.0
    return g.astype(np.float32)[:, None]


N = int(TOTAL * SR)
mix = np.zeros((N, 2), np.float32)
for s, keys in KEYS.items():
    x = load(STEMS / f'{s}.wav')[:N]
    mix += np.pad(x, ((0, N - len(x)), (0, 0))) * curve(keys, N)
END_AT = os.environ.get('END_AT')   # a clear ending: stop on this downbeat (film s) and let the hit ring out
if END_AT:
    e0 = int(float(END_AT) * SR); mix[:] = 0
    RING = {'drums': 0.35, 'bass': 0.6, 'other': 2.2, 'vocals': 2.2}     # seconds for each stem to die away after the hit
    for s_, keys in KEYS.items():
        x = load(STEMS / f'{s_}.wav')[:N]; x = np.pad(x, ((0, N - len(x)), (0, 0))) * curve(keys, N)
        tail = np.arange(N - e0, dtype=np.float32) / SR
        x[e0:] *= np.exp(-tail / (RING[s_] / 4.6))[:, None]          # ~-40 dB at the ring time
        mix += x
else:
    i0, i1 = int(FADE[0] * SR), N
    mix[i0:i1] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, i1 - i0)))[:, None].astype(np.float32)
mix *= 10 ** (-6 / 20)              # same fixed headroom as the expo arrangement (HEADROOM_DB=6)
with wave.open(str(ROOT / 'audio' / 'bgm_policy_arr.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok bgm_policy_arr.wav', TOTAL, 's, peak', round(float(np.abs(mix).max()), 3))
