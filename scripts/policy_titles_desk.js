// 생활공감정책 film, titles A안 on a real desk (Grok images/video, no people, no text in them):
//   node scripts/policy_titles_desk.js -> parts/policy/title_open.mp4 (6 s), parts/policy/title_end.mp4 (7 s),
//                                         parts/policy/title_sfx.json (pen / stamp cue times for the sound mix)
// Opening: gen/v21/memo_open_1.jpg (morning desk, 4 blank notes) with a slow push-in and drifting sunlight; the four
// inconveniences are handwritten onto the notes, then the title appears in the empty middle of the desk.
// Closing: gen/v21/memo_end_v.mp4 (evening desk, Grok lite) — the same notes are written, each gets a red ink stamp
// (개선 / 반영 / 채택 / 추진 중), then the closing words and the 경상남도 logo. Overlays follow the clip's tiny camera
// drift (parts/policy/memo_end_shift.json). Fonts (OFL): Nanum Pen Script, Gowun Batang.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const ROOT = path.resolve(__dirname, '..'); const P = path.join(ROOT, 'parts', 'policy');
const F = (f) => 'file://' + path.join(ROOT, f); const FPS = 30;
const TXT = [['길에 턱이', '너무 높아요', '개선'], ['산책로가 중간에', '끊겨 있어요', '반영'],
             ['다 같이 사진', '찍을 곳이 없어요', '채택'], ['점심시간엔', '우편을 못 보내요', '추진 중']];
const NOTES = {   // note boxes on each background (1920x1080): x0, y0, x1, y1, rotation
  open: [[264, 68, 615, 412, -4], [1335, 63, 1670, 405, 3], [333, 638, 687, 997, -3], [1200, 638, 1538, 990, 2]],
  end: [[170, 75, 552, 450, -3], [1265, 75, 1620, 440, 3], [218, 575, 590, 952, -3], [1290, 593, 1650, 968, 2]],
};
const CUE = { open: { write: (i) => 0.4 + i * 0.5, wdur: 0.8, title: 2.6 },
              end: { write: (i) => 0.9 + i * 0.22, wdur: 0.55, stamp: (i) => 2.0 + i * 0.42, title: 4.0, logo: 5.0 } };
const page = (kind) => `<!doctype html><meta charset="utf-8"><style>
@font-face { font-family: "Pen"; src: url("${F('fonts_dl/pen/NanumPenScript.ttf')}"); }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Bold.ttf')}"); font-weight: 700; }
@font-face { font-family: "Gowun"; src: url("${F('fonts_dl/gowun/GowunBatang-Regular.ttf')}"); font-weight: 400; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1920px; height: 1080px; overflow: hidden; background: ${kind === 'open' ? '#000' : 'transparent'}; }
#bg { position: absolute; inset: 0; background: url("${F('gen/v21/memo_open_1.jpg')}") center/cover; transform-origin: 50% 50%; }
#sun { position: absolute; inset: -200px; mix-blend-mode: soft-light;
  background: repeating-linear-gradient(115deg, rgba(255,226,170,0) 0 120px, rgba(255,226,170,.55) 160px 210px, rgba(255,226,170,0) 260px 420px); }
#world { position: absolute; inset: 0; transform-origin: 50% 50%; }
.note { position: absolute; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; padding: 40px 30px 0 34px; }
.ln { font-family: "Pen"; font-size: 64px; line-height: 1.12; color: #1d2340; white-space: nowrap; opacity: .92; }
.stamp { position: absolute; right: 12px; bottom: 10px; width: 140px; height: 140px; opacity: 0; filter: url(#ink); }
.stamp div { position: absolute; inset: 0; border-radius: 50%; border: 7px solid #c42a2a; display: flex; align-items: center; justify-content: center;
  color: #c42a2a; font-family: "Gowun"; font-weight: 700; font-size: 40px; white-space: nowrap; }
.stamp div::after { content: ""; position: absolute; inset: 7px; border-radius: 50%; border: 2px solid #c42a2a; }
#glow { position: absolute; left: 0; right: 0; top: ${kind === 'open' ? 395 : 430}px; height: 280px; opacity: 0;
  background: radial-gradient(ellipse 45% 50% at 50% 50%, rgba(20,10,4,.55), rgba(20,10,4,0)); }
#txt { position: absolute; left: 0; right: 0; top: ${kind === 'open' ? 428 : 452}px; text-align: center; font-family: "Gowun"; }
.sub { font-weight: 400; font-size: 40px; letter-spacing: .14em; color: #fbe9bf; opacity: 0; text-shadow: 0 2px 10px rgba(0,0,0,.75); }
.main { margin-top: 14px; font-weight: 700; font-size: 104px; color: #fffaf0; white-space: nowrap; text-shadow: 0 3px 12px rgba(0,0,0,.75), 0 0 30px rgba(0,0,0,.45); }
.main span { display: inline-block; opacity: 0; }
#logo { position: absolute; left: 50%; top: 880px; width: 280px; height: 98px; margin-left: -140px; background: rgba(255,255,255,.94); border-radius: 14px; padding: 9px 20px; box-shadow: 0 6px 18px rgba(0,0,0,.35); opacity: 0; }
#logo img { width: 100%; height: 100%; object-fit: contain; }
</style>
<svg width="0" height="0" style="position:absolute"><filter id="ink"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -0.7 1.2" result="m"/>
<feComposite in="SourceGraphic" in2="m" operator="in"/></filter></svg>
${kind === 'open' ? '<div id="bg"></div><div id="sun"></div>' : ''}
<div id="world">
${NOTES[kind].map(([x0, y0, x1, y1, r], i) => `<div class="note" style="left:${x0}px;top:${y0}px;width:${x1 - x0}px;height:${y1 - y0}px;transform:rotate(${r}deg)">
  <div class="ln" id="a${i}">${TXT[i][0]}</div><div class="ln" id="b${i}">${TXT[i][1]}</div>
  ${kind === 'end' ? `<div class="stamp" id="s${i}"><div style="${TXT[i][2].length > 2 ? 'font-size:30px' : ''}">${TXT[i][2]}</div></div>` : ''}</div>`).join('')}
</div>
<div id="glow"></div>
<div id="txt"><div class="sub" id="sub">${kind === 'open' ? '우리 곁의 평범한 이웃' : '경남의 일상을 함께 바꿔 갑니다'}</div>
<div class="main" id="main">${[...'생활공감정책 참여단'].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join('')}</div></div>
${kind === 'end' ? `<div id="logo"><img src="${F('video/assets/img/gn_logo_color.svg')}"></div>` : ''}
<script>
const KIND = ${JSON.stringify(kind)}, DUR = KIND === 'open' ? 6 : 7;
const SHIFT = ${kind === 'end' ? fs.readFileSync(path.join(P, 'memo_end_shift.json'), 'utf8') : '[]'};
const C = { write: ${CUE[kind].write.toString()}, wdur: ${CUE[kind].wdur}, stamp: ${CUE[kind].stamp ? CUE[kind].stamp.toString() : 'null'},
            title: ${CUE[kind].title}, logo: ${CUE[kind].logo || 99} };
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)); const smooth = (t) => { t = clamp(t); return t * t * (3 - 2 * t); };
const ease = (t) => 1 - Math.pow(1 - clamp(t), 3);
const back = (t) => { t = clamp(t); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const $ = (id) => document.getElementById(id);
window.draw = (t, k) => {
  const push = 1 + 0.06 * (t / DUR);
  if (KIND === 'open') { $('bg').style.transform = 'scale(' + push + ')'; $('world').style.transform = 'scale(' + push + ')';
    $('sun').style.transform = 'translateX(' + (-60 + 120 * t / DUR) + 'px)'; }
  else { const s = SHIFT[Math.min(k, SHIFT.length - 1)] || [0, 0]; $('world').style.transform = 'translate(' + s[0] + 'px,' + s[1] + 'px)'; }
  for (let i = 0; i < 4; i++) {          // handwriting: line 1 then line 2, revealed left to right
    const w0 = C.write(i), half = C.wdur / 2;
    $('a' + i).style.clipPath = 'inset(-20px ' + (100 - 100 * clamp((t - w0) / half)) + '% -20px -10px)';
    $('b' + i).style.clipPath = 'inset(-20px ' + (100 - 100 * clamp((t - w0 - half) / half)) + '% -20px -10px)';
    if (C.stamp) { const sp = (t - C.stamp(i)) / 0.14, s = $('s' + i);
      if (sp > 0) { s.style.opacity = clamp(sp * 1.5).toFixed(3); s.style.transform = 'rotate(' + (-14 + i * 9) + 'deg) scale(' + (1 + .8 * (1 - back(sp))) + ')'; } }
  }
  const T0 = C.title;
  $('glow').style.opacity = smooth((t - T0 + .2) / .8);
  $('sub').style.opacity = smooth((t - T0) / .7);
  [...document.querySelectorAll('#main span')].forEach((s, i) => { const v = ease((t - T0 - .3 - i * .055) / .7);
    s.style.opacity = v; s.style.transform = 'translateY(' + (22 * (1 - v)) + 'px)'; s.style.filter = 'blur(' + (5 * (1 - v)) + 'px)'; });
  if ($('logo')) $('logo').style.opacity = smooth((t - C.logo) / .7);
};
</script>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const sfx = { open: { pen: [0, 1, 2, 3].map(CUE.open.write), wdur: CUE.open.wdur },
                end: { pen: [0, 1, 2, 3].map(CUE.end.write), wdur: CUE.end.wdur, stamp: [0, 1, 2, 3].map(CUE.end.stamp) } };
  fs.writeFileSync(path.join(P, 'title_sfx.json'), JSON.stringify(sfx));
  for (const [kind, dur] of [['open', 6.0], ['end', 7.0]]) {
    const dir = path.join(P, `_d_${kind}`); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const tmp = path.join(P, `_d_${kind}.html`); fs.writeFileSync(tmp, page(kind));
    await p.goto('file://' + tmp); await p.evaluate(() => document.fonts.ready);
    const n = Math.round(dur * FPS);
    for (let k = 0; k < n; k++) { await p.evaluate(([t, kk]) => window.draw(t, kk), [k / FPS, k]);
      await p.screenshot({ path: path.join(dir, `f${String(k).padStart(4, '0')}.png`), omitBackground: kind === 'end' }); }
    const out = path.join(P, `title_${kind}.mp4`);
    if (kind === 'open') execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'), '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p', out]);
    else execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', path.join(ROOT, 'gen/v21/memo_end_v.mp4'), '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'),
      '-filter_complex', `[0:v]fps=30,scale=1920:1080:flags=lanczos,setsar=1,trim=duration=${dur},setpts=PTS-STARTPTS[b];[b][1:v]overlay=format=auto,format=yuv420p[v]`,
      '-map', '[v]', '-t', String(dur), '-c:v', 'libx264', '-crf', '14', out]);
    fs.rmSync(dir, { recursive: true, force: true }); fs.unlinkSync(tmp); console.log('ok', `title_${kind}.mp4`);
  }
  await b.close();
})();
