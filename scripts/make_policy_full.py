# 생활공감정책 참여단: intro (30.2 s) + scene 2 history (95.6 s) [+ scene 3 activities (41.3 s) + 4 s end card] in one film,
# Kyle narration, music, captions.
#   python scripts/make_policy_full.py src_video/policy_intro_src2.mp4 src_video/policy_scene2.mp4 [src_video/policy_scene3.mp4]
#   -> deliverables/policy/생활공감정책_인트로+장면2_kyle_미리보기.mp4
# Scene changes: overlapping transitions (ffmpeg xfade, an open-source port of GL Transitions). TRANS=glow (default):
# cross-dissolve with a soft warm light leak at the chapter changes; TRANS=fade|fadeblack|circleopen|smoothleft: plain xfade.
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
if V4:   # scene 4: three cases, one per footage section. When a case's narration is longer than its footage,
         # only that footage plays slower (the recordings are never stretched)
    SEC4 = [0.0, 15.067, 29.067, D4]   # the footage's own cuts
    GRP4 = [['U01'], ['U02a', 'T02b'], ['T03a', 'U03']]
    LEAD4, GAP4, TAIL4 = [0.8, 0.4, 0.4], 0.45, [1.0, 0.6, 1.3]
    S4 = json.load(open(ROOT / 'narr' / 'policy4' / 'script.json', encoding='utf-8'))
    SPL4 = json.load(open(ROOT / 'narr' / 'policy4' / 'splits_kyle.json'))
    d4 = {x['id']: dur(ROOT / 'narr' / 'policy4_p' / vn / f"{x['id']}.wav") for x in S4}
    SPD4, NEW4 = [], [0.0]
    for k, g in enumerate(GRP4):
        need = LEAD4[k] + sum(d4[i] for i in g) + GAP4 * (len(g) - 1) + TAIL4[k]
        f = max(1.0, need / (SEC4[k + 1] - SEC4[k])); SPD4.append(round(f, 3)); NEW4.append(NEW4[-1] + (SEC4[k + 1] - SEC4[k]) * f)
    print('scene 4 footage speed per case:', ', '.join(f'{1 / f:.2f}x' for f in SPD4), f'-> {D4:.2f} s becomes {NEW4[-1]:.2f} s')
    D4 = NEW4[-1]
CARD = 4.0 if V3 else 0.0          # end card: group name + 경상남도 logo (scripts/policy_endcard.js)
TRANS = os.environ.get('TRANS', 'glow'); XF = float(os.environ.get('XF', '1.0'))   # transition style and length
B2 = D1 - XF; B3 = B2 + D2 - XF; B4 = B3 + D3 - XF; BC = B4 + D4 - XF       # scene starts on the film timeline
FILM = BC + XF
total = round(BC + CARD, 3)
INTRO = {'P01': 0.3, 'P02': 4.4, 'P03': 10.5, 'P04': 13.85, 'P05': 19.57, 'P06': 24.66}
SECT = [0, 10.2, 15.2, 25.2, 35.4, 45.0, 55.0, 65.5, 75.3, 85.3]      # scene 2 section starts (photo changes)
LEAD = [1.1, 0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]             # first: once the transition from the intro is mostly done
IN_GAP, MIN_GAP = 0.4, 0.5
lines = []
for x in json.load(open(ROOT / 'narr' / 'policy' / 'script.json', encoding='utf-8')):
    lines.append(dict(id=x['id'], dur=dur(ROOT / 'narr' / 'policy_p' / vn / f"{x['id']}.wav"), t=INTRO[x['id']], src='policy_p'))
end = lines[-1]['t'] + lines[-1]['dur']
q = json.load(open(ROOT / 'narr' / 'policy2' / 'script.json', encoding='utf-8'))
for k in range(10):
    para = [x for x in q if x['id'].startswith(f'Q{k + 1:02d}')]
    t = max(B2 + SECT[k] + LEAD[k], end + MIN_GAP)
    for j, x in enumerate(para):
        d = dur(ROOT / 'narr' / 'policy2_p' / vn / f"{x['id']}.wav")
        lines.append(dict(id=x['id'], dur=d, t=round(t, 3), src='policy2_p'))
        end = t + d; t = end + IN_GAP
    nxt = B2 + SECT[k + 1] if k < 9 else B3
    print(f"Q{k + 1:02d}: {lines[-len(para)]['t']:.2f}-{end:.2f} s (section {B2 + SECT[k]:.2f}-{nxt:.2f}){'  runs over by %.2f' % (end - nxt) if end > nxt else ''}")
if end > B3 + 0.3: sys.exit('last line ends too late')
nd0 = ROOT / 'narr' / 'policy_full_p' / vn; nd0.mkdir(parents=True, exist_ok=True)
BGM = 'bgm_v29_arr.wav'
if V3:   # scene 3: Kyle narration (narr/policy3) on the scene's beats; the scene's own dialogue is dropped and only its
         # ambience (Demucs drums+bass+other of the scene audio) is laid under the music
    R = {'R01': 0.5, 'R02': 4.95, 'R03': 10.35, 'R04': 15.65, 'R05': 18.95, 'R06': 27.25, 'R07': 31.8, 'R08': 36.2}
    prev_end = end
    for x in json.load(open(ROOT / 'narr' / 'policy3' / 'script.json', encoding='utf-8')):
        d = dur(ROOT / 'narr' / 'policy3_p' / vn / f"{x['id']}.wav"); t = B3 + R[x['id']]
        if t - prev_end < 0.3: sys.exit(f"{x['id']} starts {t - prev_end:.2f} s after the previous line")
        lines.append(dict(id=x['id'], dur=d, t=round(t, 3), src='policy3_p')); prev_end = t + d
        print(f"{x['id']}: scene3 {R[x['id']]:.2f}-{R[x['id']] + d:.2f} s")
    if prev_end > B4 + 0.2: sys.exit('scene 3 narration ends too late')
    if V4:   # scene 4: each case starts just after its (possibly slowed) footage section begins
        for k, g in enumerate(GRP4):
            t = B4 + NEW4[k] + LEAD4[k]
            for i in g:
                if t - prev_end < 0.3: sys.exit(f'{i} starts {t - prev_end:.2f} s after the previous line')
                lines.append(dict(id=i, dur=d4[i], t=round(t, 3), src='policy4_p', split=SPL4.get(i)))
                print(f'{i}: scene4 {t - B4:.2f}-{t - B4 + d4[i]:.2f} s'); prev_end = t + d4[i]; t = prev_end + GAP4
        if prev_end > BC + 0.2: sys.exit('scene 4 narration ends too late')
    # music arranged for this film (no cuts): scripts/stem_arrange_policy.py. With scene 4 the first song ends
    # (fading) in the dip into scene 4, because it is too short for the whole film
    # with scene 4 the film is longer than the first song: the second song takes over at the dip between scene 2
    # (history) and scene 3 (today's activities), so the two songs share the film roughly half and half
    # the first song ENDS on a strong downbeat (SONG1_END, film s; 128.01 = start of an 8-bar phrase at 112 BPM) and
    # rings out; the second song starts just after it
    SONG1_END = float(os.environ.get('SONG1_END', '128.01'))
    SWITCH = SONG1_END + 0.45
    T1 = round(SONG1_END + 2.6, 3)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'stem_arrange_policy.py'), str(T1)], check=True, cwd=ROOT,
                   env=dict(os.environ, END_AT=str(SONG1_END)))
    BGM = 'bgm_policy_arr.wav'
    import numpy as np, soundfile as sf
    st = ROOT / 'audio' / 'stems' / 'htdemucs' / 'scene3_src'
    amb = sum(sf.read(st / f'{k}.wav', dtype='float32')[0] for k in ('drums', 'bass', 'other'))
    mus, sr = sf.read(ROOT / 'audio' / BGM, dtype='float32')
    mus = np.pad(mus, ((0, max(0, int(total * 48000) - len(mus))), (0, 0)))
    rs = lambda a: np.stack([np.interp(np.arange(int(len(a) * 48000 / 44100)) * 44100 / 48000, np.arange(len(a)), a[:, c]) for c in range(2)], 1)
    rms = lambda a: float(np.sqrt((a.astype(np.float64) ** 2).mean()))
    if V4:   # second song (Shared Dreams) from its own start: calm scene-3 opening, drums as the volunteering begins
        s2, sr2 = sf.read(ROOT / 'audio' / 'src_v22_5_dreams.wav', dtype='float32')
        if sr2 != 48000: s2 = rs(s2)
        L = int((total - SWITCH) * 48000); s2 = s2[:L].copy()
        g = rms(mus[int(100 * 48000):int(120 * 48000)]) / rms(s2[int(18 * 48000):int(40 * 48000)]) * 10 ** (-1 / 20)
        s2 *= g; fi, fo = int(0.8 * 48000), int(3.0 * 48000)
        s2[:fi] *= np.linspace(0, 1, fi)[:, None]; s2[-fo:] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, fo)))[:, None]
        j0 = int(SWITCH * 48000); mus[j0:j0 + len(s2)] += s2[:len(mus) - j0]
        j0 = int(B4 * 48000)   # scene 4 ambience below
        print(f'second song gain {20 * np.log10(g):+.1f} dB')
        st4 = ROOT / 'audio' / 'stems' / 'htdemucs' / 'scene4_src'
        amb4 = rs(sum(sf.read(st4 / f'{k}.wav', dtype='float32')[0] for k in ('drums', 'bass', 'other')))
        n4 = min(len(amb4), len(mus) - j0); mus[j0:j0 + n4] += amb4[:n4] * 0.7
    # Demucs stems are 44.1 kHz: resample to the music's 48 kHz
    amb = np.stack([np.interp(np.arange(int(len(amb) * 48000 / 44100)) * 44100 / 48000, np.arange(len(amb)), amb[:, c]) for c in range(2)], 1)
    i0 = int(B3 * 48000); n = min(len(amb), len(mus) - i0)
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
OUT = ROOT / 'deliverables' / 'policy' / '생활공감정책_인트로+장면2+장면3+장면4_끝화면_kyle_미리보기.mp4'
if os.environ.get('AUDIO_ONLY'):
    dst = Path(os.environ.get('AUDIO_ONLY_OUT', str(OUT)))
    tmp = dst.with_suffix('.tmp.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT), '-i', str(ROOT / 'audio' / 'master_mix9_policyfull_kyle.wav'),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(total),
                    '-movflags', '+faststart', str(tmp)], check=True)
    tmp.replace(dst); print('ok (new sound only)', dst); sys.exit(0)
if not (V3 and V4): sys.exit('the overlapping-transition build needs all four scenes')
inputs = ['-i', V1, '-i', V2, '-i', V3, '-i', V4, '-loop', '1', '-framerate', '30', '-t', str(CARD + XF), '-i', str(P / 'endcard.png')]
FIT = 'fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,format=yuv420p'
parts = ''.join(f'[q{k}]trim=start={SEC4[k]}:end={SEC4[k + 1]},setpts=(PTS-STARTPTS)*{SPD4[k]}[r{k}];' for k in range(3))
fc = [f'[0:v]{FIT}[a]',
      '[1:v]fps=30,scale=-2:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0:black,setsar=1,format=yuv420p[b]',
      f'[2:v]{FIT}[c]',
      f'[3:v]split=3[q0][q1][q2];{parts}[r0][r1][r2]concat=n=3:v=1:a=0,{FIT}[d4]',
      '[4:v]fps=30,setsar=1,format=yuv420p[e]']
if os.environ.get('FIXED'):   # use the cleaned scenes from scripts/policy_fix_scenes.py (same lengths, in-scene dissolves)
    for k in range(4): inputs[2 * k + 1] = str(P / f'fixed_s{k + 1}.mp4')
    fc[:4] = [f'[{k}:v]fps=30,settb=1/30,setsar=1,format=yuv420p[{n}]' for k, n in enumerate(('a', 'b', 'c', 'd4'))]
    fc[4] = '[4:v]fps=30,settb=1/30,setsar=1,format=yuv420p[e]'
XT = 'fade' if TRANS == 'glow' else TRANS
fc.append(f'[a][b]xfade=transition={XT}:duration={XF}:offset={B2:.3f}[x1]')
fc.append(f'[x1][c]xfade=transition={XT}:duration={XF}:offset={B3:.3f}[x2]')
fc.append(f'[x2][d4]xfade=transition={XT}:duration={XF}:offset={B4:.3f}[x3]')
fc.append(f'[x3][e]xfade=transition=fade:duration={XF}:offset={BC:.3f}[x4]')
if TRANS == 'glow':   # warm light leak (parts/policy/leak.png) rising and falling around the middle of each chapter change
    fc.append(f'color=c=black:s=1920x1080:r=30:d={total:.3f},format=rgba[g0]')
    for k, tm in enumerate((B2 + XF / 2, B3 + XF / 2, B4 + XF / 2), 1):
        inputs += ['-loop', '1', '-framerate', '30', '-t', '2.2', '-i', str(P / 'leak.png')]
        fc.append(f'[{inputs.count("-i") - 1}:v]format=rgba,lutrgb=r=val*0.65:g=val*0.65:b=val*0.65,fade=t=in:st=0:d=1.1:alpha=1,'
                  f'fade=t=out:st=1.1:d=1.1:alpha=1,setpts=PTS-STARTPTS+{tm - 1.1:.3f}/TB[l{k}]')
        fc.append(f'[g{k - 1}][l{k}]overlay=eof_action=pass[g{k}]')
    fc.append('[x4]format=gbrp[m];[g3]format=gbrp[gl];[m][gl]blend=all_mode=screen:shortest=1,format=yuva420p[b0]')
else:
    fc.append('[x4]format=yuva420p[b0]')
NV = inputs.count('-i')
cl = []
for x in lines:   # a long sentence shows as two captions, switching at a word boundary (narr/policy4/splits_kyle.json)
    if x.get('split'):
        cuts = [0.0] + x['split'] + [x['dur']]
        cl += [dict(id=f"{x['id']}_{k + 1}", t=round(x['t'] + cuts[k], 3), dur=cuts[k + 1] - cuts[k]) for k in range(len(cuts) - 1)]
    elif not x.get('nocap'): cl.append(x)
prev = 'b0'
for i, x in enumerate(cl, 1):
    a = max(0.0, x['t'] - 0.1)
    b = cl[i]['t'] - 0.08 if i < len(cl) else BC + 0.2
    for cut in (B3, B4):   # a scene's captions end as its transition begins
        if x['t'] < cut: b = min(b, cut + 0.25); break
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
