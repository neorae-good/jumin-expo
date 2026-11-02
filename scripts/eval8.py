# score every v18 take of one voice: STT match, ASR confidence, pitch drift, movement, pace, pauses -> narr/v8/<voice>_eval.txt + auto pick
import glob, os, json, difflib, sys, numpy as np, librosa
from faster_whisper import WhisperModel
from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[1]).replace(chr(92), '/')
vn = sys.argv[1]
lines = {x['id']: x for x in json.load(open(ROOT + '/narr/script6.json', encoding='utf-8'))}
norm = lambda s: ''.join(c for c in s if c.isalnum())
m = WhisperModel('medium', device='cpu', compute_type='int8')
data = {}
for f in sorted(glob.glob(f'{ROOT}/narr/v8/{vn}/L*.mp3')):
    tk = os.path.basename(f)[:-4]; lid = tk[:3]
    ref = lines[lid].get('tts', lines[lid]['text'])
    y, sr = librosa.load(f, sr=16000)
    it = librosa.effects.split(y, top_db=35)
    speech = (it[-1][1] - it[0][0]) / sr
    gaps = [(it[i + 1][0] - it[i][1]) / sr for i in range(len(it) - 1)]
    f0, vf, _ = librosa.pyin(y, fmin=70, fmax=450, sr=sr, frame_length=1024, hop_length=512)
    g = f0[vf & ~np.isnan(f0)]
    st = 12 * np.log2(g / np.median(g))
    segs = list(m.transcribe(f, language='ko', beam_size=5)[0])
    t = ''.join(s.text for s in segs).strip()
    r = difflib.SequenceMatcher(None, norm(ref), norm(t)).ratio()
    syl = sum(1 for c in ref if '\uac00' <= c <= '\ud7a3')
    data[tk] = dict(tk=tk, lid=lid, stt=r, conf=float(np.mean([s.avg_logprob for s in segs])) if segs else -9, txt=t, F0=float(np.median(g)), move=float(np.std(st)), pace=syl / max(0.1, speech - sum(x for x in gaps if x >= 0.15)), dur=len(y) / sr, maxgap=max(gaps) if gaps else 0.0)
F0all = np.median([d['F0'] for d in data.values()])
pick, rows = {}, []
for lid in lines:
    tks = [d for d in data.values() if d['lid'] == lid]
    for d in tks: d['dF0'] = 12 * np.log2(d['F0'] / F0all)
    score = lambda d: d['stt'] * 10 + d['conf'] * 4 - abs(d['dF0']) * 0.5 + min(d['move'], 5.0) * 0.3 - max(0, d['pace'] - 5.3) * 1.5 - (2 if d['maxgap'] > 1.3 else 0)
    best = max(tks, key=score); pick[lid] = best['tk'][-1]
    for d in sorted(tks, key=lambda d: d['tk']):
        rows.append(f"{d['tk']} {'*' if d is best else ' '} stt={d['stt']:.2f} conf={d['conf']:5.2f} F0={d['F0']:4.0f}({d['dF0']:+.1f}) move={d['move']:4.2f} pace={d['pace']:4.2f} dur={d['dur']:4.1f} maxgap={d['maxgap']:.2f} | {d['txt'] if d['stt'] < 0.98 else ''}")
rows.append(f'{vn} F0 median {F0all:.0f} Hz')
open(f'{ROOT}/narr/v8/{vn}_eval.txt', 'w', encoding='utf-8').write('\n'.join(rows))
json.dump(pick, open(f'{ROOT}/narr/v8/{vn}_pick_auto.json', 'w'))
