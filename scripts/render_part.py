# Render only part of the film (e.g. to review a changed opening/ending) and give it its sound.
#
#   python scripts/render_part.py 0 14          -> parts/part_0-14.mp4      (preview, 8 Mbps, mix = audio/master_mix9_dry.wav)
#   python scripts/render_part.py 173 178 --workers 3
#
# How: a temporary copy of video/index.html is shifted so that second <start> becomes 0
# (every timed element's data-start / data-duration / data-media-start is moved, and the GSAP
# timeline is driven through tl.tweenFromTo(start, end)), then HyperFrames renders just that span.
import argparse, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('start', type=float); ap.add_argument('end', type=float)
ap.add_argument('--workers', default='3'); ap.add_argument('--mix', default='audio/master_mix9_dry.wav')
a = ap.parse_args()
A, B = a.start, a.end
L = round(B - A, 3)
tmp = ROOT / 'parts' / f'_proj_{A:g}-{B:g}'
if tmp.exists(): shutil.rmtree(tmp)
tmp.mkdir(parents=True)
(tmp / 'assets').symlink_to(ROOT / 'video' / 'assets')
for f in ('hyperframes.json', 'meta.json', 'package.json'):
    if (ROOT / 'video' / f).exists(): shutil.copy(ROOT / 'video' / f, tmp / f)
html = (ROOT / 'video' / 'index.html').read_text(encoding='utf-8')
html = re.sub(r'<audio id="mix"[^>]*></audio>', '', html)

def shift(m):
    tag = m.group(0)
    st = float(re.search(r'data-start="([\d.]+)"', tag).group(1))
    du = float(re.search(r'data-duration="([\d.]+)"', tag).group(1))
    if 'data-composition-id="main"' in tag:
        return re.sub(r'data-duration="[\d.]+"', f'data-duration="{L}"', tag, 1)
    s2, e2 = max(st, A), min(st + du, B)
    if e2 <= s2:                                   # not on screen in this span: park it after the end
        s2, e2 = L + 1, L + 1.01
        new = tag
    else:
        new = tag
        ms = re.search(r'data-media-start="([\d.]+)"', tag)
        if ms and st < A:
            new = new.replace(ms.group(0), f'data-media-start="{float(ms.group(1)) + (A - st):.3f}"')
        s2, e2 = s2 - A, e2 - A
    new = re.sub(r'data-start="[\d.]+"', f'data-start="{s2:.3f}"', new, 1)
    new = re.sub(r'data-duration="[\d.]+"', f'data-duration="{e2 - s2:.3f}"', new, 1)
    return new

html = re.sub(r'<(?:div|video)[^>]*data-start="[\d.]+"[^>]*data-duration="[\d.]+"[^>]*>', shift, html)
html = html.replace("window.__timelines['main'] = tl;",
                    f"const outer = gsap.timeline({{ paused: true }});\nouter.add(tl.tweenFromTo({A}, {B}, {{ ease: 'none' }}), 0);\nwindow.__timelines['main'] = outer;")
(tmp / 'index.html').write_text(html, encoding='utf-8')

out_dir = ROOT / 'parts'
silent = out_dir / f'_silent_{A:g}-{B:g}.mp4'
subprocess.run(['npx', '--yes', 'hyperframes@0.8.164', 'render', '-f', '30', '-q', 'delivery', '-w', str(a.workers),
                '-o', str(silent), '--browser-timeout', '180'], cwd=tmp, check=True)
dst = out_dir / f'part_{A:g}-{B:g}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(silent), '-ss', str(A), '-t', str(L), '-i', str(ROOT / a.mix),
                '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-b:v', '8M', '-maxrate', '10M', '-bufsize', '16M', '-preset', 'medium',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', str(L), str(dst)], check=True)
print('ok', dst)
