const tl = gsap.timeline({ paused: true });
const $ = (s) => document.querySelector(s);
const D = DATA;
const T = D.T;

// ------------------------------------------------------------------ helpers
const fadeIn = (sel, t, d = 1, to = 1) => tl.fromTo(sel, { opacity: 0 }, { opacity: to, duration: d, ease: 'power1.inOut', immediateRender: false }, t);
const push = (sel, t, d, a = 1, b = 1.08) => tl.fromTo(sel, { scale: a }, { scale: b, duration: d, ease: 'none', immediateRender: false }, t);
function leak(id, t, d = 2.6, peak = 0.85) {
  const el = '#' + id;
  tl.fromTo(el, { opacity: 0 }, { opacity: peak, duration: d * 0.3, ease: 'sine.out', immediateRender: false }, t);
  tl.to(el, { opacity: 0, duration: d * 0.45, ease: 'sine.in' }, t + d * 0.55);
  tl.fromTo(el + ' .la', { xPercent: -22, rotation: -4 }, { xPercent: 20, rotation: 3, duration: d, ease: 'sine.inOut', immediateRender: false }, t);
  tl.fromTo(el + ' .lr', { xPercent: 18, yPercent: -8 }, { xPercent: -16, yPercent: 8, duration: d, ease: 'sine.inOut', immediateRender: false }, t);
  tl.fromTo(el + ' .lg', { xPercent: -30, rotation: -6 }, { xPercent: 26, rotation: 4, duration: d, ease: 'sine.inOut', immediateRender: false }, t);
}
function flare(id, t0, t1, peak = 0.9) {
  const el = '#' + id;
  tl.fromTo(el, { opacity: 0 }, { opacity: peak, duration: 1.2, ease: 'sine.out', immediateRender: false }, t0);
  const n = Math.max(1, Math.floor((t1 - t0 - 2.2) / 2.2));
  tl.fromTo(el + ' .fcore', { scale: 0.92 }, { scale: 1.08, duration: 1.1, ease: 'sine.inOut', yoyo: true, repeat: n * 2 - 1, immediateRender: false }, t0);
  tl.fromTo(el + ' .fstreak', { scaleX: 0.85, opacity: 0.8 }, { scaleX: 1.1, opacity: 1, duration: 1.1, ease: 'sine.inOut', yoyo: true, repeat: n * 2 - 1, immediateRender: false }, t0);
  tl.to(el, { opacity: 0, duration: 1.0, ease: 'sine.in' }, t1 - 1.0);
}
const stitch = (id, t, d = 1.0) => tl.fromTo('#' + id + '-mr', { attr: { 'stroke-dashoffset': 1 } }, { attr: { 'stroke-dashoffset': 0 }, duration: d, ease: 'power1.inOut', immediateRender: false }, t);

// ------------------------------------------------------------------ global
tl.fromTo('#fade', { opacity: 1 }, { opacity: 0, duration: 1.4, ease: 'power1.out' }, 0);
tl.fromTo('#fade', { opacity: 0 }, { opacity: 1, duration: 3.0, ease: 'power1.in', immediateRender: false }, T.end - 3.0);
tl.fromTo('#dust', { opacity: 0 }, { opacity: 0.55, duration: 3, ease: 'none' }, 0.5);
tl.to('#dust', { opacity: 0.4, duration: 2 }, T.s2);
tl.to('#dust', { opacity: 0.6, duration: 2 }, T.s3);
tl.to('#dust', { opacity: 0.9, duration: 2 }, T.throw);
D.dust.forEach((p) => {
  const reps = Math.max(1, Math.floor(T.end / p.p) - 1);
  tl.fromTo('#dp' + p.i, { x: 0, y: 0, opacity: 0.15 }, { x: p.dx, y: p.dy, opacity: 1, duration: p.p, ease: 'sine.inOut', yoyo: true, repeat: reps }, p.ph);
});
tl.fromTo('#grain .gt', { x: 0, y: 0 }, { x: -60, y: 40, duration: 0.1, ease: 'steps(1)', yoyo: true, repeat: Math.floor(T.end * 10) - 1 }, 0);
// captions: units rise 20px over 0.6s, 0.3s apart; hold >= 3s; 0.5s fade out; fixed while readable
const capOn = [];
D.narr.forEach((n, i) => {
  const el = '#c-' + n.id;
  const units = document.querySelectorAll(el + ' .cu');
  const t0 = n.t - 0.15;
  const next = D.narr[i + 1] ? D.narr[i + 1].t - 0.6 : 999;
  const t1 = Math.min(next, Math.max(t0 + 0.3 * (units.length - 1) + 0.6 + 3.0, n.t + n.d + 0.5));
  tl.set(units, { opacity: 0, y: 20 }, 0);
  tl.set(el, { opacity: 0 }, 0);
  tl.set(el, { opacity: 1 }, t0);
  units.forEach((u, k) => {
    tl.fromTo(u, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, t0 + 0.3 * k);
  });
  tl.fromTo(el, { opacity: 1 }, { opacity: 0, duration: 0.5, ease: 'sine.inOut', immediateRender: false }, t1);
  capOn.push([t0, t1 + 0.5]);
});
capOn.forEach(([a, b], i) => {
  if (D.narr[i].lt) return; // v20: no dark caption gradient on the light template
  tl.fromTo('#capbg', { opacity: 0 }, { opacity: 1, duration: 0.5, immediateRender: false }, a);
  tl.to('#capbg', { opacity: 0, duration: 0.5 }, b - 0.5);
});

// ------------------------------------------------------------------ 기
// v20: three clean template slides (PPT-like) instead of the AI clips.
// slide k: text rises in from the left, page number turns; the 조각보 on the right grows 3 patches per slide
{
  const S = [0.6, 6.8, 13.4];            // slide starts (narration L01 at 1.0 s, L02 at 8.2 s)
  const drawPatch = (id, t) => {
    tl.fromTo('#' + id, { opacity: 0, scale: 0.92, y: -18 }, { opacity: 1, scale: 1, y: 0, duration: 0.7, ease: 'power3.out', immediateRender: false }, t);
    stitch(id, t + 0.3, 0.9);
  };
  S.forEach((t, k) => {
    const el = '#ts' + (k + 1);
    tl.fromTo(el, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: 0.8, ease: 'power2.out', immediateRender: false }, t);
    tl.fromTo(el + ' .rule', { scaleX: 0 }, { scaleX: 1, duration: 0.8, ease: 'power2.inOut', immediateRender: false }, t + 0.3);
    tl.fromTo(el + ' p', { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, t + 0.55);
    tl.fromTo('#pg' + (k + 1), { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, ease: 'sine.out', immediateRender: false }, t + 0.1);
    if (k < 2) {
      tl.to(el, { opacity: 0, x: 30, duration: 0.5, ease: 'power2.in' }, S[k + 1] - 0.45);
      tl.to('#pg' + (k + 1), { opacity: 0, y: -10, duration: 0.4, ease: 'sine.in' }, S[k + 1] - 0.3);
    }
    for (let j = 0; j < 3; j++) drawPatch('tq' + (k * 3 + j), t + 0.5 + j * 1.0);
  });
  // the finished square gets one gold stitch around it, then gently comes forward into the quilt world (승 at 19 s)
  tl.fromTo('#s1q-olr', { attr: { 'stroke-dashoffset': 1 } }, { attr: { 'stroke-dashoffset': 0 }, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, 17.0);
  tl.fromTo('#s1q-in', { scale: 1 }, { scale: 1.05, duration: 19.0, ease: 'none', immediateRender: false }, 0);
  tl.to('#s1q', { x: -40, y: 10, scale: 1.12, duration: 2.0, ease: 'power2.in' }, 18.0);
}

// ------------------------------------------------------------------ 승 + 전: one quilt, 18 regions
{
  const { M, CW, CH, WW, WH } = D;
  const cellPos = (c) => ({ x: 960 - (M + c.cx * CW + CW / 2), y: 540 - (M + c.cy * CH + CH / 2) - 40 });
  const half1 = { x: 960 - WW / 2, y: 540 - (M + 1.5 * CH) };
  const whole = { x: 960 - WW / 2, y: 540 - WH / 2 };
  const a = T.s2;
  leak('lk2', a - 0.7, 2.4, 0.45);
  tl.set(['#s2-cam', '.dof', '#s2-lamp', '#s2-far'], { opacity: 0 }, 0);
  tl.fromTo(['#s2-cam', '.dof', '#s2-lamp', '#s2-far'], { opacity: 0 }, { opacity: 1, duration: 0.9, immediateRender: false }, a);
  tl.set('#s2-tilt', { rotationX: 40, rotationZ: -10, scale: 0.34 }, 0);
  document.querySelectorAll('.qcap span').forEach((sp) => { const box = sp.parentElement.clientWidth - 48; let f = 34; while (sp.scrollWidth > box && f > 22) { f -= 1; sp.style.fontSize = f + 'px'; } });
  tl.set('#s2-world', { x: half1.x + 300, y: half1.y + 200 }, 0);
  tl.to('#s2-tilt', { rotationX: 12, rotationZ: -2, scale: 0.98, duration: 3.8, ease: 'power3.inOut' }, a + 0.1);
  tl.to('#s2-world', { ...cellPos(D.cells[0]), duration: 3.8, ease: 'power3.inOut' }, a + 0.1);
  const at = (k) => (k < 9 ? T.a0 + T.astep * k : T.b0 + T.bstep * (k - 9));
  const step = (k) => (k < 9 ? T.astep : T.bstep);
  D.cells.forEach((c, k) => {
    const t = at(k);
    const p = cellPos(c);
    const dir = c.flip ? -1 : 1;
    if (k > 0 && k !== 9) {
      const prev = cellPos(D.cells[k - 1]);
      tl.fromTo('#s2-world', { x: prev.x + 24, y: prev.y + 4 }, { x: p.x, y: p.y, duration: 0.9, ease: 'power3.inOut', immediateRender: false }, t - 0.9);
      tl.to('#s2-tilt', { scale: 0.9, rotationZ: 1.2 * dir, rotationX: 15, duration: 0.45, ease: 'power2.in' }, t - 0.9);
      tl.to('#s2-tilt', { scale: 0.98, rotationZ: -2 * dir, rotationX: 12, duration: 0.45, ease: 'power2.out' }, t - 0.45);
      tl.fromTo('#s2-blur', { opacity: 0 }, { opacity: 1, duration: 0.3, yoyo: true, repeat: 1, ease: 'sine.inOut', immediateRender: false }, t - 0.75);
    }
    if (k === 9) {
      // resume on the lower half after the thread close-up
      tl.set('#s2-world', { x: p.x - 160, y: p.y - 60 }, T.s3 - 0.4);
      tl.set('#s2-tilt', { rotationX: 22, rotationZ: -4, scale: 0.8 }, T.s3 - 0.4);
      tl.to('#s2-world', { x: p.x, y: p.y, duration: t - T.s3 + 0.4, ease: 'power3.out' }, T.s3 - 0.4);
      tl.to('#s2-tilt', { rotationX: 12, rotationZ: -2, scale: 0.98, duration: t - T.s3 + 0.4, ease: 'power3.out' }, T.s3 - 0.4);
    }
    tl.fromTo('#s2-world', { x: p.x, y: p.y }, { x: p.x + 24, y: p.y + 4, duration: step(k) - 1.0, ease: 'none', immediateRender: false }, t);
    const t0 = k === 9 ? T.s3 + 0.2 : (k ? t - 0.55 : t - 0.2);
    tl.fromTo('#' + c.t, { opacity: 0, scale: 1.18, y: -40 }, { opacity: 1, scale: 1, y: 0, duration: 0.6, ease: 'power3.out', immediateRender: false }, t0);
    stitch(c.t, t0 + 0.35, 0.8);
    c.p.forEach((pid, j) => {
      const tj = t0 + 0.2 + j * 0.3;
      tl.fromTo('#' + pid, { opacity: 0, scale: 1.14, y: -70, rotation: (j - 1) * 2.5 }, { opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.7, ease: 'power3.out', immediateRender: false }, tj);
      stitch(pid, tj + 0.35, 0.9);
      tl.fromTo('#' + pid + '-img', { scale: 1.14 }, { scale: 1.0, duration: 6, ease: 'none', immediateRender: false }, tj);
    });
    tl.fromTo('#s2-sweep', { xPercent: 0, opacity: 0 }, { xPercent: 330, opacity: 1, duration: 1.3, ease: 'power1.inOut', immediateRender: false }, t + 0.9);
    tl.to('#s2-sweep', { opacity: 0, duration: 0.3 }, t + 2.0);
  });
  // first pull back: the upper nine pieces
  tl.to('#s2-tilt', { rotationX: 38, rotationZ: -8, scale: 0.3, duration: 3.4, ease: 'power3.inOut' }, T.pb);
  tl.to('#s2-world', { ...half1, duration: 3.4, ease: 'power3.inOut' }, T.pb);
  tl.to('#s2-tilt', { rotationZ: -10, scale: 0.32, duration: 1.5, ease: 'none' }, T.pb + 3.4);
  leak('lk3', T.s2end - 1.6, 2.6, 0.45);
  tl.to(['#s2-cam', '#s2-lamp', '.dof', '#s2-far'], { opacity: 0, duration: 1.2, ease: 'power1.in' }, T.s2end - 1.3);
  // thread close-up between the halves
  fadeIn('#v5-w', T.v5, 1.0); push('#v5-w', T.v5, T.v5d, 1, 1.08);
  leak('lk3', T.s3 - 0.8, 2.4, 0.45);
  tl.fromTo(['#s2-cam', '#s2-lamp', '.dof', '#s2-far'], { opacity: 0 }, { opacity: 1, duration: 1.0, ease: 'power1.inOut', immediateRender: false }, T.s3 - 0.3);
  tl.to('#v5-w', { opacity: 0, duration: 1.0, ease: 'power1.inOut' }, T.s3 + 0.2);
  // final pull back: all eighteen pieces form one quilt
  tl.to('#s2-tilt', { rotationX: 30, rotationZ: -4, scale: 0.215, duration: 4.0, ease: 'power3.inOut' }, T.wide0);
  tl.to('#s2-world', { ...whole, duration: 4.0, ease: 'power3.inOut' }, T.wide0);
  tl.to('#s2-tilt', { rotationZ: -6, scale: 0.225, duration: T.throw - T.wide0 - 4.0, ease: 'none' }, T.wide0 + 4.0);
  tl.fromTo('#s2-sweep', { xPercent: 0, opacity: 0 }, { xPercent: 330, opacity: 1, duration: 2.0, ease: 'power1.inOut', immediateRender: false }, T.wide0 + 3.0);
  tl.to('#s2-sweep', { opacity: 0, duration: 0.4 }, T.wide0 + 4.9);
  tl.to(['#s2-cam', '#s2-lamp', '.dof', '#s2-far'], { opacity: 0, duration: 1.0, ease: 'power1.in' }, T.throw + 0.4);
}

// ------------------------------------------------------------------ 결: throw -> 3 photos -> title
fadeIn('#v11-w', T.throw, 0.9); push('#v11-w', T.throw, 12.0, 1, 1.06);
leak('lk4', T.throw - 0.8, 2.4, 0.4);
['#ph0', '#ph1', '#ph2'].forEach((id, k) => {
  const a = T.ph + k * T.phd;
  tl.fromTo(id, { opacity: 0 }, { opacity: 1, duration: 0.8, ease: 'sine.inOut', immediateRender: false }, a - 0.6);
  tl.fromTo(id + ' .phfr', { scale: 1.0, y: 10 }, { scale: 1.04, y: 0, duration: T.phd + 1.2, ease: 'none', immediateRender: false }, a - 0.6);
  tl.fromTo(id + ' .phbg', { scale: 1.08 }, { scale: 1.0, duration: T.phd + 1.2, ease: 'none', immediateRender: false }, a - 0.6);
  if (k < 2) tl.to(id, { opacity: 0, duration: 0.8, ease: 'sine.inOut' }, a + T.phd - 0.2);
});
tl.to('#ph2', { opacity: 0, duration: 1.0, ease: 'sine.inOut' }, T.fin - 0.2);
leak('lk6', T.fin - 0.8, 2.6, 0.4);
// v20: the ending sits on the same ivory template (the AI island clip is gone)
tl.fromTo('#s6bg', { opacity: 0 }, { opacity: 1, duration: 1.0, ease: 'power1.inOut', immediateRender: false }, T.fin - 0.2);
for (let k = 0; k < 18; k++) {
  const t = T.fin + 0.6 + k * 0.08;
  tl.fromTo('#fq' + k, { opacity: 0, scale: 0.9, y: -14 }, { opacity: 1, scale: 1, y: 0, duration: 0.6, ease: 'power3.out', immediateRender: false }, t);
  stitch('fq' + k, t + 0.25, 0.8);
}
// main title: a fine gold thread is drawn first, then the words rise; a single light sweep
tl.set('#finline', { opacity: 1 }, T.fin + 1.2);
tl.fromTo('#finline', { '--fx': 0 }, { '--fx': 1, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, T.fin + 1.2);
tl.fromTo('#finline .flt', { x: 0, opacity: 1 }, { x: 560, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, T.fin + 1.2);
tl.to('#finline .flt', { opacity: 0, duration: 0.4 }, T.fin + 2.6);
tl.set('#fin2', { opacity: 1 }, T.fin + 2.4);
tl.set('#fin2 .f2 .l1, #fin2 .f2 .l2', { opacity: 0, y: 20 }, 0);
tl.fromTo('#fin2 .f2 .l1', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 2.4);
tl.fromTo('#fin2 .f2 .l2', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 2.7);
tl.fromTo('#fin3', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 3.6);
tl.fromTo('#fin2 .f2s', { backgroundPosition: '100% 0' }, { backgroundPosition: '0% 0', duration: 1.6, ease: 'power1.inOut', immediateRender: false }, T.fin + 4.0);
tl.fromTo('#gnlogo', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 5.4);

window.__timelines['main'] = tl;
