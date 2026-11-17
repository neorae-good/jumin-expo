// 생활공감정책 film end card: the last frame of scene 3, blurred and darkened, with the group name and the 경상남도 logo.
//   ffmpeg ... -> parts/policy/end_frame.png (see make_policy_full.py), then: node scripts/policy_endcard.js
//   -> parts/policy/endcard.png
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const P = path.join(ROOT, 'parts', 'policy');
const html = `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: "Pretendard"; src: url("file://${ROOT}/video/assets/fonts/pretendard-semibold.woff2"); font-weight: 600; }
@font-face { font-family: "Pretendard"; src: url("file://${ROOT}/video/assets/fonts/pretendard-bold.woff2"); font-weight: 700; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: #0f0a06; }
#bg { position: absolute; inset: -40px; background: url("file://${P}/end_frame.png") center / cover; filter: blur(22px) brightness(.42) saturate(.9); }
#v { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 40%, rgba(0,0,0,.45)); }
#t { position: absolute; left: 0; right: 0; top: 390px; text-align: center; font-family: Pretendard; }
#t .s { font-size: 40px; font-weight: 600; color: #dcc48e; letter-spacing: .04em; }
#t .m { margin-top: 18px; font-size: 104px; font-weight: 700; color: #f6efe2; letter-spacing: -.01em; text-shadow: 0 2px 6px rgba(0,0,0,.5), 0 0 24px rgba(0,0,0,.35); }
#line { width: 120px; height: 3px; margin: 34px auto 0; background: linear-gradient(90deg, rgba(220,196,142,0), #dcc48e, rgba(220,196,142,0)); }
#logo { position: absolute; left: 50%; top: 860px; width: 300px; height: 105px; margin-left: -150px; background: rgba(255,255,255,.92);
  border-radius: 14px; padding: 10px 22px; box-shadow: 0 6px 18px rgba(0,0,0,.3); }
#logo img { width: 100%; height: 100%; object-fit: contain; }
</style><div id="bg"></div><div id="v"></div>
<div id="t"><div class="s">우리 곁의 평범한 이웃</div><div class="m">생활공감정책 참여단</div><div id="line"></div></div>
<div id="logo"><img src="file://${ROOT}/video/assets/img/gn_logo_color.svg"></div>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const tmp = path.join(P, '_end.html'); fs.writeFileSync(tmp, html);
  await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(P, 'endcard.png') }); fs.unlinkSync(tmp); await b.close(); console.log('ok');
})();
