// 생활공감정책 film, titles C안 "불이 켜지는 마을" (draft).
//   node scripts/policy_titles_lights.js  -> parts/policy/title_open_c.mp4 (6 s), parts/policy/title_end_c.mp4 (7 s)
// Opening: the film's first street, graded to blue dawn; small warm lights come on in the street, the title's letters
// light up one by one like windows, and the morning arrives (grade warms to daylight) as the film begins.
// Closing: the last alley of the film turns to dusk; windows and lamps light up, the closing words light up letter by
// letter, then the 경상남도 logo. Fonts: Gowun Batang (OFL).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..'); const P = path.join(ROOT, 'parts', 'policy');
const F = (f) => 'file://' + path.join(ROOT, f); const FPS = 30;
const LIGHTS = {   // (x, y, size) warm lights placed on the frames' own windows, shop fronts and lamps
  open: [[300, 330, 70], [520, 410, 55], [1460, 300, 80], [1660, 380, 60], [880, 250, 50], [1180, 420, 45], [140, 520, 60], [1790, 560, 55]],
  end: [[230, 300, 70], [520, 360, 55], [760, 260, 60], [1330, 330, 75], [1560, 280, 55], [1750, 420, 60], [980, 420, 45], [400, 500, 50]],
};
const page = (kind) => `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Bold.ttf')}"); font-weight: 700; }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Regular.ttf')}"); font-weight: 400; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #000; }
#bg { position: absolute; inset: -40px; background: url("${F('parts/policy/' + (kind === 'open' ? 'title_bg_open.png' : 'title_bg_end.png'))}") center/cover; }
#tint { position: absolute; inset: 0; }
.lt { position: absolute; border-radius: 50%; background: radial-gradient(circle, rgba(255,214,150,.95), rgba(255,170,80,.35) 35%, rgba(255,150,60,0) 70%); mix-blend-mode: screen; opacity: 0; }
#txt { position: absolute; left: 0; right: 0; top: 380px; text-align: center; font-family: "Gowun"; }
.sub { font-weight: 400; font-size: 46px; letter-spacing: .14em; color: #f3dfb0; opacity: 0; text-shadow: 0 0 18px rgba(255,190,110,.6), 0 2px 8px rgba(0,0,0,.6); }
.main { margin-top: 22px; font-weight: 700; font-size: 132px; white-space: nowrap; }
.main span { display: inline-block; color: rgba(60,50,40,.0); }
#logo { position: absolute; left: 50%; top: 880px; width: 300px; height: 105px; margin-left: -150px; background: rgba(255,255,255,.93); border-radius: 14px; padding: 10px 22px; box-shadow: 0 0 30px rgba(255,200,130,.35); opacity: 0; }
#logo img { width: 100%; height: 100%; object-fit: contain; }
#fade { position: absolute; inset: 0; background: #000; }
</style>
<div id="bg"></div><div id="tint"></div>
${LIGHTS[kind].map(([x, y, s], i) => `<div class="lt" id="l${i}" style="left:${x - s}px;top:${y - s}px;width:${2 * s}px;height:${2 * s}px"></div>`).join('')}
<div id="txt"><div class="sub" id="sub">${kind === 'open' ? '우리 곁의 평범한 이웃' : '경남의 일상을 함께 바꿔 갑니다'}</div>
<div class="main" id="main">${[...'생활공감정책 참여단'].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div></div>
${kind === 'end' ? `<div id="logo"><img src="${F('video/assets/img/gn_logo_color.svg')}"></div>` : ''}
<div id="fade"></div>
<script>
const KIND = ${JSON.stringify(kind)}, NL = ${LIGHTS[kind].length}, DUR = KIND === 'open' ? 6 : 7;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)); const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
const $ = (id) => document.getElementById(id);
const flick = (t, i) => 0.85 + 0.15 * Math.sin(t * 23 + i * 7.1) * Math.sin(t * 9 + i * 2.3);
window.draw = (t) => {
  // grade: open = blue dawn -> warm daylight at the end; end = daylight -> deep blue dusk
  const d = KIND === 'open' ? 1 - smooth((t - 3.6) / 2.2) : smooth((t - 0.3) / 2.2);
  $('bg').style.filter = 'brightness(' + (1 - 0.72 * d) + ') saturate(' + (1 - 0.45 * d) + ') hue-rotate(' + (-12 * d) + 'deg) blur(' + (2 * d) + 'px)';
  $('bg').style.transform = 'scale(' + (1.04 + 0.04 * t / DUR) + ')';
  $('tint').style.background = 'linear-gradient(180deg, rgba(20,35,80,' + (0.55 * d) + '), rgba(10,15,40,' + (0.35 * d) + '))';
  for (let i = 0; i < NL; i++) {                                                   // street lights come on one by one
    const t0 = (KIND === 'open' ? 0.4 : 1.4) + i * 0.22;
    const on = clamp((t - t0) / 0.15), stay = KIND === 'open' ? 1 - smooth((t - 4.4) / 1.2) : 1;
    $('l' + i).style.opacity = (on * stay * flick(t, i) * (0.5 + 0.5 * d)).toFixed(3);
  }
  const T0 = KIND === 'open' ? 1.2 : 2.6;                                          // letters light up like windows
  [...document.querySelectorAll('#main span')].forEach((s, i) => {
    const v = clamp((t - T0 - i * 0.16) / 0.12); const glow = v * (0.85 + 0.15 * Math.sin(t * 17 + i));
    s.style.color = 'rgba(255,' + Math.round(236 + 12 * v) + ',' + Math.round(200 + 30 * v) + ',' + ((KIND === 'open' ? 0.12 : 0) * smooth(t / 1.5) + (1 - (KIND === 'open' ? 0.12 : 0)) * v) + ')';
    s.style.textShadow = '0 0 ' + (18 * glow) + 'px rgba(255,190,100,' + (0.85 * glow) + '), 0 0 ' + (60 * glow) + 'px rgba(255,160,70,' + (0.45 * glow) + '), 0 3px 8px rgba(0,0,0,.6)';
  });
  $('sub').style.opacity = smooth((t - T0 - 1.9) / 0.8);
  if ($('logo')) $('logo').style.opacity = smooth((t - 5.0) / 0.8);
  $('fade').style.opacity = KIND === 'open' ? 1 - smooth(t / 0.6) : Math.max(1 - smooth(t / 0.6), smooth((t - 6.3) / 0.7));
};
</script>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [kind, dur] of [['open', 6.0], ['end', 7.0]]) {
    const dir = path.join(P, `_c_${kind}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const tmp = path.join(P, `_c_${kind}.html`); fs.writeFileSync(tmp, page(kind));
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    const n = Math.round(dur * FPS);
    for (let k = 0; k < n; k++) { await p.evaluate((t) => window.draw(t), k / FPS); await p.screenshot({ path: path.join(dir, `f${String(k).padStart(4, '0')}.png`) }); }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'), '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', path.join(P, `title_${kind}_c.mp4`)]);
    fs.rmSync(dir, { recursive: true, force: true }); fs.unlinkSync(tmp); console.log('ok', `title_${kind}_c.mp4`);
  }
  await b.close();
})();
