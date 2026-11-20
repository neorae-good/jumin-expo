# 생활공감정책 film, scene 2 photos: the people in suits get clothes like the people around them (faces untouched),
# and the 일요신문 logo is removed. Open-source Stable Diffusion 1.5 inpainting, run on the CPU.
#   python3 scripts/policy_suit_inpaint.py [photo ids]  -> parts/policy/suit/edit<k>_c<n>.png (candidates) + sheet
# Each region is inpainted in a crop around it (context), then pasted back with a soft edge.
import json, sys, time
from pathlib import Path
import numpy as np, torch, cv2
from PIL import Image, ImageFilter, ImageDraw
from diffusers import StableDiffusionInpaintPipeline

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'parts' / 'policy' / 'suit'
torch.set_num_threads(4)
NEG = ('suit, necktie, tie, blazer, formal wear, lapel, badge, deformed, extra arms, extra hands, blurry, text, watermark, '
       'logo, cartoon, painting, distorted face, lowres')
CASUAL = 'photo of a middle-aged Korean man wearing a plain {c}, no necktie, natural daylight, realistic fabric, high quality photo'
# photo id: (reference frame, [(x0, y0, x1, y1, clothing or 'erase')])
SPEC = json.loads((ROOT / 'scripts' / 'policy_suit_spec.json').read_text(encoding='utf-8'))
pipe = StableDiffusionInpaintPipeline.from_pretrained('stable-diffusion-v1-5/stable-diffusion-inpainting', variant='fp16',
                                                      torch_dtype=torch.float32, safety_checker=None, requires_safety_checker=False)
pipe.set_progress_bar_config(disable=True)
N_CAND = int(__import__('os').environ.get('N_CAND', '2')); STEPS = int(__import__('os').environ.get('STEPS', '24'))


def region_mask(img, box, clothing, mode):
    """only the garment: inside the box keep the dark suit pixels (or the red jacket), closed and filled, so the
    background behind the person is never redrawn; 'box' (logo) uses the whole box"""
    x0, y0, x1, y1 = box
    full = np.zeros((img.height, img.width), np.uint8)
    if mode == 'box' or clothing == 'erase':
        full[y0:y1, x0:x1] = 255
    else:
        hsv = cv2.cvtColor(np.asarray(img.crop(box)), cv2.COLOR_RGB2HSV)
        if mode == 'red': sel = (((hsv[..., 0] < 10) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 110)) | (hsv[..., 2] < 60)
        else: sel = (hsv[..., 2] < 100) & (hsv[..., 1] < 140)            # dark suit cloth
        m = sel.astype(np.uint8) * 255
        k = max(5, (x1 - x0) // 25) | 1
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 0.04 * m.size]
        m = np.isin(lab, keep).astype(np.uint8) * 255
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)          # fill holes (shirt, tie)
        m = np.zeros_like(m); cv2.drawContours(m, cs, -1, 255, -1)
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
        full[y0:y1, x0:x1] = m
    return Image.fromarray(full)


def inpaint(img, box, clothing, seed, mode='dark'):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    m = int(max(w, h) * 0.45)                                       # context around the region
    cx0, cy0 = max(0, x0 - m), max(0, y0 - m); cx1, cy1 = min(img.width, x1 + m), min(img.height, y1 + m)
    crop = img.crop((cx0, cy0, cx1, cy1))
    s = 512 / max(crop.size); W8, H8 = (int(crop.width * s) // 8 * 8, int(crop.height * s) // 8 * 8)
    mask = region_mask(img, box, clothing, mode).crop((cx0, cy0, cx1, cy1))
    if clothing == 'erase':
        prompt, neg = 'empty grey carpet floor and the lower part of people sitting on chairs, realistic photo', NEG + ', letters, sign'
    else:
        prompt, neg = CASUAL.format(c=clothing), NEG
    out = pipe(prompt=prompt, negative_prompt=neg, image=crop.resize((W8, H8), Image.LANCZOS), mask_image=mask.resize((W8, H8)),
               width=W8, height=H8, num_inference_steps=STEPS, guidance_scale=7.5, strength=1.0,
               generator=torch.Generator().manual_seed(seed)).images[0].resize(crop.size, Image.LANCZOS)
    soft = mask.filter(ImageFilter.GaussianBlur(max(2, int(min(w, h) * 0.02))))
    res = img.copy(); res.paste(Image.composite(out, crop, soft), (cx0, cy0))
    return res


ids = sys.argv[1:] or list(SPEC)
for k in ids:
    ref, regions = SPEC[k]['ref'], SPEC[k]['regions']
    base = Image.open(D / ref).convert('RGB')
    for n in range(N_CAND):
        t = time.time(); img = base
        for j, r in enumerate(regions):
            img = inpaint(img, tuple(r[:4]), r[4], seed=1000 * n + 17 * j + 3, mode=r[5] if len(r) > 5 else 'dark')
        img.save(D / f'edit{k}_c{n}.png'); print(f'{k} candidate {n}: {time.time() - t:.0f} s', flush=True)
