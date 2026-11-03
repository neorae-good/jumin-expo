import json, os, subprocess, sys, numpy as np, wave
from pathlib import Path
R = str(Path(__file__).resolve().parents[1])
VN = sys.argv[1]  # bomi | kanika
TAG = sys.argv[2]  # output tag, e.g. less | dry
WET_DB = None if sys.argv[3] == 'off' else float(sys.argv[3])  # room level relative to the dry voice
RT60 = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
BGM = sys.argv[5] if len(sys.argv) > 5 else 'bgm4_fast.wav'  # v20: faster music (scripts/music_fast.py); v19 used bgm3.wav
SR = 48000

# optional per-variant start times (e.g. NARR_T=narr/t_m.json for 3안, where L01/L02 follow the title card)
def _narr_lines(path):
    import json as _j, os as _o
    L = _j.load(open(path, encoding='utf-8'))
    if _o.environ.get('NARR_T'):
        o = _j.load(open(_o.path.join(R if 'R' in globals() else str(ROOT), _o.environ['NARR_T']), encoding='utf-8'))
        for x in L:
            if x['id'] in o: x['t'] = o[x['id']]
    return L
def load(f, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', f]
    if af: cmd += ['-af', af]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
def movavg(x, w):
    c = np.cumsum(np.r_[0, x]); y = (c[w:] - c[:-w]) / w
    return np.r_[np.full(w // 2, y[0]), y, np.full(len(x) - len(y) - w // 2, y[-1])]
TOTAL = 178.0
N = int(TOTAL * SR)
bgm = load(os.path.join(R, 'audio', BGM))[:N]
bgm = np.pad(bgm, ((0, N - len(bgm)), (0, 0)))
# narration: present, punchy, a touch of hall
# v17: natural, unprocessed-sounding voice (no slap echo); a soft synthetic room is added below
NAF = 'highpass=f=75,equalizer=f=200:t=q:w=1:g=1.0,equalizer=f=3000:t=q:w=1.2:g=2.5,equalizer=f=9000:t=q:w=1:g=0.5,deesser=i=0.3,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2.5,loudnorm=I=-15:TP=-1.5:LRA=7'
nar = np.zeros((N, 2), np.float32)
for x in _narr_lines(R + '/narr/script6.json'):
    _p = R + '/narr/v8p/' + VN + '/' + x['id'] + '.wav'
    if not os.path.exists(_p): print('SKIP', x['id']); continue
    a = load(_p, NAF)
    i = int(x['t'] * SR); nar[i:i + len(a)] += a[:N - i] * db(2.5)
# soft room: exponentially decaying filtered noise, 18 ms pre-delay, RT60 ~0.7 s, about -17 dB wet
rng = np.random.default_rng(7)
n_ir = int(0.9 * SR); tt = np.arange(n_ir) / SR
ir = rng.standard_normal((n_ir, 2)) * np.exp(-6.9 * tt / RT60)[:, None]
from scipy.signal import butter, sosfilt, fftconvolve
ir = sosfilt(butter(2, [250, 5000], btype='band', fs=SR, output='sos'), ir, axis=0)
ir = np.vstack([np.zeros((int(0.018 * SR), 2)), ir]); ir /= np.sqrt((ir ** 2).sum(0))
wet = np.zeros_like(nar) if WET_DB is None else np.stack([fftconvolve(nar[:, c], ir[:, c])[:N] for c in range(2)], 1).astype(np.float32) * db(WET_DB)
stem = (nar + wet) * 0.7
with wave.open(R + '/audio/narr_stem9_' + TAG + '.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(stem, -1, 1) * 32767).astype(np.int16).tobytes())
# duck the music under the voice (~-7 dB), smooth attack/release
env = np.abs(nar).max(1)
win = int(0.05 * SR)
env = movavg(env, win)
gate = (env > 0.01).astype(np.float32)
# hold the duck 0.45 s after each phrase ends (and open 0.1 s early) so soft sentence endings are not masked
from scipy.ndimage import maximum_filter1d
hold, pre = int(0.45 * SR), int(0.10 * SR)
gate = maximum_filter1d(gate, size=hold + pre + 1, origin=(pre - hold) // 2)
k = int(0.25 * SR)
gate = movavg(gate, k)
gate = np.clip(gate * 1.6, 0, 1)
# voiceover carve: the music keeps its low end and air (-4 dB) while the speech band 300-4000 Hz dips (-9 dB)
from scipy.signal import sosfiltfilt
SPB = butter(2, [300, 4000], btype='band', fs=SR, output='sos')
band = lambda a: sosfiltfilt(SPB, a, axis=0).astype(np.float32)
bmid = band(bgm); brest = bgm - bmid
gmid = 1 - 0.72 * gate
# per line: keep the voice at least 12 dB over the music inside the speech band (deeper carve on loud climaxes, max +6 dB)
rmsdb = lambda a: 10 * np.log10((a.astype(np.float64) ** 2).mean() + 1e-12)
nmid = band(nar)
extra = np.zeros(N, np.float32)
for x in _narr_lines(R + '/narr/script6.json'):
    _p = R + '/narr/v8p/' + VN + '/' + x['id'] + '.wav'
    if not os.path.exists(_p): continue
    i0 = int(x['t'] * SR); i1 = min(N, i0 + int((float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', _p], capture_output=True, text=True).stdout) + 0.45) * SR))
    v, mu = rmsdb(nmid[i0:i1]), rmsdb(bmid[i0:i1] * gmid[i0:i1, None])
    need = min(8.0, max(0.0, float(os.environ.get('CARVE_TARGET', '11')) - (v - mu)))  # v22: CARVE_TARGET=14 keeps the male voices clearer
    print(f"{x['id']} speech-band voice-music {v - mu:5.1f} dB, extra carve {need:.1f} dB")
    if need > 0: extra[i0:i1] = np.maximum(extra[i0:i1], need)
extra = movavg(extra, int(0.3 * SR)).astype(np.float32)
bgm = brest * (1 - 0.45 * gate)[:, None] + bmid * (gmid * 10 ** (-extra / 20))[:, None]
# sound effects
P = json.load(open(os.path.join(R, 'sfx', 'pick.json')))
boom = load(os.path.join(R, P['boom']['file']), 'aecho=0.8:0.75:70|160|300:0.45|0.3|0.2,lowpass=f=6000')
wh = load(os.path.join(R, P['whoosh']['file'])); wp = P['whoosh']['peak']; wh = wh[int(max(0, wp - 1.0) * SR):int((wp + 0.6) * SR)]
fade = np.linspace(0, 1, int(0.08 * SR))[:, None]; wh[:len(fade)] *= fade; wh[-len(fade):] *= fade[::-1]
sh = load(os.path.join(R, P['shimmer']['file']), 'aecho=0.8:0.8:120|240:0.4|0.25')
sfx = np.zeros((N, 2), np.float32)
def put(a, t, g, peak=0.0):
    i = int((t - peak) * SR)
    if i < 0: a = a[-i:]; i = 0
    sfx[i:i + len(a)] += a[:N - i] * db(g)
T = {'s2': 19.0, 'a0': 23.4, 'astep': 5.4, 'pb': 70.0, 'big': 83.3, 'b0': 86.6, 'bstep': 5.0, 'wide0': 131.0, 'throw': 139.2}
for t, g in [(T['s2'] + 0.2, -3), (T['big'], 0), (T['throw'] + 0.3, -2)]:
    put(boom, t, g)
WPK = 1.0
put(wh, T['s2'] + 2.4, -9, WPK)
for k in range(1, 9):
    put(wh, T['a0'] + T['astep'] * k - 0.45, -12, WPK)
    put(wh, T['b0'] + T['bstep'] * k - 0.45, -12, WPK)
put(wh, T['pb'] + 1.6, -9, WPK)
put(wh, T['wide0'] + 1.5, -8, WPK)
put(wh, T['b0'] - 0.8, -9, WPK)
put(wh, T['throw'] + 1.2, -6, WPK)
mix = bgm + nar + wet + sfx
tmp = os.path.join(R, 'audio', 'mix3_raw.wav')
pcm = (np.clip(mix * 0.7, -1, 1) * 32767).astype(np.int16)
with wave.open(tmp, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
MAF = 'equalizer=f=70:t=q:w=0.8:g=2.5,equalizer=f=250:t=q:w=1:g=-1,acompressor=threshold=-18dB:ratio=2:attack=25:release=250:makeup=2,alimiter=limit=0.89,loudnorm=I=-14:TP=-1.2:LRA=11'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', MAF, '-ar', str(SR), '-c:a', 'pcm_s16le', R + '/audio/master_mix9_' + TAG + '.wav'], check=True)
print('ok')
