# 생활공감정책 film: rebuild each source video as a clean 1920x1080/30 fps "fixed" clip of the SAME length
#   python3 scripts/policy_fix_scenes.py [1 2 3 4]   -> parts/policy/fixed_s1.mp4 ... fixed_s4.mp4
# - every hard cut inside a video becomes a short dissolve (XF_IN s). The length is kept: at each cut the outgoing
#   shot holds its last frame and the incoming shot its first frame for half the dissolve, so nothing shifts in time
#   and every narration line stays where it was
# - glitchy AI shots are replaced by Grok re-takes (gen/v21/p_*_1.mp4) started from a clean frame of the same shot
# - slowed footage uses motion interpolation (in-between frames), not repeated frames
# - the garbled text on the post-office kiosk side is blurred
# scene 4's per-case slow-down (narration longer than footage) is the same as in make_policy_full.py
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / 'src_video'; G = ROOT / 'gen' / 'v21'; P = ROOT / 'parts' / 'policy'
XF_IN = float(os.environ.get('XF_IN', '0.7'))
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
CROP = 'scale=-2:1080:flags=lanczos,crop=1920:1080'
PAD = 'scale=-2:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0:black'
MI = 'minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1'


def shot(src, a, b, length, fit=CROP, extra=''):
    """footage src[a:b] shown for `length` s (slowed with motion interpolation when length > b - a)"""
    k = length / (b - a)
    chain = f'setpts=(PTS-STARTPTS)*{k:.6f},' + (f'{MI},' if k > 1.01 else 'fps=30,')
    return dict(src=str(src), a=a, b=b, chain=chain + f'{fit},setsar=1{extra},format=yuv420p', length=length)


def build(name, shots):
    """lay the shots on one timeline; each next shot fades in (alpha) over the held last frame of the previous one"""
    ins, fc, n = [], [], len(shots)
    # one input per shot, seeked to a whole second before it; the shot itself is cut by frame number (exact)
    for s_ in shots:
        a0 = max(0, int(s_['a']) - 1); ins += ['-ss', str(a0), '-t', f"{s_['b'] - a0 + 1:.3f}", '-i', s_['src']]
        s_['pre'] = f"fps=30,trim=start_frame={round((s_['a'] - a0) * 30)}:end_frame={round((s_['b'] - a0) * 30)},"
    h = XF_IN / 2
    total = sum(s['length'] for s in shots)
    fc.append(f'color=c=black:s=1920x1080:r=30:d={total:.4f},format=yuva420p[base]')
    t, prev = 0.0, 'base'
    for i, s in enumerate(shots):
        pre = h if i else 0.0
        post = h if i < n - 1 else 0.2      # the last shot holds a little so the final frame is never empty
        # one tpad with both pads (two chained tpads lose frames)
        opts = ([f'start_mode=clone:start_duration={pre}'] if pre else []) + ([f'stop_mode=clone:stop_duration={post}'] if post else [])
        pad = (',tpad=' + ':'.join(opts)) if opts else ''
        fade = f',fade=t=in:st=0:d={XF_IN}:alpha=1' if i else ''
        fc.append(f"[{i}:v]{s['pre']}{s['chain']}{pad},trim=duration={s['length'] + pre + post:.4f},format=yuva420p{fade},"
                  f"setpts=PTS-STARTPTS+{t - pre:.4f}/TB[s{i}]")
        fc.append(f'[{prev}][s{i}]overlay=eof_action=pass[o{i}]'); prev = f'o{i}'
        t += s['length']
    out = P / f'fixed_{name}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(fc) + f';[{prev}]format=yuv420p[v]', '-map', '[v]',
                    '-t', f'{total:.4f}', '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', str(out)], check=True)
    print(f'ok {out.name}: {n} shots, {n - 1} dissolves, {total:.3f} s (file {dur(out):.3f})')


def cuts_to_shots(src, cuts, end, fit=CROP, extra=''):
    e = [0.0] + cuts + [end]
    return [shot(src, a, b, b - a, fit, extra) for a, b in zip(e, e[1:])]


which = sys.argv[1:] or ['1', '2', '3', '4', '5']
if '1' in which:   # intro: Grok re-take of the opening; the curb shot uses only its clean part, gently slowed
    v = V / 'policy_intro_src2.mp4'; D = dur(v)
    s = [shot(G / 'p_open_1.mp4', 0, 4.4, 4.4), shot(v, 4.4, 8.9, 10.467 - 4.4)]
    e = [10.467, 13.767, 16.233, 26.3, 28.1, D]
    s += [shot(v, a, b, b - a) for a, b in zip(e, e[1:])]
    build('s1', s)
if '2' in which:   # history photos: the era changes become dissolves (the photo changes inside an era already were)
    v = V / 'policy_scene2_edit.mp4' if (V / 'policy_scene2_edit.mp4').exists() else V / 'policy_scene2.mp4'   # suits re-dressed
    # cut times half a frame early: the edited file's frames sit exactly on the 1/30 s grid, so a cut on the grid
    # would hand the new photo's first frame to the previous shot
    build('s2', cuts_to_shots(v, [15.067, 25.133, 35.2, 45.267, 55.333, 65.4, 75.467, 85.533], dur(v), fit=PAD))
if '3' in which:   # activities: the volunteers-walking shot is a Grok re-take
    v = V / 'policy_scene3.mp4'; D = dur(v)
    build('s3', [shot(v, 0, 10.067, 10.067), shot(G / 'p_walk_1.mp4', 0, 14.367 - 10.067, 14.367 - 10.067),
                 shot(v, 14.367, 20.133, 20.133 - 14.367), shot(v, 20.133, 35.2, 35.2 - 20.133), shot(v, 35.2, D, D - 35.2)])
if '4' in which:   # cases: Grok road-work shot, the three cases with their (narration-driven) speeds, Grok post-office ending
    v = V / 'policy_scene4.mp4'; D = dur(v)
    # per-case speeds: the same rule as make_policy_full.py (footage slows only when its narration is longer)
    d4 = {i: dur(ROOT / 'narr' / 'policy4_p' / 'kyle' / f'{i}.wav') for i in ('U01', 'U02a', 'T02b', 'T03a', 'U03')}
    SEC4 = [0.0, 15.067, 29.067, D]
    need = [0.8 + d4['U01'] + 1.0, 0.4 + d4['U02a'] + 0.45 + d4['T02b'] + 0.6, 0.4 + d4['T03a'] + 0.45 + d4['U03'] + 1.3]
    f1, f2, f3 = (max(1.0, need[k] / (SEC4[k + 1] - SEC4[k])) for k in range(3))
    print(f'scene 4 speeds {1 / f1:.2f}x {1 / f2:.2f}x {1 / f3:.2f}x')
    BLUR = ",split=2[k0][k1];[k1]crop=70:560:1850:180,boxblur=12:2[kb];[k0][kb]overlay=1850:180"   # kiosk side text
    s = [shot(G / 'p_work_1.mp4', 0, 6.04, 6.04 * f1), shot(v, 6.04, 15.067, (15.067 - 6.04) * f1),
         shot(v, 15.067, 29.067, (29.067 - 15.067) * f2),
         shot(v, 29.067, 33.5, (33.5 - 29.067) * f3)]
    # blurred kiosk part needs its own filter chain (split/overlay inside the shot)
    k = shot(v, 33.5, 40.9, (40.9 - 33.5) * f3); k['chain'] = k['chain'].replace(',setsar=1,format=yuv420p', BLUR + ',setsar=1,format=yuv420p')
    s.append(k)
    tail = (D - 29.067) * f3 - sum(x['length'] for x in s[3:])
    s.append(shot(G / 'p_post_1.mp4', 0, 3.04, tail))
    build('s4', s)
if '5' in which:   # thank-you scene: three shots, dissolves between them
    v = V / 'policy_scene5.mp4'
    build('s5', cuts_to_shots(v, [7.6, 15.067], dur(v)))
