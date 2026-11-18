# 생활공감정책 참여단: intro (30.2 s) + scene 2 history (95.6 s) [+ scene 3 activities (41.3 s) + 4 s end card] in one film,
# Kyle narration, music, captions.
#   python scripts/make_policy_full.py src_video/policy_intro_src2.mp4 src_video/policy_scene2.mp4 [src_video/policy_scene3.mp4]
#   -> deliverables/policy/생활공감정책_인트로+장면2_kyle_미리보기.mp4
# Intro lines keep their scene-cut starts. Scene 2 has one section per era (10 sections); each paragraph starts just
# after its section begins (or after the previous paragraph if that one ran over). Recordings are never stretched.
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1, V2 = sys.argv[1], sys.argv[2]
V3 = sys.argv[3] if len(sys.argv) > 3 else None   # scene 3 (narr/policy3) + end card (parts/policy/endcard.png)
V4 = sys.argv[4] if len(sys.argv) > 4 else None   # scene 4: proposal cases (narr/policy4); its music is a second song
vn = 'kyle'
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
D1, D2 = dur(V1), dur(V2)
D3 = dur(V3) if V3 else 0.0
D4 = dur(V4) if V4 else 0.0
CARD = 4.0 if V3 else 0.0          # end card: group name + 경상남도 logo (scripts/policy_endcard.js)
FILM = D1 + D2 + D3 + D4
total = round(FILM + CARD, 3)
INTRO = {'P01': 0.3, 'P02': 4.4, 'P03': 10.5, 'P04': 13.85, 'P05': 19.57, 'P06': 24.66}
SECT = [0, 10.2, 15.2, 25.2, 35.4, 45.0, 55.0, 65.5, 75.3, 85.3]      # scene 2 section starts (photo changes)
LEAD = [0.8, 0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]             # first: after the dip from the intro
IN_GAP, MIN_GAP = 0.4, 0.5
lines = []
for x in json.load(open(ROOT / 'narr' / 'policy' / 'script.json', encoding='utf-8')):
    lines.append(dict(id=x['id'], dur=dur(ROOT / 'narr' / 'policy_p' / vn / f"{x['id']}.wav"), t=INTRO[x['id']], src='policy_p'))
end = lines[-1]['t'] + lines[-1]['dur']
q = json.load(open(ROOT / 'narr' / 'policy2' / 'script.json', encoding='utf-8'))
for k in range(10):
    para = [x for x in q if x['id'].startswith(f'Q{k + 1:02d}')]
    t = max(D1 + SECT[k] + LEAD[k], end + MIN_GAP)
    for j, x in enumerate(para):
        d = dur(ROOT / 'narr' / 'policy2_p' / vn / f"{x['id']}.wav")
        lines.append(dict(id=x['id'], dur=d, t=round(t, 3), src='policy2_p'))
        end = t + d; t = end + IN_GAP
    nxt = D1 + SECT[k + 1] if k < 9 else D1 + D2
    print(f"Q{k + 1:02d}: {lines[-len(para)]['t']:.2f}-{end:.2f} s (section {D1 + SECT[k]:.2f}-{nxt:.2f}){'  runs over by %.2f' % (end - nxt) if end > nxt else ''}")
if end > D1 + D2 - 0.5: sys.exit('last line ends too late')
nd0 = ROOT / 'narr' / 'policy_full_p' / vn; nd0.mkdir(parents=True, exist_ok=True)
BGM = 'bgm_v29_arr.wav'
if V3:   # scene 3: Kyle narration (narr/policy3) on the scene's beats; the scene's own dialogue is dropped and only its
         # ambience (Demucs drums+bass+other of the scene audio) is laid under the music
    R = {'R01': 0.5, 'R02': 4.95, 'R03': 10.35, 'R04': 15.65, 'R05': 18.95, 'R06': 27.25, 'R07': 31.8, 'R08': 36.2}
    prev_end = end
    for x in json.load(open(ROOT / 'narr' / 'policy3' / 'script.json', encoding='utf-8')):
        d = dur(ROOT / 'narr' / 'policy3_p' / vn / f"{x['id']}.wav"); t = D1 + D2 + R[x['id']]
        if t - prev_end < 0.3: sys.exit(f"{x['id']} starts {t - prev_end:.2f} s after the previous line")
        lines.append(dict(id=x['id'], dur=d, t=round(t, 3), src='policy3_p')); prev_end = t + d
        print(f"{x['id']}: scene3 {R[x['id']]:.2f}-{R[x['id']] + d:.2f} s")
    if prev_end > D1 + D2 + D3 - 1.2: sys.exit('scene 3 narration ends too late')
    if V4:   # scene 4: each case starts on its scene cut (walking path 0 / phone stand 15.1 / post office 29.1)
        T4 = {'T01a': 0.8, 'T01b': 7.6, 'T02a': 15.5, 'T02b': 21.7, 'T03a': 29.5, 'T03b': 34.25}
        for x in json.load(open(ROOT / 'narr' / 'policy4' / 'script.json', encoding='utf-8')):
            d = dur(ROOT / 'narr' / 'policy4_p' / vn / f"{x['id']}.wav"); t = D1 + D2 + D3 + T4[x['id']]
            if t - prev_end < 0.3: sys.exit(f"{x['id']} starts {t - prev_end:.2f} s after the previous line")
            lines.append(dict(id=x['id'], dur=d, t=round(t, 3), src='policy4_p')); prev_end = t + d
            print(f"{x['id']}: scene4 {T4[x['id']]:.2f}-{T4[x['id']] + d:.2f} s")
        if prev_end > FILM - 1.2: sys.exit('scene 4 narration ends too late')
    # music arranged for this film (no cuts): scripts/stem_arrange_policy.py. With scene 4 the first song ends
    # (fading) in the dip into scene 4, because it is too short for the whole film
    T1 = round(D1 + D2 + D3 + 0.45, 3) if V4 else total
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'stem_arrange_policy.py'), str(T1)], check=True, cwd=ROOT)
    BGM = 'bgm_policy_arr.wav'
    import numpy as np, soundfile as sf
    st = ROOT / 'audio' / 'stems' / 'htdemucs' / 'scene3_src'
    amb = sum(sf.read(st / f'{k}.wav', dtype='float32')[0] for k in ('drums', 'bass', 'other'))
    mus, sr = sf.read(ROOT / 'audio' / BGM, dtype='float32')
    mus = np.pad(mus, ((0, max(0, int(total * 48000) - len(mus))), (0, 0)))
    rs = lambda a: np.stack([np.interp(np.arange(int(len(a) * 48000 / 44100)) * 44100 / 48000, np.arange(len(a)), a[:, c]) for c in range(2)], 1)
    rms = lambda a: float(np.sqrt((a.astype(np.float64) ** 2).mean()))
    if V4:   # second song (Shared Dreams) from its own start: calm walking path, drums by the phone stand
        s2, sr2 = sf.read(ROOT / 'audio' / 'src_v22_5_dreams.wav', dtype='float32')
        if sr2 != 48000: s2 = rs(s2)
        L = int((D4 + CARD) * 48000); s2 = s2[:L].copy()
        g = rms(mus[int(140 * 48000):int(160 * 48000)]) / rms(s2[int(18 * 48000):int(40 * 48000)]) * 10 ** (-1 / 20)
        s2 *= g; fi, fo = int(0.8 * 48000), int(3.0 * 48000)
        s2[:fi] *= np.linspace(0, 1, fi)[:, None]; s2[-fo:] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, fo)))[:, None]
        j0 = int((D1 + D2 + D3) * 48000); mus[j0:j0 + len(s2)] += s2[:len(mus) - j0]
        print(f'second song gain {20 * np.log10(g):+.1f} dB')
        st4 = ROOT / 'audio' / 'stems' / 'htdemucs' / 'scene4_src'
        amb4 = rs(sum(sf.read(st4 / f'{k}.wav', dtype='float32')[0] for k in ('drums', 'bass', 'other')))
        n4 = min(len(amb4), len(mus) - j0); mus[j0:j0 + n4] += amb4[:n4] * 0.7
    # Demucs stems are 44.1 kHz: resample to the music's 48 kHz
    amb = np.stack([np.interp(np.arange(int(len(amb) * 48000 / 44100)) * 44100 / 48000, np.arange(len(amb)), amb[:, c]) for c in range(2)], 1)
    i0 = int((D1 + D2) * 48000); n = min(len(amb), len(mus) - i0)
    mus = mus.copy(); mus[i0:i0 + n] += amb[:n] * 0.7
    BGM = 'bgm_policy_full.wav'; sf.write(ROOT / 'audio' / BGM, mus, 48000, subtype='PCM_16')
# one folder of line wavs for mix9
nd = ROOT / 'narr' / 'policy_full_p' / vn; nd.mkdir(parents=True, exist_ok=True)
for x in lines:
    if not x['src']: continue
    l = nd / f"{x['id']}.wav"
    if l.is_symlink() or l.exists(): l.unlink()
    l.symlink_to(Path('..') / '..' / x['src'] / vn / f"{x['id']}.wav")
json.dump(lines, open(ROOT / 'narr' / 'policy' / 'lines_full_kyle.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
env = dict(os.environ, NARR_LIGHT='1', CARVE_TARGET='14', CARVE_MAX='12', MUSIC_DB='2', NO_SFX='1', TOTAL=str(total),
           NARR_SCRIPT='narr/policy/lines_full_kyle.json', NARR_DIR='narr/policy_full_p', BGM_FADE=f'{total - 3.0},{total}')
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'mix9.py'), vn, 'policyfull_kyle', 'off', '0.4', BGM],
               env=env, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
P = ROOT / 'parts' / 'policy'
inputs = ['-i', V1, '-i', V2]
fc = [f'[0:v]fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,fade=t=out:st={D1 - 0.5:.3f}:d=0.5[a]',
      f'[1:v]fps=30,scale=-2:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0:black,setsar=1,fade=t=in:st=0:d=0.5[b]',
      ]
if V3:
    fc[1] = fc[1].replace('[b]', f',fade=t=out:st={D2 - 0.5:.3f}:d=0.5[b]')
    fc.append('[2:v]fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,fade=t=in:st=0:d=0.5[c]')
    fc[-1] = fc[-1].replace('[c]', f',fade=t=out:st={D3 - 0.6:.3f}:d=0.6[c]')
    inputs += ['-i', V3]
    if V4:
        fc.append(f'[3:v]fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,fade=t=in:st=0:d=0.5,fade=t=out:st={D4 - 0.6:.3f}:d=0.6[d4]')
        inputs += ['-i', V4]
    ei = inputs.count('-i')
    fc.append(f'[{ei}:v]fps=30,format=yuv420p,setsar=1,fade=t=in:st=0:d=0.8[e]')
    fc.append(('[a][b][c][d4][e]concat=n=5' if V4 else '[a][b][c][e]concat=n=4') + ':v=1:a=0,format=yuva420p[b0]')
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(CARD), '-i', str(ROOT / 'parts' / 'policy' / 'endcard.png')]
else:
    fc.append('[a][b]concat=n=2:v=1:a=0,format=yuva420p[b0]')
NV = inputs.count('-i')
cl = [x for x in lines if not x.get('nocap')]
SPLIT = D1 + D2   # scene-2 captions end before the dip into scene 3
prev = 'b0'
for i, x in enumerate(cl, 1):
    a = max(0.0, x['t'] - 0.1)
    b = cl[i]['t'] - 0.08 if i < len(cl) else FILM - 0.8
    for cut in (D1 + D2, D1 + D2 + D3):   # captions end before each dip between scenes
        if x['t'] < cut: b = min(b, cut - 0.3); break
    b = min(b, x['t'] + x['dur'] + 0.6)
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / f"cap_{x['id']}.png")]
    fc.append(f"[{NV + i - 1}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.25:alpha=1,fade=t=out:st={b - 0.25:.2f}:d=0.25:alpha=1[c{i}]")
    fc.append(f'[{prev}][c{i}]overlay=eof_action=pass[o{i}]'); prev = f'o{i}'
fc.append(f'[{prev}]fade=t=out:st={total - 1.0}:d=1.0,format=yuv420p[v]')
out = ROOT / 'deliverables' / 'policy' / ('생활공감정책_인트로+장면2+장면3+장면4_끝화면_kyle_미리보기.mp4' if V4 else '생활공감정책_인트로+장면2+장면3_끝화면_kyle_미리보기.mp4' if V3 else '생활공감정책_인트로+장면2_kyle_미리보기.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-i', str(ROOT / 'audio' / 'master_mix9_policyfull_kyle.wav'),
                '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f"{inputs.count('-i')}:a", '-t', str(total),
                '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)
print('ok', out, total, 's')
