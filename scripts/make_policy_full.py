# 생활공감정책 참여단: intro (30.2 s) + scene 2 history (95.6 s) in one film, Kyle narration, music, captions.
#   python scripts/make_policy_full.py src_video/policy_intro_src2.mp4 src_video/policy_scene2.mp4
#   -> deliverables/policy/생활공감정책_인트로+장면2_kyle_미리보기.mp4
# Intro lines keep their scene-cut starts. Scene 2 has one section per era (10 sections); each paragraph starts just
# after its section begins (or after the previous paragraph if that one ran over). Recordings are never stretched.
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1, V2 = sys.argv[1], sys.argv[2]
vn = 'kyle'
dur = lambda f: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                                     capture_output=True, text=True).stdout)
D1, D2 = dur(V1), dur(V2)
total = round(D1 + D2, 3)
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
    nxt = D1 + SECT[k + 1] if k < 9 else total
    print(f"Q{k + 1:02d}: {lines[-len(para)]['t']:.2f}-{end:.2f} s (section {D1 + SECT[k]:.2f}-{nxt:.2f}){'  runs over by %.2f' % (end - nxt) if end > nxt else ''}")
if end > total - 1.0: sys.exit('last line ends too late')
# one folder of line wavs for mix9
nd = ROOT / 'narr' / 'policy_full_p' / vn; nd.mkdir(parents=True, exist_ok=True)
for x in lines:
    l = nd / f"{x['id']}.wav"
    if l.is_symlink() or l.exists(): l.unlink()
    l.symlink_to(Path('..') / '..' / x['src'] / vn / f"{x['id']}.wav")
json.dump(lines, open(ROOT / 'narr' / 'policy' / 'lines_full_kyle.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
env = dict(os.environ, NARR_LIGHT='1', CARVE_TARGET='14', CARVE_MAX='12', MUSIC_DB='2', NO_SFX='1', TOTAL=str(total),
           NARR_SCRIPT='narr/policy/lines_full_kyle.json', NARR_DIR='narr/policy_full_p', BGM_FADE=f'{total - 3.0},{total}')
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'mix9.py'), vn, 'policyfull_kyle', 'off', '0.4', 'bgm_v29_arr.wav'],
               env=env, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
P = ROOT / 'parts' / 'policy'
inputs = ['-i', V1, '-i', V2]
fc = [f'[0:v]fps=30,scale=-2:1080:flags=lanczos,crop=1920:1080,setsar=1,fade=t=out:st={D1 - 0.5:.3f}:d=0.5[a]',
      f'[1:v]fps=30,scale=-2:1080:flags=lanczos,pad=1920:1080:(ow-iw)/2:0:black,setsar=1,fade=t=in:st=0:d=0.5[b]',
      '[a][b]concat=n=2:v=1:a=0,format=yuva420p[b0]']
prev = 'b0'
for i, x in enumerate(lines, 1):
    a = max(0.0, x['t'] - 0.1)
    b = lines[i]['t'] - 0.08 if i < len(lines) else total - 0.5
    b = min(b, x['t'] + x['dur'] + 0.6)
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / f"cap_{x['id']}.png")]
    fc.append(f"[{i + 1}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.25:alpha=1,fade=t=out:st={b - 0.25:.2f}:d=0.25:alpha=1[c{i}]")
    fc.append(f'[{prev}][c{i}]overlay=eof_action=pass[o{i}]'); prev = f'o{i}'
fc.append(f'[{prev}]fade=t=out:st={total - 1.0}:d=1.0,format=yuv420p[v]')
out = ROOT / 'deliverables' / 'policy' / '생활공감정책_인트로+장면2_kyle_미리보기.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-i', str(ROOT / 'audio' / 'master_mix9_policyfull_kyle.wav'),
                '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f'{len(lines) + 2}:a', '-t', str(total),
                '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)
print('ok', out, total, 's')
