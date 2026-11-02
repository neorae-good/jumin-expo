# extract paragraph text from an .hwpx (zip of XML sections) given as argv[1]; writes argv[2]
import sys, zipfile, re, html
z = zipfile.ZipFile(sys.argv[1])
names = sorted(n for n in z.namelist() if re.match(r'Contents/section\d+\.xml$', n))
out = []
for n in names:
    x = z.read(n).decode('utf-8', 'replace')
    for p in re.findall(r'<hp:p\b.*?</hp:p>', x, flags=re.S):
        t = ''.join(re.findall(r'<hp:t\b[^>]*>(.*?)</hp:t>', p, flags=re.S))
        t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
        if t: out.append(t)
imgs = [n for n in z.namelist() if n.startswith('BinData/')]
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(out) + '\n\n[BinData] ' + ', '.join(imgs))
print(len(out), 'paragraphs;', len(imgs), 'embedded files')
