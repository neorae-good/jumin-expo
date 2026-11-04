# v24: pick one take per line for a voice recorded with scripts/tts_v24.py
#   python scripts/pick_v24.py juan24
# Targets follow the intonation design: each line's median pitch should sit in its band (semitones vs the voice's
# plain-line median), the transcription must be clean, livelier intonation (pitch spread) is preferred, breaths cost.
import difflib, glob, json, os, sys
import numpy as np, librosa
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vn = sys.argv[1]
lines = {x['id']: x for x in json.load(open(f'{ROOT}/narr/script6.json', encoding='utf-8'))}
BAND = {'L01': (-2, 1.5), 'L02': (-2, 1.5), 'LT': (1, 3.5), 'L03': (1, 3.5), 'L08': (1, 3.5),
        'L12': (2, 5), 'L13': (0.5, 3), 'L14': (0.5, 3), 'L15': (3, 9)}
PLAIN = (-2, 2)
ACC = {'LT', 'L03', 'L08', 'L12', 'L15'}
norm = lambda s: ''.join(c for c in s if c.isalnum())
fix = lambda s: (s.replace('첫담', '첫땀').replace('바꾭', '바꿉').replace('하나에', '하나의').replace('하만', '함안')
                 .replace('18개', '열여덟개'))
m = WhisperModel('medium', device='cpu', compute_type='int8')


def analyse(f):
    y, sr = librosa.load(f, sr=16000)
    it = librosa.effects.split(y, top_db=35)
    sp = np.concatenate([y[a:b] for a, b in it]); spdb = 20 * np.log10(np.sqrt((sp ** 2).mean()) + 1e-9)
    breath = -90.0
    for a, b in [(0, it[0][0])] + [(b, c) for (_, b), (c, _) in zip(it, it[1:])]:
        if (b - a) / sr < 0.1: continue
        g = y[a:b]
        if librosa.feature.spectral_flatness(y=g, n_fft=512, hop_length=128).mean() > 0.05:
            breath = max(breath, 20 * np.log10(np.sqrt((g ** 2).mean()) + 1e-9) - spdb)
    yy = y[it[0][0]:it[-1][1]]
    f0, vf, _ = librosa.pyin(yy, fmin=60, fmax=450, sr=sr, frame_length=2048, hop_length=256)
    g = f0[vf & ~np.isnan(f0)]
    return len(yy) / sr, float(np.median(g)), float(np.std(12 * np.log2(g / np.median(g)))), breath, \
        20 * np.log10(np.sqrt((yy ** 2).mean()) + 1e-9)


data = {}
for f in sorted(glob.glob(f'{ROOT}/narr/v8/{vn}/*.mp3')):
    tk = os.path.basename(f)[:-4]; lid = tk[:-1]
    ref = lines[lid].get('tts', lines[lid]['text'])
    if lid == 'L15': ref = '주민의 하나된 힘으로 경남이 힘차게 도약합니다'
    t = ''.join(s.text for s in m.transcribe(f, language='ko', beam_size=5)[0]).strip()
    d, f0, spread, breath, rms = analyse(f)
    data[tk] = dict(lid=lid, stt=difflib.SequenceMatcher(None, norm(fix(ref)), norm(fix(t))).ratio(), txt=t,
                    d=d, f0=f0, spread=spread, breath=breath, rms=rms)
normal = float(np.median([v['f0'] for v in data.values() if v['lid'] not in BAND]))
pick, rows = {}, []
for lid in lines:
    tks = {k: v for k, v in data.items() if v['lid'] == lid}
    lo, hi = BAND.get(lid, PLAIN)
    def score(v):
        st = 12 * np.log2(v['f0'] / normal)
        s = v['stt'] * 10 - max(0, lo - st, st - hi) * 1.2 + v['spread'] * 0.4 - max(0, v['breath'] + 30) * 0.25
        if lid in ACC: s += (v['rms'] - np.mean([w['rms'] for w in tks.values()])) * 0.3
        return s
    best = max(tks, key=lambda k: score(tks[k])); pick[lid] = best[len(lid):]
    for k in sorted(tks):
        v = tks[k]
        rows.append(f"{k:5s} {'*' if k == best else ' '} stt={v['stt']:.2f} {v['d']:4.1f}s {12*np.log2(v['f0']/normal):+5.1f}st "
                    f"(band {lo:+.0f}..{hi:+.0f}) spread={v['spread']:.1f} breath={v['breath']:+6.1f} | {v['txt'] if v['stt'] < 0.99 else ''}")
rows.append(f'{vn} plain-line pitch {normal:.0f} Hz')
open(f'{ROOT}/narr/v8/{vn}_eval.txt', 'w', encoding='utf-8').write('\n'.join(rows))
p = json.load(open(f'{ROOT}/narr/v8/picks.json')); p[vn] = pick
json.dump(p, open(f'{ROOT}/narr/v8/picks.json', 'w'), indent=1)
print('\n'.join(r for r in rows if '*' in r or 'pitch' in r))
