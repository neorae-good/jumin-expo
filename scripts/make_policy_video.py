# 생활공감정책 참여단 intro on the producer's 30.5 s video, for one voice.
#   python scripts/make_policy_video.py kyle <video.mp4>  -> deliverables/policy/생활공감정책_인트로_영상_kyle_미리보기.mp4
# The narration is fitted to the video only by shortening the pauses between lines (the recordings are not
# stretched): lines from narr/policy_p/<voice> (scripts/pick_policy.py), captions from parts/policy (policy_caps.js).
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
vn, VID = sys.argv[1], sys.argv[2]
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
total = round(dur(VID), 3)
lines = json.load(open(ROOT / 'narr' / 'policy' / 'script.json', encoding='utf-8'))
for x in lines: x['dur'] = round(dur(ROOT / 'narr' / 'policy_p' / vn / f"{x['id']}.wav"), 3)
START, TAIL = 0.4, 1.0
W = {'P01': 1.0, 'P02': 1.2, 'P03': 1.2, 'P04': 1.0, 'P05': 0.9}     # a little more air around the inner question
free = total - START - TAIL - sum(x['dur'] for x in lines)
if free < 0: sys.exit(f'{vn}: speech {sum(x["dur"] for x in lines):.2f} s does not fit {total} s')
unit = free / sum(W.values())
t = START
for x in lines:
    x['t'] = round(t, 3); t += x['dur'] + W.get(x['id'], 0) * unit
if os.environ.get('STARTS'):   # e.g. STARTS=P01:0.3,P02:4.4 : lines start on the video's scene cuts
    for kv in os.environ['STARTS'].split(','):
        k, v = kv.split(':'); next(x for x in lines if x['id'] == k)['t'] = float(v)
    for a, b in zip(lines, lines[1:]):
        if b['t'] - (a['t'] + a['dur']) < 0.3: sys.exit(f"{a['id']}->{b['id']}: pause {b['t'] - a['t'] - a['dur']:.2f} s too short")
    if lines[-1]['t'] + lines[-1]['dur'] > total - 0.8: sys.exit('last line ends too late')
    print('starts', ', '.join(f"{x['id']} {x['t']:.2f}-{x['t'] + x['dur']:.2f}" for x in lines))
print(f"{vn}: speech {sum(x['dur'] for x in lines):.2f} s, pauses {', '.join(f'{W[k] * unit:.2f}' for k in W)} s")
json.dump(lines, open(ROOT / 'narr' / 'policy' / f'lines_fit_{vn}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
env = dict(os.environ, NARR_LIGHT='1', CARVE_TARGET='14', CARVE_MAX='12', MUSIC_DB='2', NO_SFX='1', TOTAL=str(total),
           NARR_SCRIPT=f'narr/policy/lines_fit_{vn}.json', NARR_DIR='narr/policy_p', BGM_FADE=f'{total - 2.5},{total}')
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'mix9.py'), vn, f'policyv_{vn}', 'off', '0.4', 'bgm_v29_arr.wav'],
               env=env, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
P = ROOT / 'parts' / 'policy'
inputs = ['-i', VID]
fc = ['[0:v]fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,format=yuva420p[b0]']
prev = 'b0'
for i, x in enumerate(lines, 1):
    a = max(0.0, x['t'] - 0.1)
    b = lines[i]['t'] - 0.08 if i < len(lines) else total - 0.3
    b = min(b, x['t'] + x['dur'] + 0.6)
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / f"cap_{x['id']}.png")]
    fc.append(f"[{i}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.25:alpha=1,fade=t=out:st={b - 0.25:.2f}:d=0.25:alpha=1[c{i}]")
    fc.append(f'[{prev}][c{i}]overlay=eof_action=pass[o{i}]'); prev = f'o{i}'
fc.append(f'[{prev}]fade=t=out:st={total - 0.6}:d=0.6,format=yuv420p[v]')
out = ROOT / 'deliverables' / 'policy' / (os.environ.get('OUTNAME') or f'생활공감정책_인트로_영상_{vn}_미리보기.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-i', str(ROOT / 'audio' / f'master_mix9_policyv_{vn}.wav'),
                '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f'{len(lines) + 1}:a', '-t', str(total),
                '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)
print('ok', out)
