# 생활공감정책 참여단 intro preview for one voice: mix (mix9, light compression) + captions over a plain background.
#   python scripts/make_policy_preview.py kyle   -> deliverables/policy/생활공감정책_인트로_kyle_미리보기.mp4
# needs: scripts/pick_policy.py <voice> (lines + timing), node scripts/policy_caps.js (caption PNGs, background)
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
vn = sys.argv[1]
S = json.load(open(ROOT / 'narr' / 'policy' / f'script_{vn}.json', encoding='utf-8'))
total, L = S['total'], S['lines']
env = dict(os.environ, NARR_LIGHT='1', CARVE_TARGET='14', CARVE_MAX='12', MUSIC_DB='2', NO_SFX='1', TOTAL=str(total),
           NARR_SCRIPT=f'narr/policy/lines_{vn}.json', NARR_DIR='narr/policy_p', BGM_FADE=f'{total - 3.5},{total - 0.3}')
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'mix9.py'), vn, f'policy_{vn}', 'off', '0.4', 'bgm_v29_arr.wav'],
               env=env, check=True, cwd=ROOT)
P = ROOT / 'parts' / 'policy'
inputs = ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / 'bg.png')]
fc = [f'[0:v]scale=2112:-1,crop=1920:1080:(iw-1920)/2*(1-t/{total}):(ih-1080)/2,format=yuva420p[b0]']
prev = 'b0'
for i, x in enumerate(L, 1):
    a = max(0.0, x['t'] - 0.15)
    nxt = L[i]['t'] - 0.25 if i < len(L) else total - 1.0
    b = min(x['t'] + x['dur'] + 0.6, nxt)
    inputs += ['-loop', '1', '-framerate', '30', '-t', str(total), '-i', str(P / f"cap_{x['id']}.png")]
    fc.append(f"[{i}:v]format=rgba,fade=t=in:st={a:.2f}:d=0.3:alpha=1,fade=t=out:st={b - 0.3:.2f}:d=0.3:alpha=1[c{i}]")
    fc.append(f'[{prev}][c{i}]overlay=shortest=1[o{i}]'); prev = f'o{i}'
fc.append(f'[{prev}]fade=t=in:st=0:d=0.8,fade=t=out:st={total - 1.2}:d=1.2,format=yuv420p[v]')
out = ROOT / 'deliverables' / 'policy' / f'생활공감정책_인트로_{vn}_미리보기.mp4'
out.parent.mkdir(parents=True, exist_ok=True)
na = len(L) + 1
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-i', str(ROOT / 'audio' / f'master_mix9_policy_{vn}.wav'),
                '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f'{na}:a', '-t', str(total),
                '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out)], check=True)
print('ok', out, total, 's')
