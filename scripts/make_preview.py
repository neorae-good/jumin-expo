# Full-length preview for one opening/ending variant without re-rendering the unchanged middle.
#
#   python scripts/make_preview.py a 1안              (JV=a,  mix audio/master_mix9_dry.wav)
#   python scripts/make_preview.py gv 2안
#   python scripts/make_preview.py m 3안 audio/master_mix9_dry_m.wav
#
# 1) build video/index.html with JV=<variant>
# 2) render only 0-21 s and 161-178 s (scripts/render_part.py)
# 3) splice them around 21-161 s of the last full render (video/renders/jumin-expo-v20.mp4; that span is
#    identical in every variant) -> frame-exact concat, attach the mix, encode the 8 Mbps preview
import os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
jv, label = sys.argv[1], sys.argv[2]
mix = sys.argv[3] if len(sys.argv) > 3 else 'audio/master_mix9_dry.wav'
MID = ROOT / 'video' / 'renders' / 'jumin-expo-v20.mp4'
A, B = 21, 161                       # seconds taken from the full render
env = dict(os.environ, JV=jv)
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build8.py')], env=env, check=True)
for s, e in ((0, A), (B, 178)):
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'render_part.py'), str(s), str(e), '--mix', mix], check=True)
p1, p3 = ROOT / 'parts' / f'_silent_0-{A}.mp4', ROOT / 'parts' / f'_silent_{B}-178.mp4'
out = ROOT / 'deliverables' / 'v21' / f'주민자치박람회_주제영상_v21_{label}_미리보기.mp4'
out.parent.mkdir(parents=True, exist_ok=True)
fc = (f'[0:v]trim=start_frame=0:end_frame={A * 30},setpts=PTS-STARTPTS[a];'
      f'[1:v]trim=start_frame={A * 30}:end_frame={B * 30},setpts=PTS-STARTPTS[b];'
      f'[2:v]trim=start_frame=0:end_frame={(178 - B) * 30},setpts=PTS-STARTPTS[c];'
      '[a][b][c]concat=n=3:v=1:a=0,format=yuv420p[v]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(p1), '-i', str(MID), '-i', str(p3), '-i', str(ROOT / mix),
                '-filter_complex', fc, '-map', '[v]', '-map', '3:a', '-r', '30', '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M',
                '-bufsize', '16M', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', '178', str(out)], check=True)
print('ok', out)
