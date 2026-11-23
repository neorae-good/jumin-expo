# 생활공감정책 참여단 film, v2: opening title + intro + history + activities + cases + thank-you scene + closing title.
#   python3 scripts/make_policy_v2.py   -> deliverables/policy/생활공감정책_참여단_kyle_미리보기.mp4
# Inputs (already prepared): parts/policy/title_open.mp4, fixed_s1..s5.mp4 (scripts/policy_fix_scenes.py: in-scene
# dissolves, cleaned AI shots, re-dressed photos), title_end.mp4 (scripts/policy_titles.js), Kyle lines in narr/policy*_p.
# Scene changes overlap by XF s (xfade); chapter changes add a warm light leak. Recordings are never stretched.
import json, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'parts' / 'policy'; vn = 'kyle'
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
XF = 1.0
TITLES = os.environ.get('TITLES', '0') == '1'   # 1: opening/closing title clips; 0 (default): the film starts and ends on its own scenes
CLIPS = ([P / 'title_open.mp4'] if TITLES else []) + [P / f'fixed_s{k}.mp4' for k in range(1, 6)] + ([P / 'title_end.mp4'] if TITLES else [])
DL = [dur(c) for c in CLIPS]
B = [0.0]
for d in DL[:-1]: B.append(B[-1] + d - XF)              # start of each clip on the film timeline
total = round(B[-1] + DL[-1], 3)
if TITLES: T0, B1, B2, B3, B4, B5, BE = B
else: B1, B2, B3, B4, B5 = B; BE = total
print('clip starts', ' '.join(f'{b:.2f}' for b in B), 'total', total)
L = lambda d, i: dur(ROOT / 'narr' / d / vn / f'{i}.wav')
lines, prev_end = [], 0.0
def put(i, t, d, src, **kw):
    global prev_end
    if lines and t - prev_end < 0.3: sys.exit(f'{i} starts {t - prev_end:.2f} s after the previous line')
    lines.append(dict(id=i, dur=d, t=round(t, 3), src=src, **kw)); prev_end = t + d
# intro: on the intro's own scene cuts
for i, t in {'P01': 0.3, 'P02': 4.4, 'P03': 10.5, 'P04': 13.85, 'P05': 19.57, 'P06': 24.66}.items(): put(i, B1 + t, L('policy_p', i), 'policy_p')
# history: one paragraph per era section
q = json.load(open(ROOT / 'narr' / 'policy2' / 'script.json', encoding='utf-8'))
SECT = [0, 10.2, 15.2, 25.2, 35.4, 45.0, 55.0, 65.5, 75.3, 85.3]; LEAD = [1.1] + [0.2] + [0.5] * 8
for k in range(10):
    t = max(B2 + SECT[k] + LEAD[k], prev_end + 0.5)
    for x in [x for x in q if x['id'].startswith(f'Q{k + 1:02d}')]:
        put(x['id'], t, L('policy2_p', x['id']), 'policy2_p'); t = prev_end + 0.4
if prev_end > B3 + 0.3: sys.exit('history narration ends too late')
for i, t in {'R01': 0.5, 'R02': 4.95, 'R03': 10.35, 'R04': 15.65, 'R05': 18.95, 'R06': 27.25, 'R07': 31.8, 'R08': 36.2}.items():
    put(i, B3 + t, L('policy3_p', i), 'policy3_p')
if prev_end > B4 + 0.2: sys.exit('activities narration ends too late')
# cases: same per-case timing as policy_fix_scenes.py (footage slowed only where the narration is longer)
d4 = {i: L('policy4_p', i) for i in ('U01', 'U02a', 'T02b', 'T03a', 'U03')}
SEC4 = [0.0, 15.067, 29.067, dur(ROOT / 'src_video' / 'policy_scene4.mp4')]
need = [0.8 + d4['U01'] + 1.0, 0.4 + d4['U02a'] + 0.45 + d4['T02b'] + 0.6, 0.4 + d4['T03a'] + 0.45 + d4['U03'] + 1.3]
f4 = [max(1.0, need[k] / (SEC4[k + 1] - SEC4[k])) for k in range(3)]
NEW4 = [0.0, SEC4[1] * f4[0], SEC4[1] * f4[0] + (SEC4[2] - SEC4[1]) * f4[1]]
SPL4 = json.load(open(ROOT / 'narr' / 'policy4' / 'splits_kyle.json'))
for k, (g, lead) in enumerate(zip([['U01'], ['U02a', 'T02b'], ['T03a', 'U03']], [0.8, 0.4, 0.4])):
    t = B4 + NEW4[k] + lead
    for i in g: put(i, t, d4[i], 'policy4_p', split=SPL4.get(i)); t = prev_end + 0.45
if prev_end > B5 + 0.2: sys.exit('cases narration ends too late')
# thank-you scene: one line per shot (bench / village hall / alley)
for i, t in {'V01': 1.1, 'V02': 8.3, 'V03': 15.9}.items(): put(i, B5 + t, L('policy5_p', i), 'policy5_p')
if prev_end > BE + 0.3: sys.exit('thank-you narration ends too late')
for x in lines: print(f"{x['id']:5s} {x['t']:7.2f}-{x['t'] + x['dur']:7.2f}")
# music: song 1 (stems, arranged) ends on a downbeat early in the activities chapter; song 2 from its own start
SONG1_END = float(os.environ.get('SONG1_END', '132.30' if TITLES else '128.01'))     # 128.01 + 8 beats at 112 BPM (title adds ~4 s in front)
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'stem_arrange_policy.py'), str(round(SONG1_END + 2.6, 3))], check=True, cwd=ROOT,
               env=dict(os.environ, END_AT=str(SONG1_END)))
mus, _ = sf.read(ROOT / 'audio' / 'bgm_policy_arr.wav', dtype='float32')
mus = np.pad(mus, ((0, max(0, int(total * 48000) - len(mus))), (0, 0)))[:int(total * 48000)].copy()
rs = lambda a: np.stack([np.interp(np.arange(int(len(a) * 48000 / 44100)) * 44100 / 48000, np.arange(len(a)), a[:, c]) for c in range(2)], 1)
rms = lambda a: float(np.sqrt((a.astype(np.float64) ** 2).mean()))
s2, sr2 = sf.read(ROOT / 'audio' / 'src_v22_5_dreams.wav', dtype='float32'); s2 = rs(s2) if sr2 != 48000 else s2
SW = SONG1_END + 0.45; s2 = s2[:int((total - SW) * 48000)].copy()
g = rms(mus[int(100 * 48000):int(120 * 48000)]) / rms(s2[int(18 * 48000):int(40 * 48000)]) * 10 ** (-1 / 20); s2 *= g
fi, fo = int(0.8 * 48000), int(3.5 * 48000)
s2[:fi] *= np.linspace(0, 1, fi)[:, None]; s2[-fo:] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, fo)))[:, None]
j = int(SW * 48000); mus[j:j + len(s2)] += s2[:len(mus) - j]
for name, b in (('scene3_src', B3), ('scene4_src', B4), ('scene5_src', B5)):   # each scene's own ambience (no dialogue)
    st = ROOT / 'audio' / 'stems' / 'htdemucs' / name
    a = rs(sum(sf.read(st / f'{k}.wav', dtype='float32')[0] for k in ('drums', 'bass', 'other')))
    i0 = int(b * 48000); n = min(len(a), len(mus) - i0); mus[i0:i0 + n] += a[:n] * 0.7
for name, b in ((('sfx_title_open.wav', B[0]), ('sfx_title_end.wav', BE)) if TITLES else ()):   # pen / stamp sounds of the titles
    fx, _ = sf.read(ROOT / 'audio' / name, dtype='float32'); i0 = int(b * 48000); n = min(len(fx), len(mus) - i0)
    mus[i0:i0 + n] += fx[:n] * 1.4
sf.write(ROOT / 'audio' / 'bgm_policy_v2.wav', mus, 48000, subtype='PCM_16')
nd = ROOT / 'narr' / 'policy_full_p' / vn; nd.mkdir(parents=True, exist_ok=True)
for x in lines:
    l = nd / f"{x['id']}.wav"
    if l.is_symlink() or l.exists(): l.unlink()
    l.symlink_to(Path('..') / '..' / x['src'] / vn / f"{x['id']}.wav")
json.dump(lines, open(ROOT / 'narr' / 'policy' / 'lines_v2_kyle.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
env = dict(os.environ, NARR_LIGHT='1', CARVE_TARGET='14', CARVE_MAX='12', MUSIC_DB='2', NO_SFX='1', TOTAL=str(total),
           NARR_SCRIPT='narr/policy/lines_v2_kyle.json', NARR_DIR='narr/policy_full_p', BGM_FADE=f'{total - 3.5},{total}')
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'mix9.py'), vn, 'policy_v2_kyle', 'off', '0.4', 'bgm_policy_v2.wav'],
               env=env, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
OUT = ROOT / 'deliverables' / 'policy' / '생활공감정책_참여단_kyle_미리보기.mp4'
if os.environ.get('AUDIO_ONLY'):
    tmp = OUT.with_suffix('.tmp.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(OUT), '-i', str(ROOT / 'audio' / 'master_mix9_policy_v2_kyle.wav'), '-map', '0:v',
                    '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(total), '-movflags', '+faststart', str(tmp)], check=True)
    tmp.replace(OUT); print('ok (sound only)', OUT); sys.exit(0)
# picture
inputs, fc = [], []
for k, c in enumerate(CLIPS):
    inputs += ['-i', str(c)]; fc.append(f'[{k}:v]fps=30,settb=1/30,setsar=1,format=yuv420p[v{k}]')
prev = 'v0'
for k in range(1, len(CLIPS)):
    fc.append(f'[{prev}][v{k}]xfade=transition=fade:duration={XF}:offset={B[k]:.3f}[x{k}]'); prev = f'x{k}'
fc.append(f'color=c=black:s=1920x1080:r=30:d={total:.3f},format=rgba[g0]')
glow = [B2, B3, B4, B5]                                          # chapter changes
for k, b in enumerate(glow, 1):
    inputs += ['-loop', '1', '-framerate', '30', '-t', '2.2', '-i', str(P / 'leak.png')]
    fc.append(f'[{inputs.count("-i") - 1}:v]format=rgba,lutrgb=r=val*0.65:g=val*0.65:b=val*0.65,fade=t=in:st=0:d=1.1:alpha=1,'
              f'fade=t=out:st=1.1:d=1.1:alpha=1,setpts=PTS-STARTPTS+{b + XF / 2 - 1.1:.3f}/TB[l{k}]')
    fc.append(f'[g{k - 1}][l{k}]overlay=eof_action=pass[g{k}]')
fc.append(f'[{prev}]format=gbrp[m];[g{len(glow)}]format=gbrp[gl];[m][gl]blend=all_mode=screen:shortest=1,format=yuva420p[b0]')
cl = []
for x in lines:
    if x.get('split'):
        cuts = [0.0] + x['split'] + [x['dur']]
        cl += [dict(id=f"{x['id']}_{k + 1}", t=round(x['t'] + cuts[k], 3), dur=cuts[k + 1] - cuts[k]) for k in range(len(cuts) - 1)]
    else: cl.append(x)
NV = inputs.count('-i'); prev = 'b0'
for i, x in enumerate(cl, 1):
    a = max(0.0, x['t'] - 0.1)
    b = cl[i]['t'] - 0.08 if i < len(cl) else BE + 0.3
    for cut in (B3, B4, B5, BE):
        if x['t'] < cut: b = min(b, cut + 0.25); break
    b = min(b, x['t'] + x['dur'] + 0.6)
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / f"cap_{x['id']}.png")]
    fc.append(f"[{NV + i - 1}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.25:alpha=1,fade=t=out:st={b - 0.25:.2f}:d=0.25:alpha=1[c{i}]")
    fc.append(f'[{prev}][c{i}]overlay=eof_action=pass[o{i}]'); prev = f'o{i}'
fc.append(f'[{prev}]fade=t=out:st={total - 1.0}:d=1.0,format=yuv420p[v]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-i', str(ROOT / 'audio' / 'master_mix9_policy_v2_kyle.wav'),
                '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f"{inputs.count('-i')}:a", '-t', str(total),
                '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(OUT)], check=True)
print('ok', OUT, total, 's')
