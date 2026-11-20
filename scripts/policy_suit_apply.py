# 생활공감정책 film: put the edited photos (scripts/policy_suit_inpaint.py) back into the moving scene-2 slideshow.
#   python3 scripts/policy_suit_apply.py   -> src_video/policy_scene2_edit.mp4 (same size, length and motion as the original)
# The slideshow slowly zooms/pans each photo and cross-fades between photos, so per frame:
#  - an affine transform from the reference frame to the current frame is estimated (OpenCV ECC),
#  - the edit (edited - original reference, only inside the edited regions) is warped with it and added,
#  - its strength follows how clearly the photo is on screen (1 while shown, fading with the cross-fades).
import json, subprocess, sys
from pathlib import Path
import numpy as np, cv2

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src_video' / 'policy_scene2.mp4'; OUT = ROOT / 'src_video' / 'policy_scene2_edit.mp4'
D = ROOT / 'parts' / 'policy' / 'suit'
SPEC = json.loads((ROOT / 'scripts' / 'policy_suit_spec.json').read_text(encoding='utf-8'))
PICK = json.loads((D / 'picks.json').read_text()) if (D / 'picks.json').exists() else {}
W, H = 1620, 1080; S = 4                       # ECC on a 1/4-size grey image
# pass 1: only small grey frames are kept in memory (the full video does not fit)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(SRC), '-vf', f'scale={W // S}:{H // S}:flags=area', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
                     capture_output=True, check=True).stdout
G = list(np.frombuffer(raw, np.uint8).reshape(-1, H // S, W // S).astype(np.float32) / 255)
N = len(G); fps = 30.0
small = lambda im: cv2.resize(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY), (W // S, H // S), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 60, 1e-5)
LOGO = np.zeros((H, W), np.float32); LOGO[845:1055, 1200:1515] = 1; LOGO = cv2.GaussianBlur(LOGO, (0, 0), 6)
plan = {}                                       # frame -> list of (edit k, alpha, 2x3 affine at full res)
for k, sp in SPEC.items():
    ref = cv2.cvtColor(cv2.imread(str(D / sp['ref'])), cv2.COLOR_BGR2RGB)
    ed = cv2.cvtColor(cv2.imread(str(D / f"edit{k}_final.png")), cv2.COLOR_BGR2RGB)   # per-region picks (picks_region.json)
    diff = ed.astype(np.float32) - ref.astype(np.float32)
    m = (np.abs(diff).max(2) > 6).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0)
    g0 = small(ref); i0 = int(round(sp['src_t'] * fps))
    res = {}
    for direction in (1, -1):                   # walk out from the reference frame while the photo is recognisable
        A = np.eye(2, 3, dtype=np.float32); i = i0 if direction == 1 else i0 - 1
        while 0 <= i < N:
            # strong zoom-ins leave much of the reference outside the frame, so also try the inverse direction
            # (frame as template) and keep whichever matches better
            try: cc, A1 = cv2.findTransformECC(g0, G[i], A.copy(), cv2.MOTION_AFFINE, crit, None, 5)
            except cv2.error: cc, A1 = 0.0, A
            try:
                Ainv = cv2.invertAffineTransform(A)
                cc2, B1 = cv2.findTransformECC(G[i], g0, Ainv.copy(), cv2.MOTION_AFFINE, crit, None, 5)
                if cc2 > cc: cc, A1 = cc2, cv2.invertAffineTransform(B1)
            except cv2.error: pass
            A = A1.astype(np.float32)
            if cc < 0.6 or abs(i - i0) > 12 * fps: break   # stop once another photo has taken over
            res[i] = (cc, A.copy()); i += direction
    fr = sorted(res); cc = np.array([res[i][0] for i in fr])
    full = cc >= 0.93 * cc.max()
    a0, a1 = fr[np.argmax(full)], fr[len(full) - 1 - np.argmax(full[::-1])]
    lo, hi = fr[0], fr[-1]
    lo, hi = max(lo, a0 - int(1.2 * fps)), min(hi, a1 + int(1.2 * fps))   # cross-fades last about a second
    fr = [i for i in fr if lo <= i <= hi]
    for i in fr:                                 # strength: 1 while shown, linear ramps through the cross-fades
        al = 1.0 if a0 <= i <= a1 else ((i - lo) / max(1, a0 - lo) if i < a0 else (hi - i) / max(1, hi - a1))
        A = res[i][1].copy(); A[:, 2] *= S
        plan.setdefault(i, []).append((k, float(np.clip(al, 0, 1)), A))
    globals()[f'diff{k}'] = (diff, mask, ed.astype(np.float32), any(r[4] == 'erase' for r in sp['regions']))
    print(f'photo {k}: frames {lo / fps:.2f}-{hi / fps:.2f} s, full {a0 / fps:.2f}-{a1 / fps:.2f} s, best match {cc.max():.3f}', flush=True)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', str(OUT)], stdin=subprocess.PIPE)
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(SRC), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
for i in range(N):   # pass 2: stream full frames
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    for k, al, A in plan.get(i, []):
        diff, mask, ed, logo = globals()[f'diff{k}']
        wd = cv2.warpAffine(diff, A, (W, H), flags=cv2.INTER_LINEAR)
        wm = cv2.warpAffine(mask, A, (W, H), flags=cv2.INTER_LINEAR)
        f += wd * (wm * al)[..., None]
        if logo:   # the newspaper logo is burned in at a fixed screen spot: there, show the moving photo without it
            we = cv2.warpAffine(ed, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
            f = f * (1 - LOGO[..., None] * al) + we * (LOGO[..., None] * al)
    enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('ok', OUT.name, N, 'frames')
