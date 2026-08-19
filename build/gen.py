# -*- coding: utf-8 -*-
"""Render the whole HCGretail site from build/data.py."""
import os, shutil, html, json
import data as D

ROOT = D.ROOT
SITE = D.build()
CO = SITE['company']
YEAR = 2026

ARW = ('<svg class="arw" width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
       '<path d="M1 7h11M8 3l4 4-4 4" stroke="currentColor" stroke-width="1.6" '
       'stroke-linecap="round" stroke-linejoin="round"/></svg>')
CHEV = ('<svg class="chev" width="11" height="11" viewBox="0 0 12 12" fill="none" aria-hidden="true">'
        '<path d="M2.5 4.5 6 8l3.5-3.5" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>')
X = ('<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
     '<path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" '
     'stroke-linecap="round"/></svg>')


def arrow(dir_='right'):
    d = 'M1 7h11M8 3l4 4-4 4' if dir_ == 'right' else 'M13 7H2M6 3 2 7l4 4'
    return ('<svg width="15" height="15" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
            '<path d="%s" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            'stroke-linejoin="round"/></svg>' % d)


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(str(s), quote=True)


def strip_tags(s):
    out, depth = [], 0
    for ch in str(s):
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return ''.join(out).replace(' ', ' ').replace('&nbsp;', ' ')


def img(base, alt, sizes='100vw', cls='', eager=False, ratio=None, extra=''):
    """base is a repo-relative stem such as 'assets/img/products/cb-sx-01/1'."""
    if not base:
        return ''
    src = '%s{P}-900.webp' % base
    srcset = ', '.join('%s{P}-%d.webp %dw' % (base, w, w) for w in (440, 900, 1600))
    return ('<img src="{P}%s-900.webp" srcset="%s" sizes="%s" alt="%s"%s%s loading="%s" '
            'decoding="async"%s>' % (
                base,
                ', '.join('{P}%s-%d.webp %dw' % (base, w, w) for w in (440, 900, 1600)),
                sizes, esc(alt),
                ' class="%s"' % cls if cls else '',
                ' width="%d" height="%d"' % ratio if ratio else '',
                'eager' if eager else 'lazy',
                (' ' + extra) if extra else ''))


def rel(prefix, url):
    return prefix + url


# ------------------------------------------------------------------- shell
def nav_links(prefix, current):
    def item(url, label):
        cls = 'nav-link is-current' if current == label.lower() else 'nav-link'
        return '<a class="%s" href="%s%s">%s</a>' % (cls, prefix, url, label)

    systems = ''.join(
        '<a class="mega-link" href="%sproducts/%s/"><span>%s<small>%s</small></span>%s</a>'
        % (prefix, s['slug'], s['name'], s['clip'].split(',')[0], ARW) for s in SITE['systems'])
    systems += ('<a class="mega-link" href="%sproducts/specialty/"><span>Specialty Fixtures'
                '<small>Ten purpose-built display items</small></span>%s</a>' % (prefix, ARW))
    styles = ''.join(
        '<a class="mega-link" href="%sstyles/%s/"><span>%s<small>%s</small></span>%s</a>'
        % (prefix, s['slug'], s['name'], s['code'], ARW) for s in SITE['styles'])

    mega = """
      <div class="mega" role="region" aria-label="Products">
        <div class="mega-grid">
          <div class="mega-col">
            <h4>By mounting system</h4>
            %s
          </div>
          <div class="mega-col">
            <h4>By hook style</h4>
            %s
          </div>
          <div class="mega-feature">
            %s
            <div class="mf-body">
              <strong>The full matrix</strong>
              <p>Seven hook styles across five mounting systems, plus ten specialty fixtures. Filter it
                 down to the one you need.</p>
              <a class="tlink" href="%sproducts/">Open the finder %s</a>
            </div>
          </div>
        </div>
      </div>""" % (systems, styles,
                   img('assets/img/factory/range-chrome', 'Chrome display hook range', '320px'),
                   prefix, ARW)

    return """
      <nav class="nav" aria-label="Primary">
        <div class="nav-item has-mega">
          <a class="nav-link%s" href="%sproducts/">Products %s</a>
          %s
        </div>
        %s %s %s %s
      </nav>""" % (
        ' is-current' if current == 'products' else '', prefix, CHEV, mega,
        item('capabilities/', 'Capabilities'), item('custom/', 'Custom &amp; OEM'),
        item('about/', 'About'), item('contact/', 'Contact'))


def drawer(prefix):
    systems = ''.join('<a href="%sproducts/%s/">%s</a>' % (prefix, s['slug'], s['name'])
                      for s in SITE['systems'])
    systems += '<a href="%sproducts/specialty/">Specialty Fixtures</a>' % prefix
    styles = ''.join('<a href="%sstyles/%s/">%s</a>' % (prefix, s['slug'], s['name'])
                     for s in SITE['styles'])
    return """
    <div class="drawer" id="drawer">
      <div class="dsec is-open">
        <button type="button" aria-expanded="true">Products %s</button>
        <div class="dsec-body"><div>
          <p class="grp">By mounting system</p>%s
          <p class="grp">By hook style</p>%s
          <p class="grp">Everything</p><a href="%sproducts/">Product finder</a>
        </div></div>
      </div>
      <div class="dsec"><button type="button" aria-expanded="false">More %s</button>
        <div class="dsec-body"><div>
          <a href="%scapabilities/">Capabilities</a>
          <a href="%scustom/">Custom &amp; OEM</a>
          <a href="%sabout/">About HCGretail</a>
          <a href="%scontact/">Contact</a>
        </div></div>
      </div>
      <div class="drawer-foot">
        <a class="btn btn-accent" href="%scontact/">Request a quote %s</a>
        <a class="btn btn-ghost" href="mailto:%s">%s</a>
      </div>
    </div>""" % (CHEV, systems, styles, prefix, CHEV, prefix, prefix, prefix, prefix,
                 prefix, ARW, CO['email'], CO['email'])


def header(prefix, current):
    return """
  <div class="progress" aria-hidden="true"></div>
  <header class="hdr">
    <div class="hdr-in">
      <a class="brand" href="%sindex.html" aria-label="%s home">
        <span class="brand-mark">HCG<span class="hl">retail</span></span>
        <span class="brand-sub">Display Hooks</span>
      </a>
      %s
      <a class="btn btn-sm hdr-cta" href="%scontact/">Request a quote %s</a>
      <button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="drawer">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
  %s""" % (prefix, CO['brand'], nav_links(prefix, current), prefix, ARW, drawer(prefix))


def footer(prefix):
    sys_links = ''.join('<li><a href="%sproducts/%s/">%s</a></li>' % (prefix, s['slug'], s['name'])
                        for s in SITE['systems'])
    sty_links = ''.join('<li><a href="%sstyles/%s/">%s</a></li>' % (prefix, s['slug'], s['short'])
                        for s in SITE['styles'])
    return """
  <footer class="ftr">
    <div class="wrap">
      <div class="ftr-grid">
        <div>
          <span class="brand-mark">HCG<span class="hl">retail</span></span>
          <p class="ftr-about" style="margin-top:1rem">The North American office of %s — eighteen years
             building supermarket shelf display hooks and metal stamping parts in Zhejiang, China.</p>
          <p class="ftr-about"><a class="tlink" href="%scontact/">Talk to us about a project %s</a></p>
        </div>
        <div><h5>Mounting systems</h5><ul>%s<li><a href="%sproducts/specialty/">Specialty fixtures</a></li></ul></div>
        <div><h5>Hook styles</h5><ul>%s</ul></div>
        <div><h5>Company</h5><ul>
          <li><a href="%scapabilities/">Capabilities</a></li>
          <li><a href="%scustom/">Custom &amp; OEM</a></li>
          <li><a href="%sabout/">About</a></li>
          <li><a href="%sproducts/">Product finder</a></li>
          <li><a href="mailto:%s">%s</a></li>
        </ul></div>
      </div>
      <div class="ftr-bot">
        <span>&copy; %d %s. All rights reserved.</span>
        <span>%s</span>
      </div>
    </div>
  </footer>""" % (CO['parent'], prefix, ARW, sys_links, prefix, sty_links,
                  prefix, prefix, prefix, prefix, CO['email'], CO['email'],
                  YEAR, CO['brand'], CO['address'])


def page(path, title, desc, body, current='', depth=None):
    if depth is None:
        depth = 0 if path == 'index.html' else path.count('/')
    prefix = '../' * depth
    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}assets/css/site.css">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' fill='%%23121214'/%%3E%%3Cpath d='M10 8v9a6 6 0 0 0 12 0' stroke='%%23d33f22' stroke-width='3.2' fill='none' stroke-linecap='round'/%%3E%%3C/svg%%3E">
</head>
<body>
%s
<main id="main">
%s
</main>
%s
<script src="{P}assets/js/site.js" defer></script>
</body>
</html>
""" % (esc(title), esc(desc), esc(title), esc(desc), header(prefix, current), body, footer(prefix))

    doc = doc.replace('{P}', prefix)
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as fh:
        fh.write(doc)
    return path


# --------------------------------------------------------------- components
def crumbs(items):
    out = []
    for i, (label, url) in enumerate(items):
        if i:
            out.append('<span class="sep">/</span>')
        out.append('<a href="{P}%s">%s</a>' % (url, label) if url else '<span>%s</span>' % label)
    return '<nav class="crumbs" aria-label="Breadcrumb">%s</nav>' % ''.join(out)


def product_card(p, sizes='(min-width:900px) 22vw, 46vw', reveal=True):
    if p['images']:
        shots = ''.join([
            img(p['images'][0], p['name'] + ' display hook', sizes, eager=False),
            img(p['images'][1], p['name'] + ' alternate view', sizes, cls='alt') if len(p['images']) > 1 else '',
        ])
        badge = ('<span class="card-shots">%d photos</span>' % len(p['images'])
                 if len(p['images']) > 1 else '')
    else:
        shots = ('<span class="noimg"><span class="mono">Made to order</span>'
                 '<span style="font-size:.8rem">Photography on request</span></span>')
        badge = ''
    desc = strip_tags(p.get('card_desc') or p.get('lede', ''))
    style = SITE['style_by'].get(p['style'])
    return """
      <article class="card%s"%s data-system="%s" data-style="%s" data-tag="%s">
        <div class="card-media">%s%s</div>
        <div class="card-body">
          <span class="card-sku">%s</span>
          <h3 class="card-name"><a class="stretch" href="{P}%s">%s</a></h3>
          <p class="card-desc">%s</p>
          <span class="card-foot">View specification %s</span>
        </div>
      </article>""" % (
        '', ' data-reveal' if reveal else '',
        p['system'], p['style'] or '', 'photo' if p['images'] else 'spec',
        shots, badge, esc(p['sku']), p['url'], esc(p['name']),
        esc(desc if len(desc) < 108 else desc[:105].rsplit(' ', 1)[0] + '…'),
        ARW)


def system_tile(s, i):
    hero = s['hero'] if s.get('hero') else (s['products'][0]['images'][0] if s['products'] and s['products'][0]['images'] else '')
    shots = sum(len(p['images']) for p in s['products'])
    return """
      <a class="tile" href="{P}products/%s/" data-reveal>
        <div class="tile-media"><span class="tile-idx">%02d</span>%s</div>
        <div class="tile-body">
          <h3 class="h-3">%s</h3>
          <p class="card-desc" style="font-size:.9rem">%s</p>
          <div class="tile-meta">
            <span class="chip chip-solid">%d hook styles</span>
            <span class="chip chip-solid">%s</span>
          </div>
          <span class="card-foot">Explore the system %s</span>
        </div>
      </a>""" % (s['slug'], i, img(hero, s['name'], '(min-width:900px) 33vw, 92vw'),
                 s['name'], strip_tags(s['lede']), len(s['products']), s['surface'], ARW)


def spec_table(specs, columns=True):
    if not specs:
        return '<p class="muted">Specification available on request.</p>'
    rows = []
    for s in specs:
        if s['menu']:
            vals = ''.join('<span class="chip">%s</span>' % esc(o) for o in s['options'])
            unit = '<span class="spec-unit">%s</span>' % esc(s['unit']) if s['unit'] else ''
            value = '<div class="spec-v">%s%s</div>' % (vals, unit)
        else:
            v = esc(s['options'][0] if s['options'] else '—')
            u = ' ' + esc(s['unit']) if s['unit'] else ''
            value = '<div class="spec-single">%s%s</div>' % (v, u)
        note = '<small>%s</small>' % esc(s['note']) if s['note'] else ''
        rows.append('<div class="spec"><div class="spec-l">%s%s</div>%s</div>'
                    % (esc(s['label']), note, value))
    return '<div class="specs">%s</div>' % ''.join(rows)


def cta_band(title='Send us the wall, we will send you the hook.',
             copy='Tell us the panel, the product and the volume. You get a specification, a finish '
                  'recommendation and a price — usually inside one working day.',
             primary=('contact/', 'Request a quote'), secondary=('products/', 'Browse the range')):
    return """
  <section class="section">
    <div class="wrap">
      <div class="cta-band" data-reveal>
        <div class="inner">
          <p class="eyebrow on-dark">Next step</p>
          <h2 class="h-1">%s</h2>
          <p class="lede" style="margin-top:1.2rem">%s</p>
          <div class="cta-actions">
            <a class="btn btn-light" href="{P}%s">%s %s</a>
            <a class="btn btn-onDark" href="{P}%s">%s %s</a>
          </div>
        </div>
      </div>
    </div>
  </section>""" % (title, copy, primary[0], primary[1], ARW, secondary[0], secondary[1], ARW)


def marquee():
    words = (['Slatwall', 'Pegboard', 'Tube snap', 'Wire grid', 'Chrome', 'Nickel', 'Zinc',
              'Powder coated', 'OEM &amp; ODM', 'Private label', '18 years', '20+ countries'])
    run = ''.join('<span>%s</span>' % w for w in words)
    return ('<div class="marq" aria-hidden="true"><div class="marq-track">%s%s</div></div>'
            % (run, run))


def stats_block(dark=False):
    cells = []
    for s in SITE['stats']:
        cells.append("""
        <div class="stat" data-reveal>
          <div class="stat-n"><span data-count="%d">%s</span><span class="suffix">%s</span></div>
          <div class="stat-l">%s</div>
          <div class="stat-s">%s</div>
        </div>""" % (s['value'], '{:,}'.format(s['value']), s['suffix'], s['label'], s['sub']))
    return '<div class="stats" data-stagger>%s</div>' % ''.join(cells)


def finish_block():
    cards = ''.join("""
      <div class="finish" data-reveal>
        <div class="finish-sw" style="background-color:%s"></div>
        <h4 class="h-4">%s</h4>
        <p>%s</p>
      </div>""" % (f['tone'], f['name'], f['blurb']) for f in SITE['finishes'])
    return '<div class="finishes" data-stagger>%s</div>' % cards


def matrix_table():
    head = ''.join('<th scope="col"><a href="{P}products/%s/">%s</a></th>' % (s['slug'], s['short'])
                   for s in SITE['systems'])
    rows = []
    for st in SITE['styles']:
        cells = []
        for sy in SITE['systems']:
            p = SITE['by_slug']['%s-%s' % (sy['code'].lower(), st['code'].lower())]
            cells.append('<td><a href="{P}%s"><span class="dot"></span>%s</a></td>'
                         % (p['url'], esc(p['sku'])))
        rows.append('<tr><th scope="row"><a href="{P}styles/%s/">%s</a></th>%s</tr>'
                    % (st['slug'], st['name'], ''.join(cells)))
    return """
    <div class="matrix-scroll" data-reveal>
      <table class="matrix">
        <caption class="sr">Hook style by mounting system, with part codes</caption>
        <thead><tr><th scope="col">Style \\ System</th>%s</tr></thead>
        <tbody>%s</tbody>
      </table>
    </div>""" % (head, ''.join(rows))


def rail_section(title, eyebrow, cards, link=None, bone=False, lede=''):
    more = ('<a class="btn btn-ghost btn-sm" href="{P}%s">%s %s</a>' % (link[0], link[1], ARW)
            if link else '')
    return """
  <section class="section%s">
    <div class="wrap">
      <div class="rail-head" data-reveal>
        <div style="max-width:38rem">
          <p class="eyebrow">%s</p>
          <h2 class="h-2">%s</h2>
          %s
        </div>
        <div class="rail-nav">
          %s
          <button class="rail-btn" type="button" data-rail-prev aria-label="Scroll left">%s</button>
          <button class="rail-btn" type="button" data-rail-next aria-label="Scroll right">%s</button>
        </div>
      </div>
    </div>
    <div class="railhold">
      <div class="rail" data-rail data-stagger>%s</div>
    </div>
  </section>""" % (' section-bone' if bone else '', eyebrow, title,
                   '<p class="lede" style="margin-top:1rem">%s</p>' % lede if lede else '',
                   more, arrow('left'), arrow('right'), cards)


def lightbox():
    return """
  <div class="lb" role="dialog" aria-modal="true" aria-label="Product image">
    <button class="lb-close" type="button" aria-label="Close">%s</button>
    <button class="lb-prev" type="button" aria-label="Previous image">%s</button>
    <button class="lb-next" type="button" aria-label="Next image">%s</button>
    <img src="" alt="">
    <span class="lb-count"></span>
  </div>""" % (X, arrow('left'), arrow('right'))


# ------------------------------------------------------------------- pages
def home():
    tiles = ''.join(system_tile(s, i + 1) for i, s in enumerate(SITE['systems']))
    tiles += """
      <a class="tile" href="{P}products/specialty/" data-reveal>
        <div class="tile-media"><span class="tile-idx">06</span>%s</div>
        <div class="tile-body">
          <h3 class="h-3">Specialty Fixtures</h3>
          <p class="card-desc" style="font-size:.9rem">Ten purpose-built pieces for categories a
             straight peg cannot merchandise — footwear, headwear, optical, textiles, sports balls,
             power tools and bulk promotion.</p>
          <div class="tile-meta"><span class="chip chip-solid">10 fixtures</span>
            <span class="chip chip-solid">Wall, rail and floor</span></div>
          <span class="card-foot">See the fixtures %s</span>
        </div>
      </a>""" % (img('assets/img/products/promotion-basket/1', 'Promotion basket',
                     '(min-width:900px) 33vw, 92vw'), ARW)

    style_cards = ''.join("""
      <a class="tile" href="{P}styles/%s/" data-reveal>
        <div class="tile-media">%s</div>
        <div class="tile-body">
          <span class="card-sku">%s</span>
          <h3 class="h-4">%s</h3>
          <p class="card-desc">%s</p>
          <span class="card-foot">All five systems %s</span>
        </div>
      </a>""" % (st['slug'],
                 img(next((p['images'][0] for p in st['products'] if p['images']), ''),
                     st['name'], '(min-width:1100px) 19rem, 60vw'),
                 st['code'], st['name'], strip_tags(st['lede']), ARW)
        for st in SITE['styles'])

    spec_cards = ''.join(product_card(p, '(min-width:1100px) 19rem, 60vw')
                         for p in SITE['products'] if p['kind'] == 'specialty')

    steps = ''.join("""
        <article class="step" data-reveal>
          <div class="step-media">%s</div>
          <div class="step-body">
            <span class="step-n">%s</span>
            <h4 class="h-4">%s</h4>
            <p>%s</p>
          </div>
        </article>""" % (img(p['img'], p['name'], '(min-width:1120px) 25vw, 50vw'),
                         p['step'], p['name'], p['copy'])
        for p in SITE['process'][:4])

    body = """
  <section class="hero">
    <div class="wrap">
      <div class="hero-type" data-reveal="fade">
        <p class="eyebrow">Retail display hooks &middot; Since 2008</p>
        <h1 data-words>Hooks that hold <em>the plan.</em></h1>
      </div>
      <div class="hero-sub" data-reveal>
        <p class="lede">Forty-five stock configurations across slatwall, pegboard, tube and wire grid —
           engineered, stamped, formed and finished in our own 6,000&nbsp;m&sup2; factory, and shipped to
           more than twenty countries.</p>
        <div style="display:flex;gap:.7rem;flex-wrap:wrap">
          <a class="btn" href="{P}products/">Find your hook %s</a>
          <a class="btn btn-ghost" href="{P}contact/">Request a quote</a>
        </div>
      </div>
      <div class="hero-stage" data-clip data-reveal="fade">
        %s
        <div class="hero-badge">
          <strong>Every length, every gauge</strong>
          <span>50–400&nbsp;mm arms in Ø3–8&nbsp;mm wire, four finishes</span>
        </div>
      </div>
    </div>
  </section>

  %s

  <section class="section">
    <div class="wrap">
      <div class="feat">
        <div data-reveal>
          <p class="eyebrow">What we actually do</p>
          <h2 class="h-1">A hook is the cheapest part of the fixture and the first one to fail.</h2>
        </div>
        <div data-reveal="right">
          <p class="lede">When an arm sags, a clip walks out of the groove or a ticket holder snaps, the
             cost is never the hook. It is the re-merchandising labour, the lost facing and the shrink.</p>
          <p>We have spent eighteen years on that single problem. Clip geometry stamped in-house, arms
             formed on CNC wire machines, every joint welded on dedicated equipment, and four finishes
             specified against the environment the hook has to survive — not against what happens to be
             running that week.</p>
          <p><a class="tlink" href="{P}capabilities/">See how they are made %s</a></p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">%s</section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="rail-head" data-reveal>
        <div style="max-width:40rem">
          <p class="eyebrow">Step one</p>
          <h2 class="h-2">Start with the wall you already have.</h2>
          <p class="lede" style="margin-top:1rem">Every hook in the range exists in five mounting backs.
             Pick the one that matches your panel and the rest of the catalogue narrows itself down.</p>
        </div>
      </div>
      <div class="cardgrid cols-sys" data-stagger style="margin-top:2rem">%s</div>
    </div>
  </section>

  %s

  <section class="section">
    <div class="wrap">
      <div class="rail-head" data-reveal>
        <div style="max-width:40rem">
          <p class="eyebrow">The whole range at once</p>
          <h2 class="h-2">Seven styles &times; five systems.</h2>
          <p class="lede" style="margin-top:1rem">Every cell is a stock part code with its own
             specification page. Specialty fixtures sit alongside it.</p>
        </div>
        <a class="btn btn-ghost btn-sm" href="{P}products/">Open the finder %s</a>
      </div>
      %s
    </div>
  </section>

  %s

  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Surface finish</p>
        <h2 class="h-2">Four finishes, specified against the environment.</h2>
        <p class="lede" style="margin-top:1rem">Every part in the catalogue is available in all four.
           Powder coat matches any RAL or Pantone for brand-built fixtures.</p>
      </div>
      <div style="margin-top:2.4rem">%s</div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="feat rev">
        <div class="feat-media" data-reveal="scale">%s</div>
        <div data-reveal="left">
          <p class="eyebrow">Manufacturing</p>
          <h2 class="h-1">Ninety machines. One roof.</h2>
          <p class="lede">Stamping, wire forming, welding, finishing, assembly and packing all happen in
             the same building in Zhejiang. Nothing is subcontracted, so nothing waits in someone
             else&rsquo;s queue.</p>
          <ul class="feat-list">
            <li>30+ stamping machines blanking clips, ticket plates and sole plates from coil</li>
            <li>30+ CNC wire formers running arm geometry to repeatable bend radii</li>
            <li>30+ dedicated welders on the arm-to-clip joint — the one that actually fails</li>
            <li>1,500–2,000&nbsp;m&sup2; of raw material and finished-goods warehousing</li>
          </ul>
          <p style="margin-top:1.5rem"><a class="btn btn-ghost" href="{P}capabilities/">Inside the factory %s</a></p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap"><p class="eyebrow" data-reveal>From coil to carton</p></div>
    <div class="steps" data-stagger>%s</div>
    <div class="wrap" style="margin-top:2rem"><a class="tlink" href="{P}capabilities/">All seven stages %s</a></div>
  </section>

  <section class="section section-dark">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow on-dark">Custom &amp; OEM</p>
          <h2 class="h-1">If it is not in the catalogue, it is a drawing away.</h2>
          <p class="lede">Roughly half of what leaves the factory is made to a customer&rsquo;s
             specification rather than ours — different lengths, different load cases, brand colours,
             private-label packaging.</p>
          <ul class="feat-list">%s</ul>
          <p style="margin-top:1.6rem"><a class="btn btn-light" href="{P}custom/">How custom works %s</a></p>
        </div>
        <div class="feat-media" data-reveal="scale">%s</div>
      </div>
    </div>
  </section>

  %s
""" % (ARW,
       img('assets/img/factory/range-black-2', 'Chrome display hooks in graduated lengths',
           '100vw', eager=True),
       marquee(), ARW, stats_block(), tiles,
       rail_section('Then pick the geometry.', 'Step two', style_cards,
                    lede='The arm decides how the product hangs, how it tickets and how much abuse it '
                         'takes. Seven configurations, each available on every mounting system.'),
       ARW, matrix_table(),
       rail_section('Some categories need more than a peg.', 'Specialty fixtures', spec_cards,
                    link=('products/specialty/', 'All ten fixtures'), bone=True,
                    lede='Footwear, headwear, optical, textiles, sports balls, power tools and bulk '
                         'promotion — purpose-built pieces in the same steel and the same finishes.'),
       finish_block(),
       img('assets/img/factory/wireform-bank', 'Wire forming machines on the factory floor',
           '(min-width:900px) 46vw, 92vw'),
       ARW, steps, ARW,
       ''.join('<li>%s — %s</li>' % (c['title'], c['copy'].rstrip('.').lower()) for c in SITE['custom']),
       ARW,
       img('assets/img/factory/range-black', 'Custom hook lengths laid out by size',
           '(min-width:900px) 46vw, 92vw'),
       cta_band())

    return page('index.html', 'HCGretail — Retail Display Hooks for Slatwall, Pegboard, Tube & Wire Grid',
                'Forty-five stock display hook configurations across slatwall, pegboard, tube and wire '
                'grid systems. Manufactured in our own 6,000 m² factory since 2008. OEM, ODM and private '
                'label welcome.', body, 'home')


def products_index():
    cards = ''.join(product_card(p, '(min-width:900px) 22vw, 46vw')
                    for p in SITE['products'])
    sys_btns = ''.join('<button class="fbtn" type="button" data-filter="system" data-value="%s" '
                       'aria-pressed="false">%s</button>' % (s['slug'], s['short'])
                       for s in SITE['systems'])
    sys_btns += ('<button class="fbtn" type="button" data-filter="system" data-value="specialty" '
                 'aria-pressed="false">Specialty</button>')
    sty_btns = ''.join('<button class="fbtn" type="button" data-filter="style" data-value="%s" '
                       'aria-pressed="false">%s</button>' % (s['slug'], s['short'])
                       for s in SITE['styles'])

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">The complete catalogue</p>
          <h1 class="h-1" data-words>Forty-five ways to hang a product.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">Filter by the panel you are mounting to, or by the hook geometry the product
             needs. Every result opens onto a full specification — dimensions, wire gauges, tag sizes,
             finishes and carton counts.</p>
        </div>
      </div>
    </div>
  </section>

  <div class="filterbar">
    <div class="wrap">
      <div class="filter-rows">
        <div class="filter-row">
          <span class="fgroup-label">System</span>%s
        </div>
        <div class="filter-row">
          <span class="fgroup-label">Style</span>%s
          <button class="fbtn" type="button" data-filter-clear
            style="border-style:dashed">Clear all</button>
        </div>
      </div>
    </div>
  </div>

  <section class="section-tight">
    <div class="wrap">
      <p class="result-line"><strong data-finder-count>45</strong> of 45 products</p>
    </div>
  </section>

  <section style="padding-bottom:clamp(3rem,7vw,6rem)">
    <div class="wrap">
      <div class="cardgrid cols-4" data-finder data-stagger>%s</div>
      <p class="empty" data-finder-empty hidden>No product matches that combination.
        Specialty fixtures have no hook style — clear the style filter to see them.</p>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Cross reference</p>
        <h2 class="h-2">The part code matrix.</h2>
        <p class="lede" style="margin-top:1rem">Read across for a system, down for a style. Every code
           is a live specification page.</p>
      </div>
      <div style="margin-top:2rem">%s</div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Products', None)]), sys_btns, sty_btns, cards,
       matrix_table(), cta_band())

    return page('products/index.html', 'Product Finder — All 45 Display Hooks | HCGretail',
                'Filter the complete HCGretail catalogue by mounting system and hook style. Slatwall, '
                'pegboard, tube snap and wire grid hooks plus ten specialty retail fixtures.',
                body, 'products')


def system_page(sy):
    cards = ''.join(product_card(p, '(min-width:900px) 30vw, 46vw') for p in sy['products'])
    uses = ''.join('<li>%s</li>' % u for u in sy['uses'])
    other = ''.join("""
      <a class="mega-link" href="{P}products/%s/" style="border:1px solid var(--line);
         border-radius:var(--r-sm);margin:0 0 .5rem;padding:.7rem .9rem">
        <span>%s<small>%s</small></span>%s</a>""" % (o['slug'], o['name'], o['surface'], ARW)
        for o in SITE['systems'] if o['slug'] != sy['slug'])

    shots = [p['images'][0] for p in sy['products'] if p['images']]
    mosaic = ''
    if len(shots) >= 4:
        cells = []
        for i, s in enumerate(shots[:4]):
            cls = ''
            prod = next(p for p in sy['products'] if p['images'] and p['images'][0] == s)
            cells.append('<figure%s>%s<figcaption>%s</figcaption></figure>'
                         % (cls, img(s, prod['name'], '(min-width:780px) 25vw, 50vw'), prod['sku']))
        mosaic = """
  <section class="section-tight">
    <div class="wrap wrap-wide"><div class="mosaic" data-reveal="fade">%s</div></div>
  </section>""" % ''.join(cells)

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Mounting system &middot; %s</p>
          <h1 class="h-1" data-words>%s</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">%s</p>
          <div class="tile-meta" style="margin-top:1.2rem">
            <span class="chip chip-accent">%d stock styles</span>
            <span class="chip">%s</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap">
      <div class="feat">
        <div class="feat-media" data-clip>%s</div>
        <div data-reveal="right">
          <h2 class="h-3">%s</h2>
          <p style="margin-top:1rem">%s</p>
          <dl class="kv">
            <div><dt>Fits</dt><dd>%s</dd></div>
            <div><dt>Mounting back</dt><dd>%s</dd></div>
            <div><dt>Part prefix</dt><dd><code>%s-</code></dd></div>
            <div><dt>Finishes</dt><dd>Chrome, nickel, zinc, powder coat</dd></div>
          </dl>
          <p class="eyebrow" style="margin-bottom:.8rem">Typical applications</p>
          <ul class="feat-list" style="margin-top:0">%s</ul>
        </div>
      </div>
    </div>
  </section>

  %s

  <section class="section">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">The %s range</p>
        <h2 class="h-2">Every hook style, on this back.</h2>
        <p class="lede" style="margin-top:1rem">The clip stays the same. The arm changes with what you
           are hanging and how it has to ticket.</p>
      </div>
      <div class="cardgrid cols-3" data-stagger style="margin-top:2.2rem">%s</div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow">Wrong panel?</p>
          <h2 class="h-2">The same seven styles exist on every other back.</h2>
          <p class="lede" style="margin-top:1rem">Mixed estates are normal. We supply the identical arm
             geometry across all five mounting systems so one planogram reads the same in every store
             format.</p>
        </div>
        <div data-reveal="right">%s</div>
      </div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Products', 'products/'), (sy['name'], None)]),
       sy['short'], sy['name'], strip_tags(sy['lede']), len(sy['products']), sy['surface'],
       img(sy['hero'], sy['name'], '(min-width:900px) 46vw, 92vw', eager=True),
       sy['pitch'], sy['blurb'], sy['fits'], sy['clip'], sy['code'], uses,
       mosaic, sy['short'], cards, other,
       cta_band(title='Specifying a %s wall?' % sy['short'].split(' ')[0].lower(),
                copy='Send the panel detail and what it has to carry. We will come back with the part '
                     'code, the finish and a price per thousand.'))

    return page('products/%s/index.html' % sy['slug'],
                '%s — %d Stock Styles | HCGretail' % (sy['name'], len(sy['products'])),
                strip_tags(sy['lede']) + ' ' + strip_tags(sy['blurb'])[:110],
                body, 'products')


def style_page(st):
    cards = ''.join(product_card(p, '(min-width:900px) 30vw, 46vw') for p in st['products'])
    traits = ''.join('<li>%s</li>' % t for t in st['traits'])
    hero = next((p['images'][0] for p in st['products'] if p['images']), '')

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Hook style &middot; %s</p>
          <h1 class="h-1" data-words>%s</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">%s</p>
          <div class="tile-meta" style="margin-top:1.2rem">
            <span class="chip chip-accent">On all 5 systems</span>
            <span class="chip">%s</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap">
      <div class="feat">
        <div class="feat-media" data-clip>%s</div>
        <div data-reveal="right">
          <h2 class="h-3">%s</h2>
          <p style="margin-top:1rem">%s</p>
          <dl class="kv">
            <div><dt>Best for</dt><dd>%s</dd></div>
            <div><dt>Ticketing</dt><dd>%s</dd></div>
            <div><dt>Part suffix</dt><dd><code>-%s</code></dd></div>
          </dl>
          <ul class="feat-list" style="margin-top:1.4rem">%s</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Pick your panel</p>
        <h2 class="h-2">%s, on all five mounting backs.</h2>
        <p class="lede" style="margin-top:1rem">Identical arm geometry, five different clips. Specify by
           the wall you have.</p>
      </div>
      <div class="cardgrid cols-3" data-stagger style="margin-top:2.2rem">%s</div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Compare</p>
        <h2 class="h-2">Other geometries in the range.</h2>
      </div>
      <div class="cardgrid cols-sys" data-stagger style="margin-top:2rem">%s</div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Products', 'products/'), (st['name'], None)]),
       st['code'], st['name'], strip_tags(st['lede']),
       '%d wire%s' % (st['arms'], 's' if st['arms'] > 1 else ''),
       img(hero, st['name'], '(min-width:900px) 46vw, 92vw', eager=True),
       st['lede'], st['blurb'], st['best'], st['tag'] or 'No ticket holder', st['code'], traits,
       st['name'], cards,
       ''.join("""
      <a class="tile" href="{P}styles/%s/" data-reveal>
        <div class="tile-media">%s</div>
        <div class="tile-body">
          <span class="card-sku">%s</span>
          <h3 class="h-4">%s</h3>
          <p class="card-desc">%s</p>
          <span class="card-foot">Compare %s</span>
        </div>
      </a>""" % (o['slug'],
                 img(next((p['images'][0] for p in o['products'] if p['images']), ''),
                     o['name'], '(min-width:900px) 30vw, 46vw'),
                 o['code'], o['name'], strip_tags(o['lede']), ARW)
         for o in SITE['styles'] if o['slug'] != st['slug']),
       cta_band(title='Need it in a length we do not stock?',
                copy='Arm lengths, wire gauges and tag sizes are all tooling we already own. Tell us the '
                     'dimension and we will quote it as a standard part.',
                secondary=('custom/', 'Custom &amp; OEM')))

    return page('styles/%s/index.html' % st['slug'],
                '%s Display Hooks (%s) | HCGretail' % (st['name'], st['code']),
                strip_tags(st['lede']) + ' Available on slatwall, pegboard, tube and wire grid.',
                body, 'products')


def specialty_index():
    cards = ''.join(product_card(p, '(min-width:900px) 30vw, 46vw')
                    for p in SITE['products'] if p['kind'] == 'specialty')
    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Beyond the peg</p>
          <h1 class="h-1" data-words>Specialty fixtures.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">Ten purpose-built pieces for the categories a straight arm cannot merchandise
             properly — footwear that has to face out, caps that must not crease, frames that need fine
             wire, balls that need a cradle, and bulk promotion that needs to roll.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap">
      <div class="cardgrid cols-3" data-stagger>%s</div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow">Also available</p>
          <h2 class="h-2">Anything else you can draw.</h2>
          <p class="lede" style="margin-top:1rem">These ten are the pieces customers ask for often enough
             that we hold tooling. Everything else is a custom part — and custom parts are most of what
             the factory actually runs.</p>
          <p style="margin-top:1.4rem"><a class="btn" href="{P}custom/">How custom works %s</a></p>
        </div>
        <div class="feat-media" data-reveal="scale">%s</div>
      </div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Products', 'products/'), ('Specialty Fixtures', None)]),
       cards, ARW,
       img('assets/img/factory/formed-bulk', 'Formed hook components in bulk',
           '(min-width:900px) 46vw, 92vw'),
       cta_band())

    return page('products/specialty/index.html',
                'Specialty Retail Fixtures — Shoe, Hat, Optical, Ball & Tool Hooks | HCGretail',
                'Ten purpose-built retail display fixtures: footwear hooks, hat hooks, eyeglass hooks, '
                'towel hooks, sports ball racks, power tool hooks, razor hooks, wave hooks, promotion '
                'baskets and floor display stands.', body, 'products')


def product_page(p):
    sy = SITE['system_by'].get(p['system'])
    st = SITE['style_by'].get(p['style'])

    if p['images']:
        slides = ''.join(img(s, '%s — view %d' % (p['name'], i + 1), '(min-width:980px) 52vw, 96vw',
                             cls='is-active' if i == 0 else '', eager=(i == 0),
                             extra='data-full="{P}%s-1600.webp"' % s)
                         for i, s in enumerate(p['images']))
        thumbs = ''.join(
            '<button class="gal-thumb%s" type="button" role="tab" aria-selected="%s" '
            'aria-label="View %d">%s</button>'
            % (' is-active' if i == 0 else '', 'true' if i == 0 else 'false', i + 1,
               img(s, '', '80px'))
            for i, s in enumerate(p['images'])) if len(p['images']) > 1 else ''
        gallery = """
      <div class="gal">
        <div class="gal-main" role="button" tabindex="0" aria-label="Enlarge image">
          %s
          <span class="gal-zoom">Click to enlarge</span>
        </div>
        <div class="gal-thumbs" role="tablist" aria-label="Product images">%s</div>
      </div>""" % (slides, thumbs)
        lb = lightbox()
    else:
        sibling = next((q for q in SITE['products']
                        if q['style'] == p['style'] and q['images']), None)
        gallery = """
      <div class="gal">
        <div class="gal-main" style="cursor:default">
          <span class="noimg" style="position:absolute;inset:0;display:grid;place-content:center;
            gap:.7rem;text-align:center;padding:2rem;color:var(--muted)">
            <span class="mono">Made to order</span>
            <strong style="font-family:var(--ff-display);font-size:1.3rem;color:var(--ink)">%s</strong>
            <span style="font-size:.88rem;max-width:22rem">This configuration is produced to order and
              is not yet in the photo library. %s</span>
          </span>
        </div>
      </div>""" % (esc(p['sku']),
                   'See <a class="tlink" href="{P}%s">%s</a> for the same geometry on another back.'
                   % (sibling['url'], esc(sibling['sku'])) if sibling else
                   'Send us a sample request and we will photograph the run.')
        lb = ''

    mount_specs = [s for s in p['specs'] if s['mount']]
    arm_specs = [s for s in p['specs'] if not s['mount']]

    if p['kind'] == 'matrix':
        related = [q for q in SITE['products'] if q['style'] == p['style'] and q['slug'] != p['slug']]
        related_title = 'The same arm, a different wall.'
        related_lede = ('%s geometry is stocked on all five mounting systems.' % st['name'])
        also = [q for q in SITE['products'] if q['system'] == p['system'] and q['slug'] != p['slug']]
        also_title = 'Other styles on %s' % sy['name'].lower()
        context = """
          <dl class="kv">
            <div><dt>Mounting system</dt><dd><a class="tlink" href="{P}products/%s/">%s</a></dd></div>
            <div><dt>Hook style</dt><dd><a class="tlink" href="{P}styles/%s/">%s</a></dd></div>
            <div><dt>Mounts to</dt><dd>%s</dd></div>
            <div><dt>Ticketing</dt><dd>%s</dd></div>
            <div><dt>Best for</dt><dd>%s</dd></div>
          </dl>""" % (sy['slug'], sy['name'], st['slug'], st['name'], sy['fits'],
                      st['tag'] or 'No ticket holder', st['best'])
        intro = st['blurb']
        headline = st['lede']
    else:
        related = [q for q in SITE['products'] if q['kind'] == 'specialty' and q['slug'] != p['slug']][:5]
        related_title = 'More specialty fixtures.'
        related_lede = 'Purpose-built pieces for categories a straight peg cannot merchandise.'
        also = []
        also_title = ''
        context = """
          <dl class="kv">
            <div><dt>Category</dt><dd><a class="tlink" href="{P}products/specialty/">Specialty
              fixtures</a></dd></div>
            <div><dt>Finishes</dt><dd>Chrome, nickel, zinc, powder coat</dd></div>
            <div><dt>Applications</dt><dd>%s</dd></div>
          </dl>""" % ' &middot; '.join(p['uses'])
        intro = p['blurb']
        headline = p['lede']

    uses = ''.join('<li>%s</li>' % u for u in p['uses'])

    crumb_items = [('Home', 'index.html'), ('Products', 'products/')]
    crumb_items.append((sy['name'] if sy else 'Specialty Fixtures',
                        'products/%s/' % (sy['slug'] if sy else 'specialty')))
    crumb_items.append((p['sku'], None))

    body = """
  <section class="pagehead" style="padding-bottom:1rem">
    <div class="wrap">%s</div>
  </section>

  <section style="padding-bottom:clamp(3rem,6vw,5rem)">
    <div class="wrap">
      <div class="pdp">
        %s
        <div data-reveal="right">
          <span class="pdp-sku">%s</span>
          <h1 class="pdp-title">%s</h1>
          <p class="lede" style="margin-top:1.1rem">%s</p>
          <p style="margin-top:1rem">%s</p>
          <div class="pdp-actions">
            <a class="btn btn-accent" href="{P}contact/?sku=%s">Request a quote %s</a>
            <a class="btn btn-ghost" href="mailto:%s?subject=%s">Ask a question</a>
          </div>
          %s
        </div>
      </div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="feat" style="align-items:start">
        <div data-reveal="left">
          <p class="eyebrow">Specification</p>
          <h2 class="h-2">Every dimension we hold tooling for.</h2>
          <p class="lede" style="margin-top:1rem">Values shown as chips are stock options — choose any
             combination at order. Anything outside this list is a custom part, which we also make.</p>
          <ul class="feat-list" style="margin-top:1.6rem">%s</ul>
          <p style="margin-top:1.6rem"><a class="btn btn-ghost btn-sm" href="{P}custom/">Need it
             outside these ranges? %s</a></p>
        </div>
        <div data-reveal="right">
          %s
          %s
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">%s</p>
        <h2 class="h-2">%s</h2>
        <p class="lede" style="margin-top:1rem">%s</p>
      </div>
      <div class="cardgrid cols-4" data-stagger style="margin-top:2.2rem">%s</div>
    </div>
  </section>
  %s
  %s
  %s
""" % (crumbs(crumb_items), gallery, esc(p['sku']), esc(p['name']), strip_tags(headline), intro,
       esc(p['sku']), ARW, CO['email'],
       esc('Enquiry — %s (%s)' % (p['name'], p['sku'])), context,
       uses, ARW,
       ('<p class="eyebrow is-plain" style="margin-bottom:.6rem">Mounting</p>' + spec_table(mount_specs)
        if mount_specs else ''),
       ('<p class="eyebrow is-plain" style="margin:2rem 0 .6rem">Hook body &amp; supply</p>'
        + spec_table(arm_specs) if arm_specs else ''),
       'Alternatives', related_title, related_lede,
       ''.join(product_card(q) for q in related),
       ("""
  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Same wall</p>
        <h2 class="h-2">%s.</h2>
      </div>
      <div class="cardgrid cols-4" data-stagger style="margin-top:2.2rem">%s</div>
    </div>
  </section>""" % (also_title, ''.join(product_card(q) for q in also)) if also else ''),
       cta_band(title='Quote %s' % p['sku'],
                copy='Give us the length, the gauge, the finish and the annual volume. We will come back '
                     'with a price per thousand and a lead time.',
                primary=('contact/?sku=%s' % p['sku'], 'Request a quote')),
       lb)

    desc = '%s %s Part code %s. %s' % (p['name'], strip_tags(p['lede']), p['sku'],
                                       'Chrome, nickel, zinc or powder coated.')
    return page(p['url'] + 'index.html',
                '%s (%s) — Display Hook Specification | HCGretail' % (p['name'], p['sku']),
                desc[:300], body, 'products', depth=p['url'].count('/'))


def capabilities():
    steps = ''.join("""
        <article class="step" data-reveal>
          <div class="step-media">%s</div>
          <div class="step-body">
            <span class="step-n">%s</span>
            <h4 class="h-4">%s</h4>
            <p>%s</p>
          </div>
        </article>""" % (img(s['img'], s['name'], '(min-width:1120px) 25vw, 50vw'),
                         s['step'], s['name'], s['copy'])
        for s in SITE['process'])

    machines = ''.join("""
      <div class="feat%s" style="margin-bottom:clamp(2.5rem,6vw,5rem)">
        <div class="feat-media" data-reveal="scale">%s</div>
        <div data-reveal="%s">
          <div class="stat-n" style="font-size:clamp(2.6rem,5vw,4.2rem)">%s</div>
          <h3 class="h-3" style="margin:.3rem 0 .9rem">%s</h3>
          <p class="lede">%s</p>
        </div>
      </div>""" % (' rev' if i % 2 else '',
                   img(m['img'], m['label'], '(min-width:900px) 46vw, 92vw'),
                   'left' if i % 2 else 'right', m['n'], m['label'], m['copy'])
        for i, m in enumerate(SITE['machines']))

    shots = ['raw-steel-coil', 'stamping-press', 'brazing', 'wireform-cnc', 'plated-parts',
             'assembly-floor', 'warehouse-3', 'carton-stock']
    labels = ['Steel coil stock', 'Stamping press', 'Brazing station', 'CNC wire former',
              'Plated components', 'Assembly floor', 'Finished goods', 'Carton stock']
    mosaic = ''.join('<figure%s>%s<figcaption>%s</figcaption></figure>'
                     % (' class="tall"' if i in (1, 5) else '',
                        img('assets/img/factory/' + s, l, '(min-width:780px) 25vw, 50vw'), l)
                     for i, (s, l) in enumerate(zip(shots, labels)))

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Capabilities</p>
          <h1 class="h-1" data-words>Ninety machines, one roof, no subcontractors.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">Our China headquarters and factory runs 6,000&nbsp;m&sup2; of production floor in
             Zhejiang, turning out more than 100,000 hooks a day. Stamping, wire forming, welding,
             finishing, assembly and packing all happen in the same building.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap wrap-wide">
      <div class="hero-stage" data-clip style="aspect-ratio:16/7">%s</div>
    </div>
  </section>

  <section class="section-tight">%s</section>

  <section class="section">
    <div class="wrap">
      <div style="max-width:42rem;margin-bottom:clamp(2.5rem,5vw,4rem)" data-reveal>
        <p class="eyebrow">Plant</p>
        <h2 class="h-1">What is actually on the floor.</h2>
      </div>
      %s
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Process</p>
        <h2 class="h-2">Coil to carton, in seven stages.</h2>
        <p class="lede" style="margin-top:1rem">Nothing leaves the building between the raw wire and the
           packed carton, which is why a lead time we quote is a lead time we control.</p>
      </div>
    </div>
    <div class="steps" data-stagger style="margin-top:2.5rem">%s</div>
  </section>

  <section class="section">
    <div class="wrap wrap-wide">
      <div class="wrap" style="padding-inline:0;max-width:40rem;margin-bottom:2rem" data-reveal>
        <p class="eyebrow">Inside the plant</p>
        <h2 class="h-2">Zhejiang, China.</h2>
      </div>
      <div class="mosaic" data-reveal="fade">%s</div>
    </div>
  </section>

  <section class="section section-dark">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow on-dark">Quality</p>
          <h2 class="h-1">Quality first, integrity-based operation, continuous improvement.</h2>
          <p class="lede">Not a slogan on a wall — a full-process control system that runs from raw
             material procurement through to finished goods despatch.</p>
          <ul class="feat-list">
            <li>Incoming inspection on wire gauge and sheet thickness before anything is cut</li>
            <li>Dimensional checks against the drawing at forming and again after welding</li>
            <li>Pull-testing on welded joints, the failure point that matters most in service</li>
            <li>Finish inspection for coverage, adhesion and colour match before packing</li>
          </ul>
        </div>
        <div class="feat-media" data-reveal="scale">%s</div>
      </div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Capabilities', None)]),
       img('assets/img/factory/wireform-hall', 'Wire forming production hall', '100vw', eager=True),
       stats_block(), machines, steps, mosaic,
       img('assets/img/factory/qc-bench', 'Quality inspection and assembly bench',
           '(min-width:900px) 46vw, 92vw'),
       cta_band(title='Come and see it.',
                copy='We welcome customers at the Zhejiang headquarters for site inspection and '
                     'negotiation — and the North American office can arrange it.',
                secondary=('about/', 'About HCGretail')))

    return page('capabilities/index.html', 'Manufacturing Capabilities — 6,000 m² Hook Factory | HCGretail',
                '90+ machines across stamping, wire forming and welding in a 6,000 m² Zhejiang factory '
                'producing over 100,000 retail display hooks per day.', body, 'capabilities')


def custom():
    cards = ''.join("""
      <article class="step" data-reveal style="padding-bottom:1.8rem">
        <div class="step-body" style="padding-top:1.6rem">
          <span class="step-n">%02d</span>
          <h4 class="h-3" style="margin:.5rem 0 .7rem">%s</h4>
          <p style="font-size:.95rem;color:var(--ink-2)">%s</p>
        </div>
      </article>""" % (i + 1, c['title'], c['copy'])
        for i, c in enumerate(SITE['custom']))

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Custom &amp; OEM / ODM</p>
          <h1 class="h-1" data-words>Bring a drawing. Or a sample. Or a photo of the shelf.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">Eighteen years of bespoke hook work for global buyers. We will work from a
             technical drawing, a physical sample, or nothing more than a picture of the fixture and a
             description of what has to hang on it.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap wrap-wide">
      <div class="hero-stage" data-clip style="aspect-ratio:16/7">%s</div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">What we customise</p>
        <h2 class="h-2">Four things change. The engineering does not.</h2>
      </div>
    </div>
    <div class="steps" style="margin-top:2.4rem" data-stagger>%s</div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="feat">
        <div class="feat-media" data-reveal="scale">%s</div>
        <div data-reveal="right">
          <p class="eyebrow">Tooling and prototyping</p>
          <h2 class="h-1">Prove it small before you ship it big.</h2>
          <p class="lede">Mould development happens in-house, so a new geometry does not sit in an
             external tool shop&rsquo;s queue. That is what makes a genuine trial run possible.</p>
          <ul class="feat-list">
            <li>Fast prototyping from drawing, sample or photograph</li>
            <li>In-house mould and tool development</li>
            <li>Small-batch trial production before committing to volume</li>
            <li>Scale from trial run to full container without re-tooling</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Finishing</p>
        <h2 class="h-2">Brand-matched, not batch-matched.</h2>
        <p class="lede" style="margin-top:1rem">Powder coat to any RAL or Pantone, matt or gloss, so a
           shop-in-shop build reads as one fixture rather than four suppliers.</p>
      </div>
      <div style="margin-top:2.4rem">%s</div>
    </div>
  </section>

  <section class="section section-dark">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow on-dark">Private label</p>
          <h2 class="h-1">It can arrive as your product.</h2>
          <p class="lede">Custom carding, poly-bagging, printed cartons and your own part numbering. For
             distributors and fixture houses, the hook can land ready for the shelf under your name.</p>
          <ul class="feat-list">
            <li>Private-label carding and header cards</li>
            <li>Poly-bagged multi-packs to your count</li>
            <li>Printed cartons with your SKU and barcode</li>
            <li>Carton quantities set to your pick-and-pack process</li>
          </ul>
        </div>
        <div class="feat-media" data-reveal="scale">%s</div>
      </div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('Custom &amp; OEM', None)]),
       img('assets/img/factory/range-black', 'Custom hook lengths laid out by size', '100vw', eager=True),
       cards,
       img('assets/img/factory/wireform-cnc', 'CNC wire forming setup',
           '(min-width:900px) 46vw, 92vw'),
       finish_block(),
       img('assets/img/factory/packing-fixture', 'Packing and fixture assembly',
           '(min-width:900px) 46vw, 92vw'),
       cta_band(title='Send us the drawing.',
                copy='Dimensions, load case, finish, annual volume — or just a photo and a description. '
                     'We will tell you what it costs and how fast we can prove it.',
                secondary=('capabilities/', 'See the factory')))

    return page('custom/index.html', 'Custom & OEM Hook Manufacturing — Private Label | HCGretail',
                'Bespoke retail display hooks made to your drawing, sample or application. In-house '
                'tooling, fast prototyping, RAL and Pantone powder coating, private label packaging.',
                body, 'custom &amp; oem')


def about():
    regions = ''.join('<span class="chip chip-solid">%s</span>' % r for r in SITE['regions'])
    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">About</p>
          <h1 class="h-1" data-words>Eighteen years on one thing.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">%s is the North American office of %s, in Zhejiang, China. Founded in 2008,
             the parent company has spent eighteen years doing one thing: manufacturing supermarket
             shelf display hooks and metal stamping parts.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section-tight">
    <div class="wrap wrap-wide">
      <div class="hero-stage" data-clip style="aspect-ratio:16/7">%s</div>
    </div>
  </section>

  <section class="section-tight">%s</section>

  <section class="section">
    <div class="wrap">
      <div class="feat">
        <div data-reveal="left">
          <p class="eyebrow">North America</p>
          <h2 class="h-1">A local office in front of the factory.</h2>
          <p class="lede">HCGretail exists so that North American customers deal with a local office
             rather than a time zone. Initial enquiry, sample confirmation, order follow-up and
             after-sales all run through the same people.</p>
          <ul class="feat-list">
            <li>Quick response on enquiries and quotations, in your working hours</li>
            <li>Sample coordination and confirmation before production starts</li>
            <li>Order follow-up through production and shipping</li>
            <li>After-sales support that does not route through a trading company</li>
          </ul>
        </div>
        <div class="feat-media" data-reveal="scale">%s</div>
      </div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div class="feat rev">
        <div class="feat-media" data-reveal="scale">%s</div>
        <div data-reveal="left">
          <p class="eyebrow">Reach</p>
          <h2 class="h-1">Twenty-plus countries, four continents.</h2>
          <p class="lede">For eighteen years our products have been exported worldwide, building
             long-term partnerships with well-known display rack brands and retail chains.</p>
          <div class="tile-meta" style="margin-top:1.4rem">%s</div>
          <p style="margin-top:1.8rem">Upholding the core values of quality first, integrity-based
             operation and continuous improvement, we combine internationally advanced manufacturing
             techniques with lean management. A full-process quality control system runs from raw
             material procurement through to finished goods delivery.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap wrap-narrow" style="margin-inline:auto">
      <div class="accordion" data-reveal>
        <div class="acc is-open">
          <button class="acc-btn" type="button" aria-expanded="true">Who we supply %s</button>
          <div class="acc-body"><div><div class="inner">
            <p>Display rack manufacturers, shopfitting and fixture houses, retail chains, wholesalers and
               distributors. Most of our volume ships to businesses that resell or install rather than to
               end retailers directly.</p>
          </div></div></div>
        </div>
        <div class="acc">
          <button class="acc-btn" type="button" aria-expanded="false">Minimum order quantities %s</button>
          <div class="acc-body"><div><div class="inner">
            <p>Catalogue hooks are cartoned at 100 or 200 pieces depending on style and gauge. Specialty
               fixtures carry their own minimums — typically 1,000 or 3,000 pieces, and 3 units for the
               promotion basket. Exact MOQ per part is listed on its specification page.</p>
          </div></div></div>
        </div>
        <div class="acc">
          <button class="acc-btn" type="button" aria-expanded="false">Custom and private label %s</button>
          <div class="acc-body"><div><div class="inner">
            <p>Yes to both, and it is a large share of what we make. Custom geometry from drawing, sample
               or application; private-label carding, bagging and printed cartons.
               <a class="tlink" href="{P}custom/">More on custom work %s</a></p>
          </div></div></div>
        </div>
        <div class="acc">
          <button class="acc-btn" type="button" aria-expanded="false">Factory visits %s</button>
          <div class="acc-body"><div><div class="inner">
            <p>We welcome customers to the China headquarters and factory for site inspection and
               business negotiation. The North American office arranges the visit.</p>
            <p class="muted" style="font-size:.88rem">%s</p>
          </div></div></div>
        </div>
      </div>
    </div>
  </section>

  %s
""" % (crumbs([('Home', 'index.html'), ('About', None)]), CO['brand'], CO['parent'],
       img('assets/img/factory/assembly-room', 'Assembly and inspection room', '100vw', eager=True),
       stats_block(),
       img('assets/img/factory/office', 'Production office', '(min-width:900px) 46vw, 92vw'),
       img('assets/img/factory/warehouse-4', 'Finished goods warehouse',
           '(min-width:900px) 46vw, 92vw'),
       regions, CHEV, CHEV, CHEV, ARW, CHEV, CO['address'],
       cta_band(title='Start a conversation.',
                copy='Whether it is a single carton of a catalogue part or a bespoke programme across a '
                     'store estate, the same office picks it up.'))

    return page('about/index.html', 'About HCGretail — North American Office, Hook Manufacturer Since 2008',
                'HCGretail is the North American office of Wuyi Hongchanggu Hardware Products Co., Ltd. '
                'Eighteen years manufacturing retail display hooks, exported to 20+ countries.',
                body, 'about')


def contact():
    sys_opts = ''.join('<option value="%s">%s</option>' % (s['name'], s['name'])
                       for s in SITE['systems'])
    fin_checks = ''.join(
        '<input type="checkbox" id="fin%d" name="finish" value="%s"><label for="fin%d">%s</label>'
        % (i, f['name'], i, f['name']) for i, f in enumerate(SITE['finishes']))

    body = """
  <section class="pagehead">
    <div class="wrap">
      %s
      <div class="pagehead-grid">
        <div data-reveal="fade">
          <p class="eyebrow">Contact</p>
          <h1 class="h-1" data-words>Tell us what has to hang on it.</h1>
        </div>
        <div data-reveal="right">
          <p class="lede">The more you can tell us about the panel, the product and the volume, the more
             useful the first reply is. If you already know the part code, put it in and we will quote
             straight from it.</p>
        </div>
      </div>
    </div>
  </section>

  <section style="padding-bottom:clamp(3rem,7vw,6rem)">
    <div class="wrap">
      <div class="feat" style="align-items:start">
        <div data-reveal="left">
          <form class="form" data-quote="%s" novalidate>
            <div class="form-row">
              <div class="field">
                <label for="name">Name <span class="req">*</span></label>
                <input id="name" name="name" required autocomplete="name">
              </div>
              <div class="field">
                <label for="company">Company</label>
                <input id="company" name="company" autocomplete="organization">
              </div>
            </div>
            <div class="form-row">
              <div class="field">
                <label for="email">Email <span class="req">*</span></label>
                <input id="email" name="email" type="email" required autocomplete="email">
              </div>
              <div class="field">
                <label for="country">Country</label>
                <input id="country" name="country" autocomplete="country-name">
              </div>
            </div>
            <div class="form-row">
              <div class="field">
                <label for="system">Mounting system</label>
                <select id="system" name="system">
                  <option value="">Not sure yet</option>
                  %s
                  <option value="Specialty fixture">Specialty fixture</option>
                  <option value="Custom part">Custom part</option>
                </select>
              </div>
              <div class="field">
                <label for="qty">Annual volume</label>
                <input id="qty" name="annual_volume" placeholder="e.g. 50,000 pcs">
              </div>
            </div>
            <div class="field">
              <label for="products">Part codes or products</label>
              <input id="products" name="products" placeholder="e.g. CB-SX-01, DB-DX-01">
            </div>
            <div class="field">
              <label>Finish</label>
              <div class="checks">%s</div>
            </div>
            <div class="field">
              <label for="msg">What are you hanging? <span class="req">*</span></label>
              <textarea id="msg" name="message" required
                placeholder="Panel type and thickness, product weight and pack format, arm length, wire gauge, ticketing, timing."></textarea>
            </div>
            <div>
              <button class="btn btn-accent" type="submit">Send enquiry %s</button>
              <p class="form-note" style="margin-top:.9rem">This opens your email client with the details
                 filled in — nothing is sent to a third-party server. Prefer to write directly?
                 <a class="tlink" href="mailto:%s">%s</a></p>
              <p class="form-note" data-quote-note hidden style="color:var(--accent)">Your email client
                 should now be open. If nothing happened, email us at %s.</p>
            </div>
          </form>
        </div>

        <div data-reveal="right">
          <div style="border:1px solid var(--line);border-radius:var(--r-lg);padding:clamp(1.4rem,3vw,2.2rem)">
            <p class="eyebrow">North American office</p>
            <h2 class="h-3">%s</h2>
            <p style="margin-top:.8rem">Localised support across North America — enquiry, sample
               confirmation, order follow-up and after-sales, all through one office.</p>
            <dl class="kv">
              <div><dt>Email</dt><dd><a class="tlink" href="mailto:%s">%s</a></dd></div>
              <div><dt>Parent company</dt><dd>%s</dd></div>
              <div><dt>Established</dt><dd>%d</dd></div>
            </dl>
            <p class="eyebrow" style="margin:1.8rem 0 .6rem">China headquarters &amp; factory</p>
            <p style="font-size:.92rem;color:var(--ink-2)">%s</p>
            <p style="font-size:.92rem;margin-top:1rem">Customers are welcome to visit for site
               inspection and negotiation.</p>
          </div>

          <div style="margin-top:1.2rem;border-radius:var(--r-lg);overflow:hidden">%s</div>

          <div class="tile-meta" style="margin-top:1.2rem">
            <span class="chip">Replies within one working day</span>
            <span class="chip">OEM &amp; ODM</span>
            <span class="chip">Samples available</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section section-bone">
    <div class="wrap">
      <div style="max-width:40rem" data-reveal>
        <p class="eyebrow">Not sure what you need?</p>
        <h2 class="h-2">Start from the wall.</h2>
        <p class="lede" style="margin-top:1rem">If you know what panel you are mounting to, the
           catalogue narrows to seven options in one click.</p>
      </div>
      <div class="cardgrid cols-3" data-stagger style="margin-top:2.2rem">%s</div>
    </div>
  </section>
""" % (crumbs([('Home', 'index.html'), ('Contact', None)]), CO['email'], sys_opts, fin_checks,
       ARW, CO['email'], CO['email'], CO['email'], CO['brand'], CO['email'], CO['email'],
       CO['parent'], CO['founded'], CO['address'],
       img('assets/img/factory/slatwall-install-2', 'Hooks installed on a slatwall panel',
           '(min-width:900px) 46vw, 92vw'),
       ''.join(system_tile(s, i + 1) for i, s in enumerate(SITE['systems'][:3])))

    return page('contact/index.html', 'Contact HCGretail — Request a Display Hook Quote',
                'Request a quote for retail display hooks. North American office with local support for '
                'enquiry, samples, order follow-up and after-sales.', body, 'contact')


# -------------------------------------------------------------------- extras
def sitemap(paths):
    urls = ''.join('  <url><loc>/%s</loc></url>\n' % p.replace('index.html', '') for p in sorted(paths))
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % urls)


def clean():
    for d in ('products', 'styles', 'capabilities', 'custom', 'about', 'contact'):
        p = os.path.join(ROOT, d)
        if os.path.isdir(p):
            shutil.rmtree(p)
    for f in ('script.js', 'style.css'):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            os.remove(p)


if __name__ == '__main__':
    clean()
    paths = [home(), products_index(), specialty_index(), capabilities(), custom(), about(), contact()]
    paths += [system_page(s) for s in SITE['systems']]
    paths += [style_page(s) for s in SITE['styles']]
    paths += [product_page(p) for p in SITE['products']]
    sitemap(paths)
    print('rendered %d pages' % len(paths))
