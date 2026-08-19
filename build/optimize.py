# -*- coding: utf-8 -*-
"""Generate web-optimized WebP derivatives for all product and factory imagery."""
import os, sys, io, zipfile, json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'new content', 'Product picture')
OUT = os.path.join(ROOT, 'assets', 'img')
SIZES = [(1600, 80), (900, 80), (440, 76)]

SPECIALTY_SLUG = {
    'Ball hook': 'sports-ball-rack', 'Eye glass hook': 'eyeglass-hook',
    'Hat hook': 'hat-hook', 'Promotion basket': 'promotion-basket',
    'Razor hook': 'razor-hook', 'Shoe hook': 'shoe-hook',
    'Stand hook': 'display-stand', 'Tool hook': 'tool-hook',
    'Towel hook': 'towel-hook', 'Wave hook': 'wave-hook',
}

# Photographs lifted from the corporate deck, keyed by slide media index.
FACTORY = {
    'raw-wire': 12, 'raw-wire-2': 13, 'raw-wire-3': 14, 'raw-steel-coil': 15,
    'raw-steel-coil-2': 16, 'plated-parts': 17, 'stamping-press': 10,
    'stamping-operator': 18, 'stamping-hall': 19, 'brazing': 20,
    'press-line': 22, 'formed-bulk': 23, 'wireform-machine': 24,
    'wireform-hall': 25, 'wireform-cnc': 26, 'wireform-bank': 27,
    'welding-hall': 28, 'welding-line': 29, 'assembly-floor': 30,
    'packing-fixture': 31, 'assembly-bench': 32, 'assembly-room': 33,
    'warehouse': 34, 'warehouse-2': 35, 'warehouse-3': 36, 'warehouse-4': 37,
    'carton-stock': 38, 'qc-bench': 8, 'office': 9,
    'range-black': 39, 'range-black-2': 41, 'range-chrome': 42,
    'slatwall-install': 44, 'slatwall-install-2': 45, 'slatwall-detail': 46,
}


def emit(im, dest_base):
    for w, q in SIZES:
        dest = '%s-%d.webp' % (dest_base, w)
        if os.path.exists(dest):
            continue
        r = im.copy()
        if r.width > w:
            r = r.resize((w, round(r.height * w / r.width)), Image.LANCZOS)
        r.save(dest, 'WEBP', quality=q, method=5)


def numkey(f):
    digits = ''.join(ch for ch in os.path.splitext(f)[0] if ch.isdigit())
    return int(digits) if digits else 0


def products():
    manifest = {}
    for cat in sorted(os.listdir(SRC)):
        cdir = os.path.join(SRC, cat)
        if not os.path.isdir(cdir):
            continue
        for item in sorted(os.listdir(cdir)):
            idir = os.path.join(cdir, item)
            if not os.path.isdir(idir):
                continue
            slug = SPECIALTY_SLUG[item] if cat.endswith('Others') else item.lower()
            odir = os.path.join(OUT, 'products', slug)
            os.makedirs(odir, exist_ok=True)
            files = sorted([f for f in os.listdir(idir)
                            if f.lower().endswith(('.jpg', '.jpeg'))], key=numkey)
            shots = []
            for f in files:
                n = os.path.splitext(f)[0]
                with Image.open(os.path.join(idir, f)) as im:
                    emit(im.convert('RGB'), os.path.join(odir, n))
                shots.append('assets/img/products/%s/%s' % (slug, n))
            manifest[slug] = shots
            print('product', slug, len(shots))
            sys.stdout.flush()
    return manifest


def factory():
    deck = os.path.join(ROOT, 'new content', '公司介绍0613.pptm')
    fdir = os.path.join(OUT, 'factory')
    os.makedirs(fdir, exist_ok=True)
    z = zipfile.ZipFile(deck)
    names = {os.path.splitext(os.path.basename(n))[0]: n
             for n in z.namelist() if n.startswith('ppt/media/')}
    for slug, idx in FACTORY.items():
        key = 'image%d' % idx
        if key not in names:
            print('MISSING', slug, key)
            continue
        with Image.open(io.BytesIO(z.read(names[key]))) as im:
            emit(im.convert('RGB'), os.path.join(fdir, slug))
        print('factory', slug)
        sys.stdout.flush()


if __name__ == '__main__':
    manifest = products()
    factory()
    with open(os.path.join(ROOT, 'build', 'images.json'), 'w') as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)
    print('DONE', sum(len(v) for v in manifest.values()), 'product shots',
          len(manifest), 'galleries')
