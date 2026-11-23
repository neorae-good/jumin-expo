# 생활공감정책 film: synthesized sound effects for the desk titles (no samples needed)
#   python3 scripts/policy_sfx.py   -> audio/sfx_title_open.wav (6 s), audio/sfx_title_end.wav (7 s), 48 kHz stereo
# pen: band-passed noise with quick stroke rhythm (felt-tip on paper); stamp: soft wooden thump + paper slap.
# Cue times come from parts/policy/title_sfx.json (written by scripts/policy_titles_desk.js).
import json
from pathlib import Path
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parents[1]; SR = 48000
cue = json.loads((ROOT / 'parts' / 'policy' / 'title_sfx.json').read_text())
rng = np.random.default_rng(3)
bp = lambda x, lo, hi: sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
db = lambda d: 10 ** (d / 20)


def pen(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    strokes = np.clip(np.sin(2 * np.pi * (9 + 3 * np.sin(2 * np.pi * 1.3 * t)) * t), 0, None) ** 1.5   # stroke rhythm
    gaps = (np.sin(2 * np.pi * 2.1 * t + 1) > -0.6).astype(float)                                       # short lifts of the pen
    env = strokes * np.convolve(gaps, np.ones(480) / 480, mode='same')
    env *= np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.06)
    return bp(rng.standard_normal(n), 2200, 7000) * env * db(-30)


def stamp():
    n = int(0.45 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (95 - 40 * t) * t) * np.exp(-t / 0.05) * db(-10)
    slap = bp(rng.standard_normal(n), 600, 4000) * np.exp(-t / 0.012) * db(-16)
    tail = bp(rng.standard_normal(n), 200, 1200) * np.exp(-t / 0.08) * db(-34)
    return thump + slap + tail


for kind, dur in (('open', 6.0), ('end', 7.0)):
    out = np.zeros(int(dur * SR))
    for t0 in cue[kind]['pen']:
        p = pen(cue[kind]['wdur']); i = int(t0 * SR); out[i:i + len(p)] += p[:len(out) - i]
    for t0 in cue[kind].get('stamp', []):
        s = stamp(); i = int((t0 + 0.1) * SR); out[i:i + len(s)] += s[:len(out) - i]   # contact at the end of the drop
    st = np.stack([out, out], 1).astype(np.float32)
    sf.write(ROOT / 'audio' / f'sfx_title_{kind}.wav', st, SR, subtype='PCM_16'); print('ok', kind, round(float(np.abs(out).max()), 3))
