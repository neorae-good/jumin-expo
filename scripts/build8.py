"""v3 build: richer direction (3D quilt, Three.js waving cloth, glowing map, light FX, narration).

Writes video/index.html from photos.json, geo/gyeongnam.json, narr/script.json.
Timeline: scripts/main2.js (GSAP, inlined). Cloth: scripts/cloth.js (Three.js module, inlined).
"""
import json, math, random, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VID = ROOT / 'video'
regions = json.load(open(ROOT / 'photos.json', encoding='utf-8'))
geo = json.load(open(ROOT / 'geo' / 'gyeongnam.json', encoding='utf-8'))
narr = json.load(open(ROOT / 'narr' / 'script6.json', encoding='utf-8'))

NAMES = ['창원시', '진주시', '통영시', '사천시', '김해시', '밀양시', '거제시', '양산시', '의령군',
         '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군']
COLORS = ['#2f4f7f', '#b5473c', '#d29f36', '#5f8048', '#7d4466', '#3e7f7a', '#c4705f', '#4a5f8f', '#a8763a']
rng = random.Random(18)
TOTAL = 178
T = {'s2': 19.0, 'a0': 23.4, 'astep': 5.4, 'pb': 70.0, 's2end': 75.5, 'v5': 74.6, 'v5d': 9.6, 'big': 83.3, 'flsw': 120.6, 'wide0': 131.0, 's3end': 140.0, 's3': 83.3, 'b0': 86.6, 'bstep': 5.0, 'throw': 139.2, 'ph': 149.6, 'phd': 4.6, 'fin': 162.4, 'end': 178}

def dur(f):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)

for x in narr:
    # one picture for both voices: captions hold until the longer of the two readings ends
    x['d'] = round(max(dur(ROOT / 'narr' / 'v8p' / v / f"{x['id']}.wav") for v in ('bomi', 'kanika')), 2)

TXT = {
    'k1': '기', 'k1s': '첫 바늘땀',
    'k2': '승', 'k2s': '조각이 하나씩',
    'k3': '전', 'k3s': '이어져 하나의 천으로',
    'k4': '결', 'k4s': '수놓다',
    'fin1': '주민의 힘으로,',
    'fin2': '경상남도가 도약하다',
    'fin3': '2026년 제8회 경상남도 주민자치 박람회',
}
# v21: opening (0-19 s) and ending (162.4-178 s) built from the quilt itself, no AI clips.
# Two design variants for review:  JV=a python scripts/build8.py  (quilt cloth, default)
#                                  JV=b python scripts/build8.py  (photo collage)
import os
JV = os.environ.get('JV', 'a')
IT = {'t1': '첫 땀', 's1': '새벽을 여는 손끝에서', 't2': '땀 한 방울', 's2': '마을을 잇는 첫 바늘땀',
      't3a': '한 조각씩,', 't3b': '하나의 천으로'}

# ------------------------------------------------------------------ 승: 3D quilt world
M = 2400                     # decorative margin around the 3x3 cells
CW, CH = 1920, 1080
WW, WH = 3 * CW + 2 * M, 6 * CH + 2 * M
S2_ORDER = [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (1, 3), (0, 3), (0, 4), (1, 4), (2, 4), (2, 5), (1, 5), (0, 5)]
SEAM = 24
# cell layout: tag (top-left), photo A (bottom-left), photo B (top-right), photo C (bottom-right)
CELL = {'tag': (40, 40, 560, 190), 'A': (40, 250, 720, 790), 'B': (784, 40, 1096, 500), 'C': (784, 560, 1096, 500)}

def mirror(r, flip):
    x, y, w, h = r
    return (CW - x - w, y, w, h) if flip else r

def stitch_svg(pid, w, h, inset=11, color='#ffd27a', glow=True):
    return f'''<svg class="st" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs><mask id="{pid}-m"><rect x="{inset}" y="{inset}" width="{w-2*inset}" height="{h-2*inset}" fill="none" stroke="#fff" stroke-width="10" pathLength="1" stroke-dasharray="1 0" stroke-dashoffset="1" id="{pid}-mr"/></mask></defs>
  <rect x="{inset}" y="{inset}" width="{w-2*inset}" height="{h-2*inset}" fill="none" stroke="{color}" stroke-width="3.2" stroke-dasharray="12 8" stroke-linecap="round" mask="url(#{pid}-m)" class="{'glowst' if glow else ''}"/>
</svg>'''

def photo_patch(pid, x, y, w, h, photo, color, cap=''):
    return f'''<div class="qp" id="{pid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{color}">
  <div class="qfab"></div><div class="qph"><img id="{pid}-img" src="assets/photos/{photo}" alt=""></div>
  <div class="qcap"><span>{cap}</span></div>
  {stitch_svg(pid, w, h)}
</div>'''

def tag_patch(tid, x, y, w, h, num, name, color):
    return f'''<div class="qt" id="{tid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{color}">
  <div class="qt-in"><span class="num">{num:02d}</span><span class="nm">{name}</span></div>
  {stitch_svg(tid, w, h, inset=16, color='#b8862e', glow=False)}
</div>'''

s2_html, s2_cells = [], []
# filler patchwork across the whole world (under everything)
filler = []
for k in range(18):
    cx, cy = S2_ORDER[k]
    flip = k % 2 == 1
    ox, oy = M + cx * CW, M + cy * CH
    reg = regions[k]
    ids = []
    for j, key in enumerate(['A', 'B', 'C']):
        x, y, w, h = mirror(CELL[key], flip)
        pid = f'q{k}{j}'
        s2_html.append(photo_patch(pid, ox + x, oy + y, w, h, reg['photos'][j]['file'], COLORS[(k * 3 + j) % len(COLORS)], reg['photos'][j]['cap']))
        ids.append(pid)
    x, y, w, h = mirror(CELL['tag'], flip)
    tid = f'qt{k}'
    s2_html.append(tag_patch(tid, ox + x, oy + y, w, h, k + 1, NAMES[k], COLORS[(k * 3 + 2) % len(COLORS)]))
    s2_cells.append({'cx': cx, 'cy': cy, 'p': ids, 't': tid, 'flip': flip})

# ------------------------------------------------------------------ 결: map pieces
MAP_SCALE = 0.86
MAP_W, MAP_H = geo['w'] * MAP_SCALE, geo['h'] * MAP_SCALE
from PIL import Image, ImageStat
def lum(ph):
    im = Image.open(VID / 'assets' / 'photos' / ph['file']).convert('L').resize((64, 64))
    return ImageStat.Stat(im).mean[0] * (1.0 if ph['w'] >= ph['h'] else 0.8)
map_html, map_regs = [], []
for k, reg in enumerate(regions):
    g = geo['regions'][reg['ko']]
    x0, y0, x1, y1 = g['bbox']
    pad = 6
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
    w, h = x1 - x0, y1 - y0
    big = max(reg['photos'], key=lum)
    map_html.append(f'''<svg class="mreg" id="mr{k}" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" style="left:{x0*MAP_SCALE:.1f}px;top:{y0*MAP_SCALE:.1f}px;width:{w*MAP_SCALE:.1f}px;height:{h*MAP_SCALE:.1f}px">
  <defs><clipPath id="mc{k}"><path d="{g['d']}"/></clipPath></defs>
  <g clip-path="url(#mc{k})"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{COLORS[k % len(COLORS)]}"/>
  <image href="assets/photos/{big['file']}" x="{x0}" y="{y0}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/></g>
  <path d="{g['d']}" fill="none" stroke="#ffe3a3" stroke-width="2.4" stroke-dasharray="7 5" class="mst"/>
</svg>''')
    map_regs.append({'k': k, 'from': [round(rng.uniform(-1100, 1100)), round(rng.uniform(-700, 700)), round(rng.uniform(-50, 50), 1)]})
# outline sample points for sparkles travelling along the outline
import re
outline_pts = []
for sub in geo['outline'].split('Z'):
    pts = [tuple(map(float, p.split(','))) for p in re.findall(r'[-\d.]+,[-\d.]+', sub)]
    if len(pts) > len(outline_pts):
        outline_pts = pts
outline_pts = [(round(x * MAP_SCALE, 1), round(y * MAP_SCALE, 1)) for x, y in outline_pts[::3]]

# light trails converging on the map (screen space, map centred at 960,560)
trails = []
for i in range(9):
    a = -math.pi * 0.95 + i * (math.pi * 1.9 / 8) + rng.uniform(-.1, .1)
    sx, sy = 960 + math.cos(a) * 1500, 560 + math.sin(a) * 900
    ex, ey = 960 + math.cos(a) * 330, 560 + math.sin(a) * 300
    c1 = (960 + math.cos(a + .7) * 1100, 560 + math.sin(a + .7) * 700)
    trails.append(f'<path class="trail" id="tr{i}" d="M{sx:.0f},{sy:.0f} Q{c1[0]:.0f},{c1[1]:.0f} {ex:.0f},{ey:.0f}" pathLength="1" stroke-dasharray="0.22 1" stroke-dashoffset="0.22"/>')

# swirling golden threads for the 전 wide shot
swirl = []
for i in range(5):
    y0 = 300 + i * 120
    d = f'M-200,{y0} C300,{y0-260+i*40} 700,{y0+300} 1100,{y0+20} S1700,{y0-280} 2150,{y0-60}'
    swirl.append(f'<path class="swirl" id="sw{i}" d="{d}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>')

# gold dust (seeded)
dust = []
for i in range(70):
    x, y = rng.uniform(0, 1920), rng.uniform(0, 1080)
    s = rng.uniform(2, 6)
    dust.append(f'<i class="dp" id="dp{i}" style="left:{x:.0f}px;top:{y:.0f}px;width:{s:.1f}px;height:{s:.1f}px"></i>')
DUST = [{'i': i, 'dx': round(rng.uniform(-60, 60)), 'dy': round(rng.uniform(-160, -40)), 'p': round(rng.uniform(3, 7), 2), 'ph': round(rng.uniform(0, 3), 2)} for i in range(70)]

# ------------------------------------------------------------------ captions
caps = []
CAPL = json.load(open(ROOT / 'narr' / 'caplines6.json', encoding='utf-8'))
def hl(s):
    return re.sub(r'\[([^\]]+)\]', r'<em>\1</em>', s)
for x in [n for n in narr if n['id'] != 'L15']:
    lines = ''.join('<div class="cl">' + ' '.join(f'<span class="cu">{hl(u)}</span>' for u in line) + '</div>' for line in CAPL[x['id']])
    lt = ''  # v21: opening/ending are photo/cloth scenes again -> normal light captions
    x['lt'] = False
    caps.append(f'<div class="ncap{lt}" id="c-{x["id"]}">{lines}</div>')

# ------------------------------------------------------------------ font subset
chars = set(''.join(TXT.values()) + ''.join(IT.values()) + ''.join(NAMES) + ''.join(x['text'] for x in narr) + ''.join(p['cap'] for r in regions for p in r['photos']) + '0123456789·,.- ')
FONTS = VID / 'assets' / 'fonts'
(ROOT / 'fonts_dl' / 'chars.txt').write_text(''.join(sorted(chars)), encoding='utf-8')
(ROOT / 'fonts_dl' / 'chars_cap.txt').write_text(''.join(sorted(set(''.join(x['text'] for x in narr) + ''.join(TXT.values()) + ''.join(IT.values()) + ''.join(p['cap'] for r in regions for p in r['photos']) + '0123456789,.!?&·()/- '))), encoding='utf-8')
subprocess.run([sys.executable, '-I', '-m', 'fontTools.subset', str(ROOT / 'fonts_dl' / 'pre' / 'Pretendard-Bold.ttf'),
                f'--text-file={ROOT / "fonts_dl" / "chars_cap.txt"}', '--flavor=woff2', f'--output-file={FONTS / "pretendard-bold.woff2"}',
                '--layout-features=*'], check=True, capture_output=True)
subprocess.run([sys.executable, '-I', '-m', 'fontTools.subset', str(ROOT / 'fonts_dl' / 'pre' / 'Pretendard-SemiBold.ttf'),
                f'--text-file={ROOT / "fonts_dl" / "chars_cap.txt"}', '--flavor=woff2', f'--output-file={FONTS / "pretendard-semibold.woff2"}',
                '--layout-features=*'], check=True, capture_output=True)
for src, dst in [('HCRBatang.ttf', 'hcr-batang.woff2'), ('HCRBatang-Bold.ttf', 'hcr-batang-bold.woff2')]:
    subprocess.run([sys.executable, '-I', '-m', 'fontTools.subset', str(ROOT / 'fonts_dl' / src),
                    f'--text-file={ROOT / "fonts_dl" / "chars.txt"}', '--flavor=woff2', f'--output-file={FONTS / dst}',
                    '--layout-features=*'], check=True, capture_output=True)

def vid(id_, src, start, d, media_start=0, cls='vw'):
    return f'<div class="{cls}" id="{id_}-w"><video id="{id_}" class="clip" src="assets/video/{src}" muted playsinline data-start="{start}" data-duration="{d}" data-media-start="{media_start}" data-track-index="1"></video></div>'

def chap(id_, big, small):
    return f'<div class="chap" id="{id_}"><span class="cb">{big}</span><span class="cr"></span><span class="cs">{small}</span></div>'

def flare(id_, x, y):
    return f'<div class="flare" id="{id_}" style="left:{x}px;top:{y}px"><i class="fcore"></i><i class="fstreak"></i><i class="fhalo h1"></i><i class="fhalo h2"></i><i class="fhalo h3"></i></div>'

def leak(id_):
    return f'<div class="leak" id="{id_}"><i class="la"></i><i class="lr"></i><i class="lg"></i></div>'

def itag(id_, x, y, w, h, title, sub, cls=''):
    """linen name-tag patch (same look as the region tags) carrying the opening words"""
    sub_html = f'<span class="its">{sub}</span>' if sub else ''
    return f'''<div class="qt itag {cls}" id="{id_}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">
  <div class="qt-in itag-in"><span class="itt">{title}</span>{sub_html}</div>
  {stitch_svg(id_, w, h, inset=16, color='#b8862e', glow=False)}
</div>'''

def cframe(id_, x, y, w, h, photo, color):
    """small fabric-framed photo for the collage variant"""
    return f'<div class="cf" id="{id_}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--c:{color}"><img src="assets/photos/{photo}" alt=""><i></i></div>'

ALLPH = [(k, j, regions[k]['photos'][j]['file']) for j in range(3) for k in range(18)]
if JV in ('a', 'g'):
    # the camera glides over the very same quilt cloth the regions are later laid on (same image, light, tilt)
    P0, P1 = (3400, 1250), (6600, 1300)
    th_x0, th_y0 = 1800, 900
    TH = 'M0,700 C800,200 1300,900 1900,650 S3400,300 4300,700 S5300,1000 5900,420'
    intro_world = (f'''<svg class="ith" style="left:{th_x0}px;top:{th_y0}px" width="6000" height="1100" viewBox="0 0 6000 1100">
  <defs><mask id="ith-m" maskUnits="userSpaceOnUse" x="0" y="0" width="6000" height="1100"><path id="ith-mr" d="{TH}" fill="none" stroke="#fff" stroke-width="40" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/></mask></defs>
  <path class="ithp" d="{TH}" mask="url(#ith-m)"/></svg>'''
        + itag('it1', P0[0] - 520, P0[1] - 190, 1040, 330, IT['t1'], IT['s1'])
        + itag('it2', P1[0] - 520, P1[1] - 540, 1040, 300, IT['t2'], IT['s2'])
        + photo_patch('ip0', P1[0] - 960, P1[1] - 160, 600, 450, regions[8]['photos'][0]['file'], COLORS[1], regions[8]['photos'][0]['cap'])
        + photo_patch('ip1', P1[0] - 300, P1[1] - 160, 600, 450, regions[6]['photos'][2]['file'], COLORS[3], regions[6]['photos'][2]['cap'])
        + photo_patch('ip2', P1[0] + 360, P1[1] - 160, 600, 450, regions[4]['photos'][2]['file'], COLORS[5], regions[4]['photos'][2]['cap']))
    INTRO = f'''<div id="s1" class="layer clip va" data-start="0" data-duration="19.6" data-track-index="1">
  <div id="i-cam" class="layer"><div id="i-tilt"><div id="i-world">
    <img class="wfab" src="assets/img/quilt_base2.jpg" alt="" style="width:{WW}px;height:{WH}px">
    {intro_world}
  </div></div></div>
  <div class="dof top"></div><div class="dof bot"></div>
  <div id="i-far" class="layer"></div>
  <div id="i-lamp" class="lamp"></div>
  {itag('it3', 960 - 560, 330, 1120, 330, IT['t3a'] + ' ' + IT['t3b'], '', 'scr')}
</div>'''
    INTRO_DATA = {'P0': P0, 'P1': P1}
    ENDBG = '<div id="s6bg" class="layer"><img id="ebg" src="assets/img/end_quilt.jpg" alt=""></div>'
    if JV == 'g':
        # v21g: Grok clips (no people) carry the narration L01/L02, then the camera pulls back over the quilt (from 13.4 s);
        # the ending plays a clip of the finished jogakbo floating in the sky under the title
        # Grok Imagine stills only (2k, no people), moved with slow push-ins and light in the timeline
        gimg = lambda id_, f: f'<div class="vw gv" id="{id_}-w"><img id="{id_}" src="assets/img/{f}" alt=""></div>'
        INTRO = INTRO.replace('<div class="dof top"></div>', gimg('g1', 'v21_o1_dawn.jpg') + gimg('g2', 'v21_o2_drop.jpg') + gimg('g3', 'v21_o2b_stitch.jpg') + '<div class="dof top"></div>', 1)
        ENDBG = '<div id="s6bg" class="layer">' + gimg('g9', 'v21_e1_sky.jpg') + '</div>'
else:
    # a wall of real photos in fabric frames, stitched in one by one on the same quilt cloth
    cw, chh, g = 300, 214, 22
    cells = [(c, r) for r in range(4) for c in range(6)]
    order = sorted(range(24), key=lambda i: (abs(cells[i][0] - 2.5) + abs(cells[i][1] - 1.5) * 1.3, i))
    pick = [ALLPH[(i * 7) % len(ALLPH)][2] for i in range(24)]
    wall = ''.join(cframe(f'cf{i}', cells[i][0] * (cw + g), cells[i][1] * (chh + g), cw, chh, pick[i], COLORS[(i * 4 + 1) % len(COLORS)]) for i in range(24))
    INTRO = f'''<div id="s1" class="layer clip vb" data-start="0" data-duration="20.0" data-track-index="1">
  <img class="cbg" src="assets/img/quilt_base2.jpg" alt="">
  <div id="c-cam" class="layer"><div id="c-tilt"><div id="c-wall" style="width:{6 * cw + 5 * g}px;height:{4 * chh + 3 * g}px">{wall}</div></div></div>
  <div id="i-lamp" class="lamp"></div>
  {itag('it1', 960 - 520, 360, 1040, 330, IT['t1'], IT['s1'], 'scr')}
  {itag('it2', 960 - 520, 360, 1040, 330, IT['t2'], IT['s2'], 'scr')}
  {itag('it3', 960 - 560, 360, 1120, 330, IT['t3a'] + ' ' + IT['t3b'], '', 'scr')}
</div>'''
    INTRO_DATA = {'order': order}
    ew, eh, eg = 204, 168, 10
    ewall = ''.join(cframe(f'ef{i}', (i % 9) * (ew + eg), (i // 9) * (eh + eg), ew, eh, ALLPH[(i * 5) % 54][2], COLORS[(i * 4 + 2) % len(COLORS)]) for i in range(54))
    ENDBG = f'<div id="s6bg" class="layer"><img class="cbg" src="assets/img/quilt_base2.jpg" alt=""><div id="ewall" style="width:{9 * ew + 8 * eg}px;height:{6 * eh + 5 * eg}px">{ewall}</div></div>'

CSS = (ROOT / 'scripts' / 'style5.css').read_text(encoding='utf-8')
CSS = CSS.replace('__WW__', str(WW)).replace('__WH__', str(WH)).replace('__MAPW__', f'{MAP_W:.0f}').replace('__MAPH__', f'{MAP_H:.0f}')

html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="assets/gsap.min.js"></script>
<style>
{CSS}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
<audio id="mix" src="assets/audio/master_mix9_less.m4a" data-start="0" data-duration="{TOTAL}" data-track-index="0" data-volume="1"></audio>

<!-- 기 0-19: v21 opening built from the quilt (variant JV) -->
{INTRO}

<!-- 승 25-123 -->
<div id="s2" class="layer clip" data-start="19.0" data-duration="121.5" data-track-index="2">
  <div id="s2-cam" class="layer">
    <div id="s2-tilt">
      <div id="s2-world">
        <img class="wfab" src="assets/img/quilt_base2.jpg" alt="" style="width:{WW}px;height:{WH}px">
        {''.join(s2_html)}
      </div>
    </div>
  </div>
  <div class="dof top"></div><div class="dof bot"></div>
  <div id="s2-far" class="layer"></div>
  <div id="s2-blur" class="layer"></div>
  <div id="s2-sweep" class="sweep"></div>
  <div id="s2-lamp" class="lamp"></div>
</div>

<!-- 전 122.5-207 -->
{vid('v5', 'v13_c5_thread.mp4', 74.6, 9.6)}

<!-- 결: throw, three photos, title -->
{vid('v11', 'v13_c11_throw.mp4', T['throw'], 12.0)}
<div id="s7" class="layer clip" data-start="{T['ph'] - 0.6}" data-duration="{T['fin'] - T['ph'] + 1.6}" data-track-index="4">
  <div class="phs" id="ph0"><div class="phbg" style="background-image:url('assets/photos/end-uiryeong.jpg')"></div><div class="phfr"><img src="assets/photos/end-uiryeong.jpg" alt=""><i class="phst"></i></div></div>
  <div class="phs" id="ph1"><div class="phbg" style="background-image:url('assets/photos/end-changwon.jpg')"></div><div class="phfr"><img src="assets/photos/end-changwon.jpg" alt=""><i class="phst"></i></div></div>
  <div class="phs" id="ph2"><div class="phbg" style="background-image:url('assets/photos/end-miryang.jpg')"></div><div class="phfr"><img src="assets/photos/end-miryang.jpg" alt=""><i class="phst"></i></div></div>
</div>
<div id="s6" class="layer clip" data-start="{T['fin']}" data-duration="{T['end'] - T['fin']}" data-track-index="6">
  {ENDBG}
  <div id="s6g"></div>
  <div id="finline" class="fl"><i class="flt"></i></div>
  <div id="fin2" class="fin"><span class="f2"><span class="l1">주민의 힘으로,</span><span class="l2">경상남도가 <em>도약</em>하다</span></span><span class="f2s" aria-hidden="true"><span class="l1">주민의 힘으로,</span><span class="l2">경상남도가 도약하다</span></span></div>
  <div id="fin3" class="fin">{TXT['fin3']}</div>
  <img id="gnlogo" src="assets/img/gn_logo_color.svg" alt="경상남도">
  {flare('fl6', 975, 360)}
</div>

<!-- overlays -->
<div id="ov" class="layer clip" data-start="0" data-duration="{TOTAL}" data-track-index="7">
  <div id="dust">{''.join(dust)}</div>
  {leak('lk1')}{leak('lk2')}{leak('lk3')}{leak('lk4')}{leak('lk5')}{leak('lk6')}
  <div class="vig"></div>
  <div id="grain"><div class="gt"></div></div>
  <div id="capbg"></div>
  {''.join(caps)}
  <div id="fade" class="layer"></div>
</div>
</div>
<script>
const DATA = {json.dumps({'cells': s2_cells, 'M': M, 'CW': CW, 'CH': CH, 'WW': WW, 'WH': WH, 'narr': [{k: v for k, v in x.items() if k != 'tts'} for x in narr if x['id'] != 'L15'], 'T': T, 'map': map_regs, 'opts': outline_pts, 'dust': DUST, 'jv': JV, 'intro': INTRO_DATA, 'mapW': MAP_W, 'mapH': MAP_H}, ensure_ascii=False)};
</script>
<script>
{{MAINJS}}
</script>

</body>
</html>
'''
html = html.replace('{MAINJS}', (ROOT / 'scripts' / 'main5.js').read_text(encoding='utf-8'))
cloth_cfg = json.dumps({'t0': 83.0, 'b0': 86.6, 'step': 5.3, 'wide0': T['wide0'], 'wide1': 137.0, 'end': 140.5, 'cols': [{'name': NAMES[9 + k], 'num': 10 + k, 'photos': [p['file'] for p in regions[9 + k]['photos']], 'caps': [p['cap'] for p in regions[9 + k]['photos']], 'color': COLORS[(k * 3 + 4) % len(COLORS)]} for k in range(9)]}, ensure_ascii=False)
html = html.replace('{CLOTHJS}', (ROOT / 'scripts' / 'cloth3.js').read_text(encoding='utf-8').replace('__CFG__', cloth_cfg))
(VID / 'index.html').write_text(html, encoding='utf-8')
print('ok', len(html), 'world', WW, WH)
