// 생활공감정책 film: opening and closing titles as a photo mosaic (only real frames from the film).
//   node scripts/policy_titles_mosaic.js   -> parts/policy/title_open.mp4 (6 s), parts/policy/title_end.mp4 (7 s)
// Opening: small photo tiles (parts/policy/tiles) drift in from all sides and settle into the shape of 경상남도
// (geo/gyeongnam.json), the outline is drawn in gold, then the title rises beside the map.
// Closing: tiles fly in and land on a grid; each tile turns into its piece of the last group photo, the gaps close
// into the whole photo, it dims, and the closing words and the 경상남도 logo appear.
// Rendered frame by frame in Chromium (canvas + CSS), fonts: Gowun Batang / Pretendard (both OFL).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..'); const P = path.join(ROOT, 'parts', 'policy');
const F = (f) => 'file://' + path.join(ROOT, f);
const FPS = 30;
const tiles = fs.readdirSync(path.join(P, 'tiles')).filter(f => f.endsWith('.jpg')).sort().map(f => F(`parts/policy/tiles/${f}`));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo', 'gyeongnam.json'), 'utf8'));
const page = (kind) => `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Bold.ttf')}"); font-weight: 700; }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Regular.ttf')}"); font-weight: 400; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #120c08; }
canvas { position: absolute; inset: 0; }
#txt { position: absolute; text-align: center; font-family: "Gowun"; }
.sub { font-weight: 400; font-size: 44px; letter-spacing: .14em; color: #e7cf98; text-shadow: 0 2px 10px rgba(0,0,0,.6); }
.main { margin-top: 22px; font-weight: 700; font-size: 104px; color: #fbf3e4; white-space: nowrap; text-shadow: 0 3px 8px rgba(0,0,0,.55), 0 0 40px rgba(0,0,0,.35); }
.main span { display: inline-block; }
.thread { width: 640px; height: 3px; margin: 36px auto 0; background: linear-gradient(90deg, rgba(231,207,152,0), #e7cf98 18%, #f3e2b6 50%, #e7cf98 82%, rgba(231,207,152,0)); box-shadow: 0 0 10px rgba(243,226,182,.7); transform-origin: 50% 50%; }
#logo { position: absolute; left: 50%; top: 880px; width: 300px; height: 105px; margin-left: -150px; background: rgba(255,255,255,.93); border-radius: 14px; padding: 10px 22px; box-shadow: 0 6px 18px rgba(0,0,0,.35); opacity: 0; }
#logo img { width: 100%; height: 100%; object-fit: contain; }
</style>
<canvas id="c" width="1920" height="1080"></canvas>
<div id="txt" style="${kind === 'open' ? 'left:920px;width:1000px;top:400px' : 'left:0;right:0;top:330px'}">
  <div class="sub" id="sub">${kind === 'open' ? '우리 곁의 평범한 이웃' : '경남의 일상을 함께 바꿔 갑니다'}</div>
  <div class="main" id="main">${[...'생활공감정책 참여단'].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div>
  <div class="thread" id="thread"></div>
</div>
${kind === 'end' ? `<div id="logo"><img src="${F('video/assets/img/gn_logo_color.svg')}"></div>` : ''}
<script>
const KIND = ${JSON.stringify(kind)}, TILES = ${JSON.stringify(tiles)}, GEO = ${JSON.stringify(geo)};
const GROUP = ${JSON.stringify(F('parts/policy/end_group.jpg'))};
const c = document.getElementById('c'), x = c.getContext('2d');
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = (t) => 1 - Math.pow(1 - clamp(t), 3);
const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
let rnd = 7; const R = () => (rnd = (rnd * 16807) % 2147483647) / 2147483647;
const load = (s) => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = s; });
let imgs = [], group = null, cells = [], outline;
// opening: map placement
const MS = 800 / GEO.h, MX = 150, MY = 140;
window.ready = (async () => {
  imgs = await Promise.all(TILES.map(load)); group = await load(GROUP);
  if (KIND === 'open') {
    outline = new Path2D(GEO.outline); const S = 40, G = 3;          // tile size and gap (screen px)
    for (let yy = 0; yy < GEO.h * MS; yy += S) for (let xx = 0; xx < GEO.w * MS; xx += S) {
      const gx = (xx + S / 2) / MS, gy = (yy + S / 2) / MS;
      if (x.isPointInPath(outline, gx, gy)) cells.push({ tx: MX + xx, ty: MY + yy, s: S - G });
    }
  } else {
    const S = 120; for (let yy = 0; yy < 1080; yy += S) for (let xx = 0; xx < 1920; xx += S) cells.push({ tx: xx, ty: yy, s: S });
  }
  cells.forEach((q, i) => {
    const a = R() * Math.PI * 2, d = 900 + R() * 700;
    q.fx = q.tx + Math.cos(a) * d; q.fy = q.ty + Math.sin(a) * d; q.fr = (R() - .5) * 1.4; q.fs = .4 + R() * .9;
    q.img = imgs[Math.floor(R() * imgs.length)]; q.sx = R(); q.sy = R();
    const dist = Math.hypot(q.tx + q.s / 2 - 960, q.ty + q.s / 2 - 540);
    q.delay = (KIND === 'open' ? 0.15 + dist / 1500 * 1.4 : 0.1 + R() * 1.2) + R() * .35;
  });
})();
function crop(img, sx, sy, k) {           // a square piece of a tile photo
  const side = Math.min(img.width, img.height) * k;
  return [ (img.width - side) * sx, (img.height - side) * sy, side, side ];
}
const groupCrop = () => { const s = Math.max(1920 / group.width, 1080 / group.height); return [s, (1920 - group.width * s) / 2, (1080 - group.height * s) / 2]; };
window.draw = (t) => {
  x.fillStyle = '#120c08'; x.fillRect(0, 0, 1920, 1080);
  const g = x.createRadialGradient(960, 520, 100, 960, 540, 1200); g.addColorStop(0, 'rgba(70,45,22,.55)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(0, 0, 1920, 1080);
  const DUR = KIND === 'open' ? 2.0 : 1.6;
  for (const q of cells) {
    const p = ease((t - q.delay) / DUR); if (p <= 0) continue;
    const px = q.fx + (q.tx - q.fx) * p, py = q.fy + (q.ty - q.fy) * p, r = q.fr * (1 - p), sc = q.fs + (1 - q.fs) * p;
    let size = q.s;
    if (KIND === 'end') size = q.s - 6 + 6 * smooth((t - 3.0) / .7);          // gaps close into the whole photo
    x.save(); x.globalAlpha = clamp(p * 2.2); x.translate(px + q.s / 2, py + q.s / 2); x.rotate(r); x.scale(sc, sc);
    x.drawImage(q.img, ...crop(q.img, q.sx, q.sy, .55), -size / 2, -size / 2, size, size);
    if (KIND === 'end') {                 // each tile turns into its own piece of the group photo
      const m = smooth((t - q.delay - DUR * .85) / .6);
      if (m > 0) { const [s, ox, oy] = groupCrop(); x.globalAlpha = m;
        x.drawImage(group, (q.tx - ox) / s, (q.ty - oy) / s, q.s / s, q.s / s, -size / 2, -size / 2, size, size); }
    }
    x.restore();
  }
  if (KIND === 'open') {                  // gold outline of 경상남도 drawn after the tiles settle
    const o = smooth((t - 2.6) / 1.2);
    if (o > 0) { x.save(); x.translate(MX, MY); x.scale(MS, MS); x.lineWidth = 3 / MS; x.strokeStyle = 'rgba(231,207,152,' + (.9 * o) + ')';
      x.shadowColor = 'rgba(243,226,182,.8)'; x.shadowBlur = 12; x.setLineDash([2400 * o, 4000]); x.stroke(new Path2D(GEO.outline)); x.restore(); }
  } else {                                // whole photo dims under the closing words
    const dm = smooth((t - 3.6) / .8); x.fillStyle = 'rgba(10,6,3,' + (.58 * dm) + ')'; x.fillRect(0, 0, 1920, 1080);
  }
  const T0 = KIND === 'open' ? 2.9 : 4.0;   // words
  document.getElementById('sub').style.opacity = smooth((t - T0) / .8);
  document.getElementById('thread').style.transform = 'scaleX(' + smooth((t - T0 - .2) / 1.2) + ')';
  [...document.querySelectorAll('#main span')].forEach((s, i) => { const v = ease((t - T0 - .5 - i * .06) / .8);
    s.style.opacity = v; s.style.transform = 'translateY(' + (26 * (1 - v)) + 'px)'; s.style.filter = 'blur(' + (6 * (1 - v)) + 'px)'; });
  const lg = document.getElementById('logo'); if (lg) lg.style.opacity = smooth((t - 5.0) / .8);
  const fi = 1 - smooth(t / .5); if (fi > 0) { x.fillStyle = 'rgba(0,0,0,' + fi + ')'; x.fillRect(0, 0, 1920, 1080); }
};
</script>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [kind, dur] of [['open', 6.0], ['end', 7.0]]) {
    const dir = path.join(P, `_m_${kind}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const tmp = path.join(P, `_m_${kind}.html`); fs.writeFileSync(tmp, page(kind));
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready); await p.evaluate(() => window.ready);
    const n = Math.round(dur * FPS);
    for (let k = 0; k < n; k++) {
      await p.evaluate((t) => window.draw(t), k / FPS);
      await p.screenshot({ path: path.join(dir, `f${String(k).padStart(4, '0')}.png`) });
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'), '-c:v', 'libx264', '-crf', '14',
      '-pix_fmt', 'yuv420p', path.join(P, `title_${kind}.mp4`)]);
    fs.rmSync(dir, { recursive: true, force: true }); fs.unlinkSync(tmp); console.log('ok', `title_${kind}.mp4`);
  }
  await b.close();
})();
