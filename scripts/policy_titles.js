// 생활공감정책 film: animated opening and closing titles (HTML/CSS animation, rendered frame by frame with Playwright).
// Open-source fonts: Gowun Batang (OFL, Google Fonts) for the titles, Pretendard (OFL) for small text.
//   node scripts/policy_titles.js        -> parts/policy/title_open.mp4, parts/policy/title_end.mp4 (5 s, 1920x1080, 30 fps)
// Look: the film's own frame, softly blurred and warm-graded, slowly pushing in; a warm light drifts across; a fine gold
// thread draws out, then the words rise in letter by letter.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const P = path.join(ROOT, 'parts', 'policy');
const F = (f) => 'file://' + path.join(ROOT, f);
const DUR = 5.0, FPS = 30;
const TITLES = {
  open: { bg: 'title_bg_open.png', sub: '우리 곁의 평범한 이웃', main: '생활공감정책 참여단', foot: '', logo: false },
  end: { bg: 'title_bg_end.png', sub: '경남의 일상을 함께 바꿔 갑니다', main: '생활공감정책 참여단', foot: '', logo: true },
};
const css = (t) => `
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Bold.ttf')}"); font-weight: 700; }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Regular.ttf')}"); font-weight: 400; }
@font-face { font-family: "Pretendard"; src: url("${F('video/assets/fonts/pretendard-semibold.woff2')}"); font-weight: 600; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #120c08; }
#bg { position: absolute; inset: -60px; background: url("file://${path.join(P, t.bg)}") center / cover;
  filter: blur(14px) brightness(.5) saturate(.85) sepia(.18); animation: push ${DUR}s linear both; }
@keyframes push { from { transform: scale(1.04); } to { transform: scale(1.12); } }
#tone { position: absolute; inset: 0; background: radial-gradient(ellipse 75% 65% at 50% 46%, rgba(40, 24, 10, .05), rgba(12, 7, 3, .62) 100%); }
#light { position: absolute; width: 1400px; height: 1400px; left: -700px; top: -520px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 196, 120, .30), rgba(255, 170, 90, .10) 40%, transparent 68%);
  mix-blend-mode: screen; animation: drift ${DUR}s ease-in-out both; }
@keyframes drift { from { transform: translate(0, 0); opacity: 0; } 30% { opacity: 1; } to { transform: translate(1150px, 160px); opacity: .85; } }
#wrap { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-58%); text-align: center; }
#sub { font-family: "Gowun"; font-weight: 400; font-size: 46px; letter-spacing: .14em; color: #e7cf98; opacity: 0;
  text-shadow: 0 2px 10px rgba(0, 0, 0, .55); animation: fadeup 1.1s ease-out 1.0s both; }
#main { margin-top: 26px; font-family: "Gowun"; font-weight: 700; font-size: 132px; letter-spacing: .02em; color: #fbf3e4;
  text-shadow: 0 3px 8px rgba(0, 0, 0, .55), 0 0 40px rgba(0, 0, 0, .35); white-space: nowrap; }
#main span { display: inline-block; opacity: 0; animation: rise .9s cubic-bezier(.2, .7, .2, 1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(26px); filter: blur(6px); } to { opacity: 1; transform: none; filter: blur(0); } }
@keyframes fadeup { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
#thread { position: relative; width: 760px; height: 3px; margin: 40px auto 0; }
#thread i { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(231, 207, 152, 0), #e7cf98 18%, #f3e2b6 50%, #e7cf98 82%, rgba(231, 207, 152, 0));
  transform-origin: 50% 50%; animation: draw 1.6s cubic-bezier(.4, 0, .2, 1) .3s both; box-shadow: 0 0 10px rgba(243, 226, 182, .7); }
@keyframes draw { from { transform: scaleX(0); } to { transform: scaleX(1); } }
#logo { position: absolute; left: 50%; top: 860px; width: 300px; height: 105px; margin-left: -150px; background: rgba(255, 255, 255, .92);
  border-radius: 14px; padding: 10px 22px; box-shadow: 0 6px 18px rgba(0, 0, 0, .3); opacity: 0; animation: fadeup 1s ease-out 2.6s both; }
#logo img { width: 100%; height: 100%; object-fit: contain; }
#vig { position: absolute; inset: 0; background: #000; animation: vin .9s ease-out both; }
@keyframes vin { from { opacity: 1; } to { opacity: 0; } }
`;
const html = (t) => {
  const letters = [...t.main].map((c, i) => c === ' ' ? '<span>&nbsp;</span>' : `<span style="animation-delay:${(1.5 + i * 0.07).toFixed(2)}s">${c}</span>`).join('');
  return `<!doctype html><meta charset="utf-8"><style>${css(t)}</style><div id="bg"></div><div id="tone"></div><div id="light"></div>
<div id="wrap"><div id="sub">${t.sub}</div><div id="main">${letters}</div><div id="thread"><i></i></div></div>
${t.logo ? `<div id="logo"><img src="${F('video/assets/img/gn_logo_color.svg')}"></div>` : ''}<div id="vig"></div>`;
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [name, t] of Object.entries(TITLES)) {
    const dir = path.join(P, `_t_${name}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const tmp = path.join(P, `_t_${name}.html`); fs.writeFileSync(tmp, html(t));
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    await p.evaluate(() => document.getAnimations().forEach(a => a.pause()));
    const n = Math.round(DUR * FPS);
    for (let k = 0; k < n; k++) {
      await p.evaluate((ms) => document.getAnimations().forEach(a => { a.currentTime = ms; }), (k / FPS) * 1000);
      await p.screenshot({ path: path.join(dir, `f${String(k).padStart(4, '0')}.png`) });
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'), '-c:v', 'libx264', '-crf', '14',
      '-pix_fmt', 'yuv420p', path.join(P, `title_${name}.mp4`)]);
    fs.rmSync(dir, { recursive: true, force: true }); fs.unlinkSync(tmp); console.log('ok', `title_${name}.mp4`);
  }
  await b.close();
})();
