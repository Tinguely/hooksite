# -*- coding: utf-8 -*-
"""Integrity check: every href/src on every generated page must resolve on disk."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('http://', 'https://', 'mailto:', 'tel:', 'data:', '#', 'javascript:')

pages, bad, checked = [], [], 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('.git', 'build', 'new content', 'siterip', 'assets')]
    for f in filenames:
        if f.endswith('.html'):
            pages.append(os.path.join(dirpath, f))

for pg in sorted(pages):
    with open(pg, encoding='utf-8') as fh:
        doc = fh.read()
    rel = os.path.relpath(pg, ROOT).replace('\\', '/')

    if '{P}' in doc:
        bad.append((rel, '{P}', 'unsubstituted path token'))
    for tok in re.findall(r'%\((\w+)\)s', doc):
        bad.append((rel, tok, 'unsubstituted format token'))

    refs = re.findall(r'(?:href|src)="([^"]+)"', doc)
    refs += [u.strip() for chunk in re.findall(r'srcset="([^"]+)"', doc)
             for u in [p.rsplit(' ', 1)[0] for p in chunk.split(',')]]
    base = os.path.dirname(pg)
    for r in refs:
        if r.startswith(SKIP) or not r:
            continue
        target = os.path.normpath(os.path.join(base, r.split('?')[0].split('#')[0]))
        if os.path.isdir(target):
            target = os.path.join(target, 'index.html')
        checked += 1
        if not os.path.exists(target):
            bad.append((rel, r, 'missing'))

# Are all optimised product shots actually referenced somewhere?
import data as D
site = D.build()
allhtml = ''
for pg in pages:
    with open(pg, encoding='utf-8') as fh:
        allhtml += fh.read()
orphan = []
for p in site['products']:
    for shot in p['images']:
        if shot + '-' not in allhtml:
            orphan.append((p['sku'], shot))

print('pages       :', len(pages))
print('refs checked:', checked)
print('broken      :', len(bad))
for b in bad[:40]:
    print('   ', b)
print('unused shots:', len(orphan))
for o in orphan[:20]:
    print('   ', o)
sys.exit(1 if bad or orphan else 0)
