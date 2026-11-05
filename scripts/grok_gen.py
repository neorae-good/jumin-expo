# Grok Imagine (xAI) helper for v21 clips. Needs XAI_API_KEY.
#   python scripts/grok_gen.py image o1_dawn 2          -> gen/v21/o1_dawn_1.jpg, _2.jpg   (prompt prompts/v21/o1_dawn.txt)
#   python scripts/grok_gen.py fetch o1_dawn_1        -> download a finished request again (id in gen/v21/<name>.request)
#   python scripts/grok_gen.py video o1_dawn_1 8        -> gen/v21/o1_dawn_1.mp4 (start frame gen/v21/o1_dawn_1.jpg, prompt prompts/v21/v_o1_dawn.txt)
import base64, json, os, sys, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
KEY = os.environ.get('XAI_API_KEY') or sys.exit('set XAI_API_KEY first')
OUT = ROOT / 'gen' / 'v21'; OUT.mkdir(parents=True, exist_ok=True)
H = {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}
def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers=H, method='POST' if body is not None else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=300) as r: return json.loads(r.read())
    except urllib.error.HTTPError as e: sys.exit(f'HTTP {e.code} {e.read()[:500]}')
def fetch(url, dst):
    with urllib.request.urlopen(url, timeout=300) as r: dst.write_bytes(r.read())
kind, name = sys.argv[1], sys.argv[2]
if kind == 'image':
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    prompt = (ROOT / 'prompts' / 'v21' / f'{name}.txt').read_text(encoding='utf-8').strip()
    d = call('https://api.x.ai/v1/images/generations', {'model': os.environ.get('XIMG', 'grok-imagine-image-2.0'), 'prompt': prompt, 'n': n, 'aspect_ratio': '16:9',
                                                      'resolution': '2k', 'quality': 'medium', 'response_format': 'b64_json'})
    for i, x in enumerate(d['data'], 1):
        (OUT / f'{name}_hd{i}.jpg').write_bytes(base64.b64decode(x['b64_json'])); print(OUT / f'{name}_hd{i}.jpg')
else:
    dur = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    base = name.rsplit('_', 1)[0]
    prompt = (ROOT / 'prompts' / 'v21' / f'v_{base}.txt').read_text(encoding='utf-8').strip()
    img = 'data:image/jpeg;base64,' + base64.b64encode((OUT / f'{name}.jpg').read_bytes()).decode()
    body = {'model': os.environ.get('XVID', 'grok-imagine-video-1.5'), 'prompt': prompt, 'image': {'url': img}, 'duration': dur, 'aspect_ratio': '16:9', 'resolution': '720p'}
    if kind == 'video':
        d = call('https://api.x.ai/v1/videos/generations', body)
        rid = d.get('request_id') or d.get('id'); print('request', rid, flush=True)
        (OUT / f'{name}.request').write_text(rid)
    else:  # 'fetch': re-poll a request made earlier (e.g. after the download host was allowed)
        rid = (OUT / f'{name}.request').read_text().strip()
    for _ in range(120):
        if kind == 'video': time.sleep(10)
        s = call(f'https://api.x.ai/v1/videos/{rid}')
        st = s.get('status')
        if s.get('video', {}).get('url') or st in ('done', 'completed', 'succeeded'):
            url = s.get('video', {}).get('url') or s.get('url')
            print('meta', json.dumps({k: v for k, v in s.items() if k != 'video'})[:600], flush=True); print('url', url, flush=True); fetch(url, OUT / f'{name}.mp4'); print(OUT / f'{name}.mp4'); break
        if st in ('failed', 'error', 'expired'): sys.exit(json.dumps(s)[:500])
    else: sys.exit('timeout')
