# warm light-leak frame for the 생활공감정책 film's chapter transitions (TRANS=glow in make_policy_full.py)
#   python3 scripts/policy_leak.py -> parts/policy/leak.png
# soft orange glow from the upper left, a fainter one lower right, and a light diagonal streak
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
W, H = 1920, 1080
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
g1 = np.exp(-(((x - 520) / 900) ** 2 + ((y - 260) / 620) ** 2))
g2 = np.exp(-(((x - 1450) / 700) ** 2 + ((y - 820) / 500) ** 2)) * 0.45
streak = np.exp(-((((x - 960) * 0.42 + (y - 540) * 0.9) / 140) ** 2)) * 0.35
v = np.clip(g1 + g2 + streak, 0, 1)[..., None]
img = (v * np.array([255, 196, 128], np.float32)).astype(np.uint8)
(ROOT / 'parts' / 'policy').mkdir(parents=True, exist_ok=True)
Image.fromarray(img).save(ROOT / 'parts' / 'policy' / 'leak.png')
print('ok parts/policy/leak.png')
