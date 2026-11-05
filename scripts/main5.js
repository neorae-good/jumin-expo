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
// v21: opening without AI clips. JV a = camera over the same quilt cloth, b = photo wall on the cloth.
const tagIn = (id, t, d = 0.7) => {
  tl.fromTo('#' + id, { opacity: 0, scale: 1.12, y: -40 }, { opacity: 1, scale: 1, y: 0, duration: d, ease: 'power3.out', immediateRender: false }, t);
  stitch(id, t + 0.35, 0.9);
};
const tagOut = (id, t) => tl.to('#' + id, { opacity: 0, y: 20, duration: 0.6, ease: 'power2.in' }, t);
if (['a', 'g', 'gv', 'm'].includes(D.jv)) {
  const { M, CW, CH, WW } = D;
  const P0 = D.intro.P0, P1 = D.intro.P1;
  const at = (x, y) => ({ x: 960 - x, y: 540 - y - 40 });
  const half1 = { x: 960 - WW / 2, y: 540 - (M + 1.5 * CH) };
  tl.set('#i-tilt', { rotationX: 14, rotationZ: -2, scale: 0.95 }, 0);
  tl.set('#i-world', at(P0[0] - 120, P0[1] + 40), 0);
  // slow drift over the cloth while the gold thread is sewn across it
  tl.to('#i-world', { ...at(P0[0] + 160, P0[1] + 60), duration: 6.4, ease: 'none' }, 0);
  tl.to('#i-tilt', { rotationZ: 0, duration: 6.4, ease: 'none' }, 0);
  tl.fromTo('#ith-mr', { attr: { 'stroke-dashoffset': 1 } }, { attr: { 'stroke-dashoffset': 0 }, duration: 12.0, ease: 'none', immediateRender: false }, 0.4);
  tagIn('it1', 1.0);
  // glide along the thread to the next stretch of cloth
  tl.to('#i-world', { ...at(P1[0], P1[1] - 90), duration: 1.4, ease: 'power3.inOut' }, 6.4);
  tl.to('#i-tilt', { scale: 0.86, rotationX: 17, duration: 0.7, ease: 'power2.in' }, 6.4);
  tl.to('#i-tilt', { scale: 0.95, rotationX: 14, duration: 0.7, ease: 'power2.out' }, 7.1);
  tl.to('#i-world', { ...at(P1[0] + 140, P1[1] - 70), duration: 5.6, ease: 'none' }, 7.8);
  tagIn('it2', 7.4);
  ['ip0', 'ip1', 'ip2'].forEach((pid, j) => {
    const tj = 8.6 + j * 0.9;
    tl.fromTo('#' + pid, { opacity: 0, scale: 1.14, y: -70, rotation: (j - 1) * 2.5 }, { opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.7, ease: 'power3.out', immediateRender: false }, tj);
    stitch(pid, tj + 0.35, 0.9);
    tl.fromTo('#' + pid + '-img', { scale: 1.14 }, { scale: 1.0, duration: 6, ease: 'none', immediateRender: false }, tj);
  });
  // pull back: the whole cloth comes into view, then the region pieces start (승, 19 s) from this exact framing
  tl.to('#i-tilt', { rotationX: 40, rotationZ: -10, scale: 0.34, duration: 5.0, ease: 'power3.inOut' }, 13.4);
  tl.to('#i-world', { x: half1.x + 300, y: half1.y + 200, duration: 5.0, ease: 'power3.inOut' }, 13.4);
  tl.to(['#it1', '#it2', '#ip0', '#ip1', '#ip2', '.ith'], { opacity: 0, duration: 1.0, ease: 'sine.inOut' }, 13.6);
  tl.fromTo('#it3', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', immediateRender: false }, 14.8);
  stitch('it3', 15.1, 0.9);
  tagOut('it3', 18.0);
  if (D.jv === 'gv') {
    // 2안: Grok clips over the cloth: dawn + threaded needle (L01), drop -> golden stitch (L02); then the quilt pull-back
    tl.set(['#it1', '#it2', '#ip0', '#ip1', '#ip2', '.ith'], { visibility: 'hidden' }, 0);
    tl.set('#g1-w', { opacity: 1 }, 0); push('#g1-w', 0, 7.8, 1.0, 1.06);
    fadeIn('#g2-w', 7.0, 0.8); push('#g2-w', 7.0, 7.4, 1.0, 1.06);
    tl.to('#g2-w', { opacity: 0, duration: 1.0, ease: 'power1.inOut' }, 13.4);
  }
  if (D.jv === 'm') {
    // 3안: letters as a window onto real photos -> inhale -> rush through a stroke -> the photo takes the frame
    tl.set(['#it1', '#it2', '#ip0', '#ip1', '#ip2', '.ith'], { visibility: 'hidden' }, 0);
    const O = { x: 1230, y: 537 };
    tl.fromTo('#mk-word', { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.55, ease: 'power3.out', immediateRender: false }, 0.05);
    tl.fromTo('#mk-eyebrow', { opacity: 0, letterSpacing: '0.6em' }, { opacity: 1, letterSpacing: '0.32em', duration: 0.7, ease: 'power2.out', immediateRender: false }, 0.25);
    tl.fromTo('#mk-sub', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', immediateRender: false }, 0.4);
    tl.fromTo('#mk-photo', { x: -300 }, { x: -1500, duration: 2.75, ease: 'sine.inOut', immediateRender: false }, 0);
    tl.to('#mk-word', { scale: 0.965, svgOrigin: O.x + ' ' + O.y, duration: 0.3, ease: 'power2.inOut' }, 2.45);
    tl.to(['#mk-eyebrow', '#mk-sub'], { opacity: 0, duration: 0.3, ease: 'power2.in' }, 2.45);
    const rush = { t: 0 };
    tl.to(rush, { t: 1, duration: 0.8, ease: 'none', onUpdate: () => {
      const k = Math.pow(rush.t, 1.8);
      gsap.set('#mk-word', { scale: 0.965 * Math.pow(46 / 0.965, k), svgOrigin: O.x + ' ' + O.y, x: (960 - O.x) * rush.t, y: (540 - O.y) * rush.t });
    } }, 2.75);
    tl.to('#mk-photo', { x: -1920, duration: 0.9, ease: 'expo.out' }, 2.75);
    tl.to('#mk-stage', { opacity: 0, duration: 0.25, ease: 'none' }, 3.3);
    // hand over to the same photo as its own layer (identical framing), then the L01/L02 photos
    tl.set('#m1-w', { opacity: 1 }, 3.6); tl.set('#mk', { opacity: 0 }, 3.62);
    tl.fromTo('#m1', { scale: 1.0 }, { scale: 1.10, duration: 6.6, ease: 'sine.inOut', immediateRender: false }, 3.6);
    fadeIn('#m2-w', 9.7, 0.8);
    tl.fromTo('#m2', { scale: 1.08, xPercent: 1.5 }, { scale: 1.0, xPercent: -1.0, duration: 3.6, ease: 'sine.inOut', immediateRender: false }, 9.7);
    fadeIn('#m3-w', 12.6, 0.8);
    tl.fromTo('#m3', { scale: 1.0 }, { scale: 1.08, duration: 3.0, ease: 'sine.inOut', immediateRender: false }, 12.6);
    tl.to(['#m2-w', '#m3-w', '#m1-w'], { opacity: 0, duration: 1.0, ease: 'power1.inOut' }, 14.6);
  }
  if (D.jv === 'g') {
    // Grok clips over the cloth: dawn + threaded needle (L01), drop -> golden stitch (L02); then reveal the quilt pull-back
    tl.set(['#it1', '#it2', '#ip0', '#ip1', '#ip2', '.ith'], { visibility: 'hidden' }, 0);
    // stills: dawn light grows over the threaded needle; the drop, then the drop on a freshly stitched golden seam
    tl.set('#g1-w', { opacity: 1 }, 0);
    tl.fromTo('#g1', { scale: 1.0, xPercent: 0, yPercent: 0, filter: 'brightness(0.86)' }, { scale: 1.14, xPercent: -2.5, yPercent: 2.0, filter: 'brightness(1.06)', duration: 7.8, ease: 'sine.inOut', immediateRender: false }, 0);
    leak('lk1', 0.6, 4.2, 0.30);
    fadeIn('#g2-w', 7.0, 0.9);
    tl.fromTo('#g2', { scale: 1.04, yPercent: -1.5 }, { scale: 1.12, yPercent: 1.0, duration: 4.4, ease: 'sine.inOut', immediateRender: false }, 7.0);
    fadeIn('#g3-w', 10.6, 1.0);
    tl.fromTo('#g3', { scale: 1.10 }, { scale: 1.02, duration: 3.8, ease: 'sine.out', immediateRender: false }, 10.6);
    leak('lk2', 10.9, 2.4, 0.25);
    tl.to(['#g2-w', '#g3-w'], { opacity: 0, duration: 1.0, ease: 'power1.inOut' }, 13.4);
  }
} else {
  const o = D.intro.order;
  tl.set('#c-tilt', { rotationX: 18, rotationZ: -3, scale: 1.25 }, 0);
  tl.to('#c-tilt', { rotationX: 10, rotationZ: 0, scale: 1.08, duration: 13.4, ease: 'sine.inOut' }, 0);
  o.forEach((i, k) => {
    const t = k < 4 ? 1.2 + k * 0.9 : (k < 12 ? 7.4 + (k - 4) * 0.6 : 13.0 + (k - 12) * 0.22);
    tl.fromTo('#cf' + i, { opacity: 0, scale: 1.16, y: -50, rotation: ((i % 3) - 1) * 3 }, { opacity: 1, scale: 1, y: 0, rotation: 0, duration: 0.7, ease: 'power3.out', immediateRender: false }, t);
  });
  tagIn('it1', 0.8); tagOut('it1', 6.3);
  tagIn('it2', 6.9); tagOut('it2', 12.9);
  tagIn('it3', 13.6); tagOut('it3', 17.8);
  // pull back and tilt like the quilt world before the region pieces start
  tl.to('#c-tilt', { rotationX: 40, rotationZ: -10, scale: 0.5, duration: 4.0, ease: 'power3.inOut' }, 15.6);
  tl.to('#c-cam', { opacity: 0, duration: 1.0, ease: 'sine.in' }, 18.4);
  leak('lk1', 18.3, 2.4, 0.45);
}
// ------------------------------------------------------------------ 승 + 전: one quilt, 18 regions
{
  const { M, CW, CH, WW, WH } = D;
  const cellPos = (c) => ({ x: 960 - (M + c.cx * CW + CW / 2), y: 540 - (M + c.cy * CH + CH / 2) - 40 });
  const half1 = { x: 960 - WW / 2, y: 540 - (M + 1.5 * CH) };
  const whole = { x: 960 - WW / 2, y: 540 - WH / 2 };
  const a = T.s2;
  if (D.jv === 'b') leak('lk2', a - 0.7, 2.4, 0.45);
  tl.set(['#s2-cam', '#s2 .dof', '#s2-lamp', '#s2-far'], { opacity: 0 }, 0);
  if (D.jv === 'b') tl.fromTo(['#s2-cam', '#s2 .dof', '#s2-lamp', '#s2-far'], { opacity: 0 }, { opacity: 1, duration: 0.9, immediateRender: false }, a);
  else tl.set(['#s2-cam', '#s2 .dof', '#s2-lamp', '#s2-far'], { opacity: 1 }, a);  // opening ends on this exact framing: switch on the first frame (no 1-frame flash of the bare background)
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
// v21: the ending sits on the finished quilt (a) or the photo wall (b)
tl.fromTo('#s6bg', { opacity: 0 }, { opacity: 1, duration: 1.0, ease: 'power1.inOut', immediateRender: false }, T.fin - 0.2);
if (D.jv === 'gv') {
  // the sky clip now sits at top level (not inside #s6bg), so it needs its own 1 s crossfade like #s6bg had
  tl.fromTo('#g9-w', { opacity: 0 }, { opacity: 1, duration: 1.0, ease: 'power1.inOut', immediateRender: false }, T.fin - 0.2); push('#g9-w', T.fin - 0.2, T.end - T.fin + 0.2, 1.0, 1.05);
} else if (D.jv === 'm') {
  tl.set('#m9-w', { opacity: 1 }, T.fin - 0.2);
  tl.fromTo('#m9', { scale: 1.0 }, { scale: 1.08, duration: T.end - T.fin + 0.2, ease: 'sine.inOut', immediateRender: false }, T.fin - 0.2);
} else if (D.jv === 'g') {
  tl.set('#g9-w', { opacity: 1 }, T.fin - 0.2);
  tl.fromTo('#g9', { scale: 1.02, yPercent: 1.5 }, { scale: 1.12, yPercent: -1.5, duration: T.end - T.fin + 0.2, ease: 'sine.inOut', immediateRender: false }, T.fin - 0.2);
} else if (D.jv === 'a') {
  tl.fromTo('#ebg', { scale: 1.08 }, { scale: 1.0, duration: T.end - T.fin + 0.2, ease: 'none', immediateRender: false }, T.fin - 0.2);
} else {
  tl.fromTo('#ewall', { scale: 1.1 }, { scale: 1.0, duration: T.end - T.fin + 0.2, ease: 'none', immediateRender: false }, T.fin - 0.2);
  for (let i = 0; i < 54; i++) tl.set('#ef' + i, { opacity: 1 }, 0);
}
tl.fromTo('#s6g', { opacity: 0 }, { opacity: 1, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, T.fin);
// main title: a fine gold thread is drawn first, then the words rise; a single light sweep
tl.set('#finline', { opacity: 1 }, T.fin + 1.2);
tl.fromTo('#finline', { '--fx': 0 }, { '--fx': 1, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, T.fin + 1.2);
tl.fromTo('#finline .flt', { x: 0, opacity: 1 }, { x: 560, duration: 1.4, ease: 'power1.inOut', immediateRender: false }, T.fin + 1.2);
tl.to('#finline .flt', { opacity: 0, duration: 0.4 }, T.fin + 2.6);
tl.set('#fin2', { opacity: 1 }, T.fin + 2.4);
tl.set('#fin2 .f2 .l1, #fin2 .f2 .l2', { opacity: 0, y: 20 }, 0);
tl.fromTo('#fin2 .f2 .l1', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 2.4);
tl.fromTo('#fin2 .f2 .l2', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 2.7);
// v30: the event line is embroidered: a needle runs left to right, the letters (satin-stitch texture) and a gold running stitch appear behind it
tl.set('#fin3', { opacity: 1 }, T.fin + 3.3);
tl.fromTo('#fin3 .f3w', { '--p': 0 }, { '--p': 1, duration: 2.4, ease: 'sine.inOut', immediateRender: false }, T.fin + 3.3);
tl.fromTo('#fin3 .f3n', { opacity: 0 }, { opacity: 1, duration: 0.25, immediateRender: false }, T.fin + 3.15);
tl.fromTo('#fin3 .f3n', { y: -5 }, { y: 5, duration: 0.15, ease: 'sine.inOut', repeat: 15, yoyo: true, immediateRender: false }, T.fin + 3.3);
tl.to('#fin3 .f3n', { opacity: 0, duration: 0.4 }, T.fin + 5.6);
tl.fromTo('#fin2 .f2s', { backgroundPosition: '100% 0' }, { backgroundPosition: '0% 0', duration: 1.6, ease: 'power1.inOut', immediateRender: false }, T.fin + 4.0);
tl.fromTo('#gnlogo', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: 'sine.out', immediateRender: false }, T.fin + 5.4);
flare('fl6', T.fin + 0.4, T.end, 0.5);
leak('lk6', T.fin + 3.0, 3.0, 0.45);

window.__timelines['main'] = tl;
