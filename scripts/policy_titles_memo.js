// 생활공감정책 film, titles "A안": a proposal note → a "reflected" stamp.
//   node scripts/policy_titles_memo.js   -> parts/policy/title_open.mp4 (6 s), parts/policy/title_end.mp4 (7 s)
// Opening: handwritten notes (the inconveniences the film shows) are written one by one on paper slips, then the
// title rises over them. Closing: the same notes come back and each gets a red stamp (반영 / 채택 / 추진 중 / 개선),
// then the closing words and the 경상남도 logo. Fonts (all OFL): Nanum Pen Script, Gowun Batang.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..'); const P = path.join(ROOT, 'parts', 'policy');
const F = (f) => 'file://' + path.join(ROOT, f); const FPS = 30;
const NOTES = [   // text, x, y, rotation, paper colour, stamp
  ['길에 턱이 너무 높아요', 160, 150, -5, '#fbf3d5', '개선'],
  ['산책로가 중간에 끊겨 있어요', 1040, 130, 4, '#f3efe6', '반영'],
  ['다 같이 사진 찍을 곳이 없어요', 120, 620, 3, '#eef4ea', '채택'],
  ['점심시간엔 우편을 못 보내요', 1020, 640, -4, '#f6ece8', '추진 중'],
];
const page = (kind) => `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: "Pen"; src: url("${F('fonts_dl/pen/NanumPenScript.ttf')}"); }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Bold.ttf')}"); font-weight: 700; }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Regular.ttf')}"); font-weight: 400; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; }
#bg { position: absolute; inset: 0; background: radial-gradient(ellipse 80% 70% at 50% 45%, #3a2a1c, #1a120b 70%, #0e0906); }
#grain { position: absolute; inset: 0; opacity: .35; background: url("${F('video/assets/img/linen.jpg')}") center/cover; mix-blend-mode: overlay; }
.note { position: absolute; width: 760px; height: 300px; padding: 60px 46px 0; border-radius: 4px;
  box-shadow: 0 18px 40px rgba(0,0,0,.45), 0 2px 6px rgba(0,0,0,.3); opacity: 0; }
.note::before { content: ""; position: absolute; left: 50%; top: -14px; width: 150px; height: 34px; margin-left: -75px;
  background: rgba(235,222,190,.75); transform: rotate(-2deg); box-shadow: 0 2px 4px rgba(0,0,0,.15); }
.note .lines { position: absolute; left: 36px; right: 36px; top: 150px; height: 2px; background: rgba(120,100,70,.18); }
.note .t { font-family: "Pen"; font-size: 80px; color: #2a2a3a; white-space: nowrap; display: inline-block; }
.stamp { position: absolute; right: 34px; bottom: 16px; width: 150px; height: 150px; border-radius: 50%; border: 9px solid #c8322f;
  color: #c8322f; font-family: "Gowun"; font-weight: 700; font-size: 46px; display: flex; white-space: nowrap; align-items: center; justify-content: center;
  opacity: 0; background: rgba(250,240,230,.08); letter-spacing: -.02em; }
.stamp::after { content: ""; position: absolute; inset: 9px; border-radius: 50%; border: 3px solid #c8322f; }
#dim { position: absolute; inset: 0; background: rgba(10,6,3,0); }
#txt { position: absolute; left: 0; right: 0; top: 380px; text-align: center; font-family: "Gowun"; }
.sub { font-weight: 400; font-size: 46px; letter-spacing: .14em; color: #e7cf98; text-shadow: 0 2px 10px rgba(0,0,0,.7); opacity: 0; }
.main { margin-top: 22px; font-weight: 700; font-size: 128px; color: #fbf3e4; white-space: nowrap; text-shadow: 0 3px 10px rgba(0,0,0,.7), 0 0 40px rgba(0,0,0,.5); }
.main span { display: inline-block; opacity: 0; }
.thread { width: 720px; height: 3px; margin: 38px auto 0; transform: scaleX(0); background: linear-gradient(90deg, rgba(231,207,152,0), #e7cf98 18%, #f3e2b6 50%, #e7cf98 82%, rgba(231,207,152,0)); box-shadow: 0 0 10px rgba(243,226,182,.7); }
#logo { position: absolute; left: 50%; top: 880px; width: 300px; height: 105px; margin-left: -150px; background: rgba(255,255,255,.93); border-radius: 14px; padding: 10px 22px; box-shadow: 0 6px 18px rgba(0,0,0,.35); opacity: 0; }
#logo img { width: 100%; height: 100%; object-fit: contain; }
#fade { position: absolute; inset: 0; background: #000; }
</style>
<div id="bg"></div><div id="grain"></div>
${NOTES.map(([t, x, y, r, c, s], i) => `<div class="note" id="n${i}" style="left:${x}px;top:${y}px;background:${c};--r:${r}deg">
  <div class="lines"></div><span class="t" id="t${i}">${t}</span>${kind === 'end' ? `<div class="stamp" id="s${i}" style="${s.length > 2 ? 'font-size:34px' : ''}">${s}</div>` : ''}</div>`).join('')}
<div id="dim"></div>
<div id="txt"><div class="sub" id="sub">${kind === 'open' ? '우리 곁의 평범한 이웃' : '경남의 일상을 함께 바꿔 갑니다'}</div>
<div class="main" id="main">${[...'생활공감정책 참여단'].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div><div class="thread" id="thread"></div></div>
${kind === 'end' ? `<div id="logo"><img src="${F('video/assets/img/gn_logo_color.svg')}"></div>` : ''}
<div id="fade"></div>
<script>
const KIND = ${JSON.stringify(kind)}, N = ${NOTES.length};
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const ease = (t) => 1 - Math.pow(1 - clamp(t), 3); const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
const back = (t) => { t = clamp(t); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const $ = (id) => document.getElementById(id);
window.draw = (t) => {
  let shake = 0;
  for (let i = 0; i < N; i++) {
    const n = $('n' + i), r = getComputedStyle(n).getPropertyValue('--r');
    const t0 = KIND === 'open' ? 0.3 + i * 0.55 : 0.15 + i * 0.18;            // note drops in
    const a = ease((t - t0) / 0.45);
    n.style.opacity = a; n.style.transform = 'translateY(' + (-40 * (1 - a)) + 'px) rotate(' + r + ') scale(' + (1.06 - .06 * a) + ')';
    const w0 = t0 + 0.25, wd = KIND === 'open' ? 1.0 : 0.6;                    // handwriting: revealed left to right
    $('t' + i).style.clipPath = 'inset(-20px ' + (100 - 100 * clamp((t - w0) / wd)) + '% -20px -10px)';
    if (KIND === 'end') {                                                      // stamp slams down
      const s0 = 1.6 + i * 0.42, sp = (t - s0) / 0.16, s = $('s' + i);
      if (sp > 0) { s.style.opacity = clamp(sp * 1.4) * .92; s.style.transform = 'rotate(' + (-12 + i * 7) + 'deg) scale(' + (1 + 0.9 * (1 - back(sp))) + ')';
        if (sp > 1 && sp < 1.9) shake = Math.max(shake, (1.9 - sp) * 5); }
    }
  }
  document.body.style.transform = shake ? 'translate(' + (Math.sin(t * 90) * shake) + 'px,' + (Math.cos(t * 77) * shake) + 'px)' : '';
  const T0 = KIND === 'open' ? 3.0 : 4.2;                                        // dim + title
  $('dim').style.background = 'rgba(10,6,3,' + (0.7 * smooth((t - T0 + .3) / .9)) + ')';
  $('sub').style.opacity = smooth((t - T0) / .8);
  $('thread').style.transform = 'scaleX(' + smooth((t - T0 - .2) / 1.2) + ')';
  [...document.querySelectorAll('#main span')].forEach((s, i) => { const v = ease((t - T0 - .45 - i * .06) / .8);
    s.style.opacity = v; s.style.transform = 'translateY(' + (26 * (1 - v)) + 'px)'; s.style.filter = 'blur(' + (6 * (1 - v)) + 'px)'; });
  if ($('logo')) $('logo').style.opacity = smooth((t - 5.2) / .8);
  $('fade').style.opacity = 1 - smooth(t / .5);
};
</script>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [kind, dur] of [['open', 6.0], ['end', 7.0]]) {
    const dir = path.join(P, `_n_${kind}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const tmp = path.join(P, `_n_${kind}.html`); fs.writeFileSync(tmp, page(kind));
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    const n = Math.round(dur * FPS);
    for (let k = 0; k < n; k++) { await p.evaluate((t) => window.draw(t), k / FPS); await p.screenshot({ path: path.join(dir, `f${String(k).padStart(4, '0')}.png`) }); }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'), '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', path.join(P, `title_${kind}.mp4`)]);
    fs.rmSync(dir, { recursive: true, force: true }); fs.unlinkSync(tmp); console.log('ok', `title_${kind}.mp4`);
  }
  await b.close();
})();
