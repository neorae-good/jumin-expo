# v30: end sky clip with the cloth raised and "주민자치" embroidered into it, riding the cloth's own motion.
#   python3 scripts/cloth_text_v30.py [lift] -> video/assets/video/v30_e1_sky_text.mp4
# How: the clip is enlarged (bottom kept) so the cloth sits higher. The letters are drawn once; every frame a dense
# optical flow (Farneback) tells where each pixel of the cloth came from, and the letter map is carried along with it
# (with a slow pull back to rest so the word never drifts away). Each frame the letters take the cloth's own light,
# shade and creases, so they bend and dim with the folds like stitching.
import subprocess, sys
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'video' / 'assets' / 'video' / 'v21_e1_sky.mp4'
OUT = ROOT / 'video' / 'assets' / 'video' / 'v30_e1_sky_text.mp4'
LIFT = float(sys.argv[1]) if len(sys.argv) > 1 else 1.25
W, H = 1920, 1080
TXT, SIZE, CX, CY = '주민자치', 210, 0.5, 0.64
DECAY = 0.985          # pull back to rest per frame
FS = 2                 # flow computed at 1/FS resolution

font = ImageFont.truetype(str(ROOT / 'fonts_dl' / 'pre' / 'Pretendard-Bold.ttf'), SIZE)
L = Image.new('L', (W, H), 0); d = ImageDraw.Draw(L)
bb = d.textbbox((0, 0), TXT, font=font); tw, th = bb[2] - bb[0], bb[3] - bb[1]
cx, cy = CX * W, CY * H
d.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1]), TXT, font=font, fill=255)
M0 = np.asarray(L.filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
stripe = (0.92 + 0.08 * np.sin((xx * 0.8 + yy * 1.6) * 0.9))[..., None]
GOLD = np.array([0.70, 0.93, 1.0], np.float32)            # BGR of a cream-gold thread

dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(SRC), '-vf',
                        f'scale={int(W * LIFT)}:{int(H * LIFT)}:flags=lanczos,crop={W}:{H}:(iw-{W})/2:ih-{H}',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30',
                        '-i', '-', '-c:v', 'libx264', '-crf', '14', '-preset', 'slow', '-pix_fmt', 'yuv420p', str(OUT)],
                       stdin=subprocess.PIPE)
PX, PY = xx.copy(), yy.copy()        # where each output pixel sits in the rest (frame 0) letter map
prev = None; n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    g = cv2.cvtColor(cv2.resize(f, (W // FS, H // FS), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    if prev is not None:
        fl = cv2.calcOpticalFlowFarneback(g, prev, None, 0.5, 4, 31, 3, 7, 1.5, 0)   # current -> previous
        fl = cv2.resize(fl, (W, H)) * FS
        fl = cv2.GaussianBlur(fl, (0, 0), 14)
        mx, my = xx + fl[..., 0], yy + fl[..., 1]
        PX = cv2.remap(PX, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        PY = cv2.remap(PY, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # keep the letters whole: the displacement field is smoothed every frame (bends, never tears)
        PX = xx + DECAY * cv2.GaussianBlur(PX - xx, (0, 0), 22); PY = yy + DECAY * cv2.GaussianBlur(PY - yy, (0, 0), 22)
    prev = g
    m = cv2.remap(M0, PX, PY, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    base = f.astype(np.float32) / 255
    lum = base.mean(2, keepdims=True)
    blur = cv2.GaussianBlur(lum[..., 0], (0, 0), 18)[..., None]
    shade = np.clip(0.55 + 0.45 * lum / max(float(np.percentile(lum, 70)), 1e-3), 0.72, 1.12)
    detail = np.clip(lum / np.maximum(blur, 1e-3), 0.8, 1.2)
    thread = 0.88 * GOLD * shade * stripe * detail + 0.12 * base * 1.3
    rim = np.clip(np.roll(m, 4, 0) + np.roll(m, 2, 1) - 2 * m, 0, 1)[..., None]
    A = 0.93 * m[..., None]
    o = base * (1 - 0.6 * rim)
    o = o * (1 - A) + thread * A
    enc.stdin.write((np.clip(o, 0, 1) * 255).astype(np.uint8).tobytes()); n += 1
enc.stdin.close(); enc.wait()
print('ok', OUT, n, 'frames')
