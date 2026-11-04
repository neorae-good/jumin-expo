# v23: score Juan's takes and pick one per line.
#   transcription match (faster-whisper) -> must be clean
#   breath: noise energy inside the pauses between words (breaths are broadband hiss, not voiced)
#   pitch: accent lines must stay near Juan's normal pitch (median of the plain lines) so they sound like the same man
# Writes narr/v8/juan_eval.txt and the "juan" entry of narr/v8/picks.json.
import difflib, glob, json, os
import numpy as np, librosa
from faster_whisper import WhisperModel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lines = {x['id']: x for x in json.load(open(f'{ROOT}/narr/script6.json', encoding='utf-8'))}
ACCENT = {'L03', 'L08', 'L12', 'LT', 'L15'}
norm = lambda s: ''.join(c for c in s if c.isalnum())
fix = lambda s: s.replace('첫담', '첫땀').replace('바꾭', '바꿉').replace('하나에', '하나의').replace('하만', '함안').replace('18개', '열여덟개')
m = WhisperModel('medium', device='cpu', compute_type='int8')


def analyse(f):
    y, sr = librosa.load(f, sr=16000)
    it = librosa.effects.split(y, top_db=35)
    y0, y1 = it[0][0], it[-1][1]
    # breath: in each gap of >= 0.12 s between speech chunks, loudness of unvoiced noise relative to speech
    sp = np.concatenate([y[a:b] for a, b in it])
    sp_db = 20 * np.log10(np.sqrt((sp ** 2).mean()) + 1e-9)
    worst = -90.0
    for (a, b), (c, d) in zip(it, it[1:]):
        if (c - b) / sr < 0.12: continue
        g = y[b:c]; flat = librosa.feature.spectral_flatness(y=g, n_fft=512, hop_length=128).mean()
        e = 20 * np.log10(np.sqrt((g ** 2).mean()) + 1e-9) - sp_db
        if flat > 0.05: worst = max(worst, e)
    f0, vf, _ = librosa.pyin(y[y0:y1], fmin=60, fmax=400, sr=sr, frame_length=2048, hop_length=256)
    g = f0[vf & ~np.isnan(f0)]
    rms = 20 * np.log10(np.sqrt((y[y0:y1] ** 2).mean()) + 1e-9)
    return (y1 - y0) / sr, float(np.median(g)), worst, rms


rows, data = [], {}
for f in sorted(glob.glob(f'{ROOT}/narr/v8/juan/*.mp3')):
    tk = os.path.basename(f)[:-4]; lid = tk[:-1]
    ref = lines[lid].get('tts', lines[lid]['text'])
    t = ''.join(s.text for s in m.transcribe(f, language='ko', beam_size=5)[0]).strip()
    stt = difflib.SequenceMatcher(None, norm(fix(ref)), norm(fix(t))).ratio()
    d, f0, breath, rms = analyse(f)
    data[tk] = dict(lid=lid, stt=stt, txt=t, d=d, f0=f0, breath=breath, rms=rms)
normal = np.median([v['f0'] for v in data.values() if v['lid'] not in ACCENT])
pick = {}
for lid in lines:
    tks = {k: v for k, v in data.items() if v['lid'] == lid}
    def score(v):
        s = v['stt'] * 10 - max(0, v['breath'] + 30) * 0.25          # breaths louder than -30 dB re speech cost points
        if lid in ACCENT:
            s -= max(0, abs(12 * np.log2(v['f0'] / normal)) - 2.0) * 1.5  # more than 2 semitones off normal costs points
            s += (v['rms'] - np.mean([w['rms'] for w in tks.values()])) * 0.3  # a little louder = more emphasis
        return s
    best = max(tks, key=lambda k: score(tks[k])); pick[lid] = best[-1]
    for k in sorted(tks):
        v = tks[k]
        rows.append(f"{k:5s} {'*' if k == best else ' '} stt={v['stt']:.2f} {v['d']:4.1f}s F0={v['f0']:4.0f} ({12*np.log2(v['f0']/normal):+.1f}st) "
                    f"breath={v['breath']:+6.1f}dB rms={v['rms']:6.1f} | {v['txt'] if v['stt'] < 0.99 else ''}")
rows.append(f'Juan normal pitch {normal:.0f} Hz')
open(f'{ROOT}/narr/v8/juan_eval.txt', 'w', encoding='utf-8').write('\n'.join(rows))
p = json.load(open(f'{ROOT}/narr/v8/picks.json')); p['juan'] = pick
json.dump(p, open(f'{ROOT}/narr/v8/picks.json', 'w'), indent=1)
print('\n'.join(rows)); print(pick)
