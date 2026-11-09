# 생활공감정책 참여단 intro: pick the best of 3 takes per line for one voice, trim, and lay the lines out in time.
#   python scripts/pick_policy.py kyle   -> narr/policy_p/kyle/P01.wav ..., narr/policy/script_kyle.json (with t), eval txt
# Score: words right (STT) first, then a natural pitch (not shouted), no loud breaths, lively stresses (pitch spread,
# a little extra loudness). No time stretching: lines are only trimmed of silence and placed with pauses.
import difflib, glob, json, os, subprocess, sys
import numpy as np, librosa, soundfile as sf
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vn = sys.argv[1]
PD = os.environ.get('PDIR', 'policy')
lines = json.load(open(f'{ROOT}/narr/{PD}/script.json', encoding='utf-8'))
BAND = {'P03': (-1, 4), 'P06': (-0.5, 4), 'Q10b': (-0.5, 4)}
PLAIN = (-2, 2.5)
GAP_AFTER = {'P01': 0.75, 'P02': 0.8, 'P03': 0.8, 'P04': 0.7, 'P05': 0.6}
START, TAIL = 1.5, 3.5
norm = lambda s: ''.join(c for c in s if c.isalnum())
m = WhisperModel('medium', device='cpu', compute_type='int8')


def analyse(y, sr):
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
    return dict(d=len(yy) / sr, f0=float(np.median(g)), spread=float(np.std(12 * np.log2(g / np.median(g)))), breath=breath,
                rms=20 * np.log10(np.sqrt((yy ** 2).mean()) + 1e-9))


data = {}
for f in sorted(glob.glob(f'{ROOT}/narr/{PD}/{vn}/*.mp3')):
    tk = os.path.basename(f)[:-4]; lid = tk[:-1]
    ref = next(x['text'] for x in lines if x['id'] == lid)
    t = ''.join(s.text for s in m.transcribe(f, language='ko', beam_size=5)[0]).strip()
    y, sr = librosa.load(f, sr=16000)
    data[tk] = dict(lid=lid, stt=difflib.SequenceMatcher(None, norm(ref), norm(t)).ratio(), txt=t, **analyse(y, sr))
normal = float(np.median([v['f0'] for v in data.values()]))
rows, pick = [], {}
for x in lines:
    lid = x['id']; tks = {k: v for k, v in data.items() if v['lid'] == lid}
    lo, hi = BAND.get(lid, PLAIN); mr = np.mean([w['rms'] for w in tks.values()])
    def score(v):
        st = 12 * np.log2(v['f0'] / normal)
        return (v['stt'] * 10 - max(0, lo - st, st - hi) * 1.2 - max(0, v['breath'] + 30) * 0.25
                + v['spread'] * 0.4 + (v['rms'] - mr) * 0.3)
    best = max(tks, key=lambda k: score(tks[k])); pick[lid] = best
    for k in sorted(tks):
        v = tks[k]
        rows.append(f"{k:5s} {'*' if k == best else ' '} stt={v['stt']:.2f} {v['d']:4.1f}s {12*np.log2(v['f0']/normal):+5.1f}st "
                    f"spread={v['spread']:.1f} rms={v['rms']:.1f} breath={v['breath']:+6.1f} | {v['txt']}")
rows.append(f'{vn} normal pitch {normal:.0f} Hz')
# trim and lay out
out = f'{ROOT}/narr/{PD}_p/{vn}'; os.makedirs(out, exist_ok=True)
t, script = START, []
for x in lines:
    y, sr = librosa.load(f"{ROOT}/narr/{PD}/{vn}/{pick[x['id']]}.mp3", sr=48000)
    it = librosa.effects.split(y, top_db=40)
    a, b = max(0, it[0][0] - int(0.05 * sr)), min(len(y), it[-1][1] + int(0.12 * sr))
    seg = y[a:b]; n = int(0.01 * sr); seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
    sf.write(f"{out}/{x['id']}.wav", seg, sr)
    script.append(dict(x, t=round(t, 3), dur=round(len(seg) / sr, 3)))
    t += len(seg) / sr + GAP_AFTER.get(x['id'], 0)
total = round(t + TAIL, 2)
json.dump(dict(total=total, lines=script), open(f'{ROOT}/narr/{PD}/script_{vn}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(script, open(f'{ROOT}/narr/{PD}/lines_{vn}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(f'{ROOT}/narr/{PD}/eval_{vn}.txt', 'w', encoding='utf-8').write('\n'.join(rows))
print('\n'.join(r for r in rows if '*' in r or 'normal' in r)); print(vn, 'total', total)
