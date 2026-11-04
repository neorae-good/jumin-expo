# v25 take picking.
#   python scripts/pick_v25.py title juan24              stronger 15 s title (LT e-h) into an existing pick
#   python scripts/pick_v25.py full haechan24            whole designed-style pick (title from LT e-h)
#   python scripts/pick_v25.py strong juanS juan24       "힘찬" pick: same length as the designed pick (+-5 %), more force
import difflib, glob, json, os, subprocess, sys
import numpy as np, librosa
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode, vn = sys.argv[1], sys.argv[2]
ref_vn = sys.argv[3] if len(sys.argv) > 3 else None
lines = {x['id']: x for x in json.load(open(f'{ROOT}/narr/script6.json', encoding='utf-8'))}
DESIGN = {'L01': (-2, 1.5), 'L02': (-2, 1.5), 'LT': (1.5, 5), 'L03': (1, 3.5), 'L08': (1, 3.5),
          'L12': (2, 5), 'L13': (0.5, 3), 'L14': (0.5, 3), 'L15': (3, 9)}
STRONG = {'L01': (-1, 3), 'L02': (-1, 3), 'LT': (1.5, 6), 'L03': (1, 6), 'L08': (1, 6),
          'L12': (2, 6.5), 'L13': (1, 5), 'L14': (1, 5), 'L15': (3, 10)}
PLAIN = {'full': (-2, 2), 'title': (-2, 2), 'strong': (-1, 4.5)}[mode]
BAND = {'full': DESIGN, 'title': DESIGN, 'strong': STRONG}[mode]
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


def wav_len(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f],
                                capture_output=True, text=True).stdout)


files = sorted(glob.glob(f'{ROOT}/narr/v8/{vn}/*.mp3'))
if mode == 'title':
    files = [f for f in files if os.path.basename(f)[:3] == 'LTe' or os.path.basename(f)[:2] == 'LT' and os.path.basename(f)[2] in 'efgh']
data = {}
for f in files:
    tk = os.path.basename(f)[:-4]; lid = tk[:3] if tk.startswith('L1') or tk.startswith('L0') else tk[:2]
    if mode == 'full' and lid == 'LT' and tk[2] not in 'efgh': continue
    ref = '주민의 하나된 힘으로 경남이 힘차게 도약합니다' if lid == 'L15' else lines[lid].get('tts', lines[lid]['text'])
    t = ''.join(s.text for s in m.transcribe(f, language='ko', beam_size=5)[0]).strip()
    d, f0, spread, breath, rms = analyse(f)
    data[tk] = dict(lid=lid, stt=difflib.SequenceMatcher(None, norm(fix(ref)), norm(fix(t))).ratio(), txt=t,
                    d=d, f0=f0, spread=spread, breath=breath, rms=rms)
# the voice's normal pitch = median of its plain designed-style lines
normal_dir = ref_vn or vn
plain_ref = [analyse(f)[1] for f in sorted(glob.glob(f'{ROOT}/narr/v8p/{normal_dir}/*.wav'))
             if os.path.basename(f)[:-4] not in DESIGN] if mode != 'full' else []
normal = float(np.median(plain_ref)) if plain_ref else float(np.median([v['f0'] for v in data.values() if v['lid'] not in BAND]))
picks = json.load(open(f'{ROOT}/narr/v8/picks.json'))
pick = dict(picks.get(vn, {})) if mode == 'title' else {}
rows = []
for lid in lines:
    tks = {k: v for k, v in data.items() if v['lid'] == lid}
    if not tks: continue
    lo, hi = BAND.get(lid, PLAIN)
    ref_len = wav_len(f'{ROOT}/narr/v8p/{ref_vn}/{lid}.wav') if mode == 'strong' else None
    def score(v):
        st = 12 * np.log2(v['f0'] / normal)
        s = v['stt'] * 10 - max(0, lo - st, st - hi) * 1.2 - max(0, v['breath'] + 30) * 0.25
        if mode == 'strong':
            s += (v['rms'] - np.mean([w['rms'] for w in tks.values()])) * 0.4 + v['spread'] * 0.2
            s -= max(0, abs(v['d'] / ref_len - 1) - 0.05) * 40       # keep the same pace as the designed version
        else:
            s += v['spread'] * 0.4
            if lid in ACC: s += (v['rms'] - np.mean([w['rms'] for w in tks.values()])) * 0.4
        return s
    best = max(tks, key=lambda k: score(tks[k])); pick[lid] = best[len(lid):]
    for k in sorted(tks):
        v = tks[k]
        extra = f" len x{v['d'] / ref_len:.2f}" if ref_len else ''
        rows.append(f"{k:5s} {'*' if k == best else ' '} stt={v['stt']:.2f} {v['d']:4.1f}s {12*np.log2(v['f0']/normal):+5.1f}st "
                    f"(band {lo:+.1f}..{hi:+.1f}) spread={v['spread']:.1f} rms={v['rms']:.1f} breath={v['breath']:+6.1f}{extra} | {v['txt'] if v['stt'] < 0.99 else ''}")
rows.append(f'{vn} normal pitch {normal:.0f} Hz ({mode})')
open(f'{ROOT}/narr/v8/{vn}_eval_{mode}.txt', 'w', encoding='utf-8').write('\n'.join(rows))
picks = json.load(open(f'{ROOT}/narr/v8/picks.json')); picks[vn] = pick
json.dump(picks, open(f'{ROOT}/narr/v8/picks.json', 'w'), indent=1)
print('\n'.join(r for r in rows if '*' in r or 'normal pitch' in r))
