// 생활공감정책 intro preview: caption PNGs (transparent) + background PNG in the expo film's caption style.
//   node scripts/policy_caps.js   -> parts/policy/cap_P01.png ... , parts/policy/bg.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'parts', 'policy'); fs.mkdirSync(OUT, { recursive: true });
const CAPS = {
  P01: ['오늘도 저마다의 자리에서 하루를 시작하는 사람들.'],
  P02: ['누군가에게는 익숙한 길이,', '다른 누군가에게는 <em>넘어야 할 턱</em>이 되기도 합니다.'],
  P03: ['“조금 더 편하게 바꿀 수는 없을까?”'],
  P04: ['이웃의 불편을 지나치지 않은 마음이', '수첩 속 <em>한 줄의 제안</em>으로 이어집니다.'],
  P05: ['생활 속 작은 생각을 모아,', '우리의 일상을 바꾸어 가는 사람들.'],
  P06: ['<em>생활공감정책 참여단</em>의 이야기는', '바로 여기서 시작됩니다.'],
};
const CSS = `
@font-face { font-family: "Pretendard"; src: url("assets/fonts/pretendard-semibold.woff2") format("woff2"); font-weight: 600; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: transparent; }
:root { --cw: #f6efe2; --cg: #dcc48e; }
.ncap { position: absolute; left: 154px; right: 154px; bottom: 96px; text-align: center; }
.ncap .cl { display: block; margin-top: 10px; }
.ncap .cu { display: inline-block; font-family: "Pretendard", sans-serif; font-size: 46px; font-weight: 600; line-height: 1.5; color: var(--cw);
  letter-spacing: -.005em; word-break: keep-all; text-shadow: 0 1px 3px rgba(0, 0, 0, .55), 0 0 12px rgba(0, 0, 0, .3); }
.ncap em { font-style: normal; color: var(--cg); }
#bg { position: absolute; inset: 0; background:
  radial-gradient(ellipse 70% 60% at 62% 38%, rgba(222, 170, 104, .30), transparent 70%),
  radial-gradient(ellipse 50% 45% at 22% 70%, rgba(150, 110, 160, .16), transparent 70%),
  linear-gradient(180deg, #2a1d14 0%, #17100b 70%, #0f0a06 100%); }
#bg::after { content: ""; position: absolute; inset: 0; background: radial-gradient(ellipse at center, transparent 55%, rgba(0, 0, 0, .45)); }`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const tmp = path.join(ROOT, 'video', '_policy_cap.html');
  for (const [id, ls] of Object.entries(CAPS)) {
    const html = `<!doctype html><meta charset="utf-8"><style>${CSS}</style><div class="ncap">${ls.map(l => `<span class="cl"><span class="cu">${l}</span></span>`).join('')}</div>`;
    fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(OUT, `cap_${id}.png`), omitBackground: true });
  }
  fs.writeFileSync(tmp, `<!doctype html><meta charset="utf-8"><style>${CSS}</style><div id="bg"></div>`);
  await p.goto('file://' + tmp); await p.screenshot({ path: path.join(OUT, 'bg.png') });
  fs.unlinkSync(tmp); await b.close(); console.log('ok');
})();
