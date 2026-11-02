import subprocess, sys
import numpy as np
f = sys.argv[1]
W, H = 64, 36
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
frames = []
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    frames.append(np.frombuffer(b, np.uint8).astype(np.float32))
d = [0] + [float(np.abs(frames[i] - frames[i - 1]).mean()) for i in range(1, len(frames))]
# a pop = a big change that is NOT part of a continuous move: spike vs neighbours
for i in range(2, len(d) - 2):
    nb = max(d[i - 2], d[i + 2], 1.0)
    if d[i] > 12 and d[i] > 3 * nb:
        print(f'{i/30:7.2f}s diff={d[i]:5.1f} neighbours={d[i-2]:.1f}/{d[i+2]:.1f}')
