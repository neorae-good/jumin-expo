import * as THREE from './assets/three.module.min.js';

const CFG = __CFG__;
const T0 = CFG.t0;
const B = (k) => CFG.b0 + CFG.step * k;
const ORDER = [[0, 0], [1, 0], [2, 0], [2, 1], [1, 1], [0, 1], [0, 2], [1, 2], [2, 2]];
const BW = 8.8, BH = 6.0;          // block size in world units
const CLW = BW * 3, CLH = BH * 3;  // cloth size
const PX = 200;                    // atlas px per unit

const canvas = document.getElementById('cloth');
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(1920, 1080, false);
renderer.setPixelRatio(1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, 1920 / 1080, 0.1, 300);
scene.add(new THREE.HemisphereLight(0xfff1dc, 0x4a2c18, 1.25));
const sun = new THREE.DirectionalLight(0xffdcaa, 2.4);
sun.position.set(14, 12, 18);
scene.add(sun);

const blockCenter = (k) => { const [bx, by] = ORDER[k]; return new THREE.Vector2((bx - 1) * BW, (1 - by) * BH); };

// ---------------------------------------------------------------- atlas
function loadImg(src) {
  return new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; });
}
function cover(ctx, im, x, y, w, h) {
  const s = Math.max(w / im.width, h / im.height);
  const sw = w / s, sh = h / s;
  ctx.drawImage(im, (im.width - sw) / 2, (im.height - sh) / 2, sw, sh, x, y, w, h);
}
function stitchRect(ctx, x, y, w, h, color, glow) {
  ctx.save();
  ctx.setLineDash([24, 16]);
  ctx.lineWidth = 6;
  ctx.strokeStyle = color;
  if (glow) { ctx.shadowColor = 'rgba(255,190,80,0.95)'; ctx.shadowBlur = 18; }
  ctx.strokeRect(x, y, w, h);
  ctx.restore();
}
async function buildAtlas() {
  await document.fonts.load('700 120px "HCR Batang"');
  await document.fonts.load('600 40px "Pretendard"');
  const linen = await loadImg('assets/img/linen.jpg');
  const W = CLW * PX, H = CLH * PX;
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  const s = PX / 100; // scale for block-local px (block = 880x600 at PX=100)
  for (let k = 0; k < 9; k++) {
    const [bx, by] = ORDER[k];
    const ox = bx * BW * PX, oy = by * BH * PX;
    const col = CFG.cols[k];
    // fabric base
    ctx.fillStyle = col.color;
    ctx.fillRect(ox, oy, BW * PX, BH * PX);
    ctx.save(); ctx.globalCompositeOperation = 'multiply';
    for (let lx = 0; lx < BW * PX; lx += 800) for (let ly = 0; ly < BH * PX; ly += 800) ctx.drawImage(linen, ox + lx, oy + ly, 800, 800);
    ctx.restore();
    const photos = await Promise.all(col.photos.map(f => loadImg('assets/photos/' + f)));
    const cells = [
      { x: 0, y: 200, w: 400, h: 400, im: photos[0], cap: col.caps[0] },
      { x: 400, y: 0, w: 480, h: 300, im: photos[1], cap: col.caps[1] },
      { x: 400, y: 300, w: 480, h: 300, im: photos[2], cap: col.caps[2] },
    ];
    for (const c of cells) {
      const x = ox + c.x * s, y = oy + c.y * s, w = c.w * s, h = c.h * s, b = 22 * s;
      const ch = 46 * s;
      cover(ctx, c.im, x + b, y + b, w - 2 * b, h - 2 * b - ch);
      ctx.fillStyle = '#efe2c4'; ctx.fillRect(x + b, y + h - b - ch, w - 2 * b, ch);
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(linen, x + b, y + h - b - ch, w - 2 * b, ch); ctx.restore();
      ctx.fillStyle = '#2b1b0c'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      let fs = 22 * s; ctx.font = `600 ${fs}px "Pretendard"`;
      while (ctx.measureText(c.cap).width > w - 2 * b - 24 * s && fs > 12 * s) { fs -= s; ctx.font = `600 ${fs}px "Pretendard"`; }
      ctx.fillText(c.cap, x + w / 2, y + h - b - ch / 2 + 2 * s);
      ctx.textAlign = 'left';
      stitchRect(ctx, x + b * 0.5, y + b * 0.5, w - b, h - b, '#ffd27a', true);
    }
    // name tag
    const tx = ox + 18 * s, ty = oy + 18 * s, tw = 364 * s, th = 164 * s;
    ctx.fillStyle = '#efe2c4'; ctx.fillRect(tx, ty, tw, th);
    ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(linen, tx, ty, tw, th); ctx.restore();
    stitchRect(ctx, tx + 14 * s, ty + 14 * s, tw - 28 * s, th - 28 * s, '#b8862e', false);
    ctx.fillStyle = '#7a5420'; ctx.font = `700 ${36 * s}px "HCR Batang"`; ctx.textBaseline = 'middle';
    ctx.fillText(String(col.num).padStart(2, '0'), tx + 40 * s, ty + th / 2 + 4 * s);
    ctx.fillStyle = '#2a1a0c'; ctx.font = `700 ${78 * s}px "HCR Batang"`;
    ctx.fillText(col.name, tx + 108 * s, ty + th / 2 + 4 * s);
    // block border stitches
    stitchRect(ctx, ox + 6 * s, oy + 6 * s, BW * PX - 12 * s, BH * PX - 12 * s, 'rgba(255,214,140,0.7)', false);
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  tex.generateMipmaps = true;
  tex.minFilter = THREE.LinearMipmapLinearFilter;
  return tex;
}

// ---------------------------------------------------------------- cloth + seams
const SX = 176, SY = 120;
const geo = new THREE.PlaneGeometry(CLW, CLH, SX, SY);
const base = geo.attributes.position.array.slice();
let amp = 1;
const wave = (x, y, t) =>
  amp * (0.17 * Math.sin(0.36 * x - 0.7 * t + 0.2 * y) + 0.06 * Math.sin(0.8 * x + 0.5 * y - 1.0 * t));
const mat = new THREE.MeshStandardMaterial({ roughness: 0.82, metalness: 0.0, side: THREE.DoubleSide, emissive: 0x2a1a08, emissiveIntensity: 0.35 });
const cloth = new THREE.Mesh(geo, mat);
scene.add(cloth);

// a gold ribbon along each shared edge between consecutive blocks
const seams = [];
const gold = new THREE.MeshBasicMaterial({ color: 0xffd27a, side: THREE.DoubleSide });
const glowMat = new THREE.MeshBasicMaterial({ color: 0xffb54a, transparent: true, opacity: 0.38, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
function ribbon(width, material) {
  const N = 80;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array((N + 1) * 2 * 3), 3));
  const idx = [];
  for (let i = 0; i < N; i++) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  g.setIndex(idx);
  const m = new THREE.Mesh(g, material);
  m.frustumCulled = false;
  scene.add(m);
  return { m, g, N, width };
}
for (let k = 1; k < 9; k++) {
  const a = blockCenter(k - 1), b = blockCenter(k);
  const horiz = Math.abs(a.y - b.y) < 0.01; // same row -> vertical shared edge
  const p0 = horiz ? new THREE.Vector2((a.x + b.x) / 2, a.y + BH / 2) : new THREE.Vector2(a.x - BW / 2, (a.y + b.y) / 2);
  const p1 = horiz ? new THREE.Vector2((a.x + b.x) / 2, a.y - BH / 2) : new THREE.Vector2(a.x + BW / 2, (a.y + b.y) / 2);
  if (!horiz && b.x < a.x) {} // keep direction
  seams.push({ k, p0, p1, horiz, core: ribbon(0.07, gold), glow: ribbon(0.42, glowMat) });
}
const tipTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const x = c.getContext('2d'); const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,240,1)'); g.addColorStop(0.25, 'rgba(255,220,140,0.9)'); g.addColorStop(1, 'rgba(255,160,40,0)');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const tip = new THREE.Sprite(new THREE.SpriteMaterial({ map: tipTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true }));
tip.scale.set(1.4, 1.4, 1);
scene.add(tip);

function setRibbon(r, p0, p1, horiz, prog, t) {
  const pos = r.g.attributes.position.array;
  const n = r.N;
  for (let i = 0; i <= n; i++) {
    const f = i / n;
    const x = p0.x + (p1.x - p0.x) * f, y = p0.y + (p1.y - p0.y) * f;
    const z = wave(x, y, t) + 0.03;
    const ox = horiz ? r.width / 2 : 0, oy = horiz ? 0 : r.width / 2;
    pos.set([x - ox, y - oy, z, x + ox, y + oy, z], i * 6);
  }
  r.g.attributes.position.needsUpdate = true;
  r.g.setDrawRange(0, Math.floor(n * prog) * 6);
}

// ---------------------------------------------------------------- camera path
const smooth = (u) => u * u * (3 - 2 * u);
const KEYS = [];
KEYS.push([T0, 0, 0, 34]);
KEYS.push([B(0) - 0.4, blockCenter(0).x, blockCenter(0).y, 10.6]);
for (let k = 0; k < 9; k++) {
  const c = blockCenter(k);
  KEYS.push([B(k), c.x, c.y, 10.6]);
  if (k < 8) KEYS.push([B(k + 1) - 1.0, c.x + 0.3, c.y - 0.08, 10.1]);
}
KEYS.push([CFG.wide0, blockCenter(8).x + 0.3, blockCenter(8).y - 0.08, 10.1]);
KEYS.push([CFG.wide1, 0, 0, 33]);
KEYS.push([CFG.end, 0, 0.5, 26]);
function camAt(t) {
  if (t <= KEYS[0][0]) return KEYS[0];
  for (let i = 1; i < KEYS.length; i++) {
    if (t <= KEYS[i][0]) {
      const a = KEYS[i - 1], b = KEYS[i];
      const u = smooth((t - a[0]) / (b[0] - a[0]));
      return [t, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u];
    }
  }
  return KEYS[KEYS.length - 1];
}

// ---------------------------------------------------------------- render
let ready = false;
function renderAt(time) {
  if (!ready) return;
  const t = time;
  const lt = t - T0;
  amp = t > CFG.wide0 ? 1 + Math.min(1, (t - CFG.wide0) / 4) * 0.4 : 1;
  const pos = geo.attributes.position.array;
  for (let i = 0; i < pos.length; i += 3) {
    const x = base[i], y = base[i + 1];
    pos[i + 2] = wave(x, y, lt);
    pos[i + 1] = y;
  }
  geo.attributes.position.needsUpdate = true;
  geo.computeVertexNormals();
  let tipOn = false;
  for (const s of seams) {
    const st = B(s.k) - 1.0, en = B(s.k) - 0.05;
    const prog = t <= st ? 0 : t >= en ? 1 : smooth((t - st) / (en - st));
    setRibbon(s.core, s.p0, s.p1, s.horiz, prog, lt);
    setRibbon(s.glow, s.p0, s.p1, s.horiz, prog, lt);
    if (prog > 0 && prog < 1) {
      const x = s.p0.x + (s.p1.x - s.p0.x) * prog, y = s.p0.y + (s.p1.y - s.p0.y) * prog;
      tip.position.set(x, y, wave(x, y, lt) + 0.1);
      tipOn = true;
    }
  }
  tip.visible = tipOn;
  glowMat.opacity = 0.38 + (t > CFG.wide0 ? 0.25 * (0.5 + 0.5 * Math.sin((t - CFG.wide0) * 3.0)) : 0);
  const [, cx, cy, d] = camAt(t);
  const orbit = 0.08 * Math.sin(lt * 0.15);
  camera.position.set(cx - 1.9 + orbit, cy - 2.6, d);
  camera.lookAt(cx, cy + 0.25, 0);
  camera.rotateZ(-0.03);
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady['cloth'] = buildAtlas().then((tex) => {
  mat.map = tex;
  mat.needsUpdate = true;
  ready = true;
  renderAt(window.__hfThreeTime || 0);
});
window.addEventListener('hf-seek', (e) => renderAt(e.detail.time));
