# -*- coding: utf-8 -*-
"""Single source of truth for the HCGretail catalogue.

Specification text is read straight out of `new content/Hook product list.xlsx`,
so published pages can never drift from the master product list. Everything else
in here is editorial copy written around that data.
"""
import os, re, json, zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, 'new content', 'Hook product list.xlsx')
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


# ---------------------------------------------------------------- xlsx reader
def read_sheet():
    z = zipfile.ZipFile(XLSX)
    shared = [''.join(t.text or '' for t in si.iter(M + 't'))
              for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = {}
    for row in sheet.iter(M + 'row'):
        cells = {}
        for c in row:
            col = re.match(r'[A-Z]+', c.get('r')).group()
            v, ist = c.find(M + 'v'), c.find(M + 'is')
            if c.get('t') == 's' and v is not None:
                val = shared[int(v.text)]
            elif ist is not None:
                val = ''.join(x.text or '' for x in ist.iter(M + 't'))
            elif v is not None:
                val = v.text
            else:
                val = ''
            if val:
                cells[col] = val
        if cells:
            rows[int(row.get('r'))] = cells
    return rows


# ------------------------------------------------------------- spec normaliser
# Ordered longest-prefix-first: the first match wins.
LABELS = [
    ('clip size*后高', 'Clip size (W × D × H)'),
    ('pegboard thickness', 'Pegboard thickness'),
    ('sheet thickness', 'Sheet thickness'),
    ('clip thickness', 'Clip thickness'),
    ('tube thickness', 'Tube diameter'),
    ('up line length', 'Upper wire length'),
    ('down line length', 'Lower wire length'),
    ('metal price tag', 'Metal price tag'),
    ('surface handling', 'Surface finish'),
    ('u length', 'U-wire length'),
    ('head shape', 'Head shape'),
    ('price tag', 'Price tag (PVC)'),
    ('clip size', 'Clip size'),
    ('feet size', 'Base footprint'),
    ('net size', 'Grid aperture'),
    ('distance', 'Peg centres'),
    ('diameter', 'Wire diameter'),
    ('thickness', 'Tube diameter'),
    ('packing', 'Packing'),
    ('height', 'Height'),
    ('length', 'Length'),
    ('lenth', 'Length'),
    ('balls', 'Ball count'),
    ('size', 'Overall size'),
    ('moq', 'Minimum order'),
]
UNITLESS = {'Surface finish', 'Head shape'}
NOTES = {
    'Surface finish': 'Choose one at order',
    'Wire diameter': 'Sets the load rating',
    'Grid aperture': 'Maximum mesh opening',
}
# Spec labels that identify how a hook attaches, surfaced separately in the UI.
MOUNT_LABELS = {'Clip size', 'Clip size (W × D × H)', 'Clip thickness', 'Peg centres',
                'Pegboard thickness', 'Tube diameter', 'Grid aperture'}


def norm_label(raw):
    k = raw.strip().lower().rstrip(':：').strip()
    for needle, nice in LABELS:
        if k.startswith(needle):
            return nice
    k = raw.strip().rstrip(':：').strip()
    return k[:1].upper() + k[1:]


def norm_packing(val):
    v = val.lower().replace(' ', '')
    m = re.search(r'(\d+)pcs', v) or re.search(r'pcs(\d+)', v)
    return 'Ø6 mm and under — %s pcs per carton' % m.group(1) if m else val.strip()


def split_options(val):
    """'25*76/30*80/38*80mm' -> (['25 × 76', '30 × 80', '38 × 80'], 'mm')"""
    v = val.strip().replace('内', '').strip()
    v = re.sub(r'\bwith\b\s*$', '', v).strip()
    unit = ''
    for u in ('mm', 'pcs'):
        if v.lower().endswith(u):
            unit, v = u, v[:-len(u)].strip()
            break
    opts = [o.strip().replace('*', ' × ') for o in v.split('/') if o.strip()]
    return opts, unit


def parse_specs(blob):
    """Turn one spreadsheet cell into an ordered list of spec rows."""
    out = []
    for line in (blob or '').split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = re.split(r'[：:]', line, 1)
        if len(parts) != 2:
            continue
        label, value = norm_label(parts[0]), parts[1].strip()
        if label == 'Packing':
            row = dict(label=label, options=[norm_packing(value)], unit='')
        elif label == 'Minimum order':
            shown = '{:,} pcs'.format(int(value)) if value.strip().isdigit() else value
            row = dict(label=label, options=[shown], unit='')
        else:
            opts, unit = split_options(value)
            if label in UNITLESS:
                opts = [o[:1].upper() + o[1:] for o in opts]
            row = dict(label=label, options=opts, unit=unit)
        row['menu'] = len(row['options']) > 1
        row['note'] = NOTES.get(label, '')
        row['mount'] = label in MOUNT_LABELS
        out.append(row)
    return out


# ------------------------------------------------------------------- taxonomy
SYSTEMS = [
    dict(
        slug='slatwall', col='B', code='CB', name='Slatwall Hooks', short='Slatwall',
        back='stamped slatwall clip',
        pitch='Drops in, locks flush, stays level.',
        lede='Stamped steel clip that drops into a standard slatwall groove and locks flush.',
        blurb='The workhorse of soft-line and impulse merchandising. A 1.5–2.5&nbsp;mm stamped clip seats '
              'into standard slatwall channel, sits tight against the panel face and carries the wire arm '
              'dead level under load — no droop, no rotation, no gapping between facings.',
        fits='Standard slatwall panel, MDF or aluminium-inserted',
        surface='Slatwall panel',
        clip='25 × 76 / 30 × 80 / 38 × 80&nbsp;mm stamped clip',
        uses=['Apparel and accessory walls', 'Convenience and c-store impulse bays',
              'Hardware and auto-parts aisles', 'Pop-up and seasonal fixtures'],
        hero='assets/img/factory/slatwall-install',
    ),
    dict(
        slug='pegboard', col='C', code='DB', name='Pegboard Hooks', short='Pegboard',
        back='twin-prong pegboard back',
        pitch='The panel everyone has, done properly.',
        lede='Twin-prong wire back for perforated board on 25.4, 32, 45 or 50&nbsp;mm centres.',
        blurb='The most widely specified back panel in retail, and the most abused. Our pegboard range is '
              'formed with a return prong sized to the exact board thickness, so the hook cannot walk out '
              'when a shopper lifts a facing — the single biggest source of shrink and re-merchandising '
              'labour on a peg wall.',
        fits='Perforated board 1–10&nbsp;mm thick, 25.4 / 32 / 45 / 50&nbsp;mm hole centres',
        surface='Perforated pegboard',
        clip='Formed twin-prong wire back',
        uses=['Hardware, DIY and trade counters', 'Toys, stationery and party goods',
              'Pharmacy and HBA gondola ends', 'Workshop and garage organisation'],
        hero='assets/img/products/db-sx-01/1',
    ),
    dict(
        slug='tube', col='D', code='FG', name='Tube Snap Hooks', short='Tube',
        back='snap-on tube clip',
        pitch='Re-plan a whole rail by hand.',
        lede='Sprung clip that snaps onto 15, 20 or 25&nbsp;mm round tube — no tools, no fasteners.',
        blurb='Built for tubular garment rails, round-bar gridwork and clothing rack uprights. A 2&nbsp;mm '
              'stamped clip snaps over the tube and grips by spring tension, so a merchandiser can re-plan '
              'an entire rail by hand in minutes without a single fixing.',
        fits='Round tube 15 / 20 / 25&nbsp;mm outside diameter',
        surface='Round tube and bar',
        clip='29 × 38 × 20 / 38 × 38 × 20&nbsp;mm snap clip, 2&nbsp;mm',
        uses=['Tubular garment rails and rounders', 'Market and forecourt display',
              'Rail-mounted accessory add-ons', 'Temporary promotional rigs'],
        hero='assets/img/products/fg-sx-01/1',
    ),
    dict(
        slug='bow', col='E', code='WJ-SG', name='Grid Hooks — Bow Clip', short='Grid · Bow',
        back='bow grid clip',
        pitch='Load spread across the mesh, not one weld.',
        lede='Bow-form grid clip for welded wire mesh up to 80 × 80&nbsp;mm aperture.',
        blurb='The heavier of our two wire-grid backs. A bow-shaped 1.5–2&nbsp;mm clip wraps two mesh wires '
              'at once and spreads load across the grid rather than pointing it at a single weld — the '
              'right call for dense, heavy or high-turn planograms on large-aperture mesh.',
        fits='Welded wire grid, apertures up to 80 × 80&nbsp;mm',
        surface='Wire grid / mesh panel',
        clip='25 × 83&nbsp;mm bow clip, 1.5–2&nbsp;mm',
        uses=['Wire-grid shop-in-shop walls', 'Cash-and-carry and wholesale mesh bays',
              'Trade show and exhibition grids', 'Back-of-house and stockroom mesh'],
        hero='assets/img/products/wj-sg-sx-01/1',
    ),
    dict(
        slug='longstrip', col='F', code='WJ-DG', name='Grid Hooks — Long Strip', short='Grid · Strip',
        back='long-strip grid clip',
        pitch='A longer bearing face for finer mesh.',
        lede='Long-strip grid clip for tighter mesh up to 60 × 60&nbsp;mm aperture.',
        blurb='A 25 × 68 or 25 × 80&nbsp;mm strip clip that runs along the mesh wire instead of across it. '
              'The longer bearing face stops the arm tipping on fine-aperture grid, which is where short '
              'clips fail first — typically on lightweight panels carrying long-arm facings.',
        fits='Welded wire grid, apertures up to 60 × 60&nbsp;mm',
        surface='Wire grid / mesh panel',
        clip='25 × 68 / 25 × 80&nbsp;mm strip clip, 1.5–2&nbsp;mm',
        uses=['Fine-aperture mesh panels', 'Lightweight and mobile grid fixtures',
              'Retail merchandising cages', 'Craft, hobby and homeware mesh walls'],
        hero='assets/img/products/wj-dg-sx-01/1',
    ),
]

STYLES = [
    dict(
        slug='single-wire', row=3, code='DX-01', name='Single Wire', short='Single wire',
        lede='One arm, eight stock lengths. The default facing for bagged and carded product.',
        blurb='The most specified hook in retail and the lowest cost per facing. A single wire arm with an '
              'upturned tip that holds carded stock square and lets a shopper lift one unit without '
              'dragging the rest forward.',
        best='Lightweight carded and bagged product where facings turn fast and cost per hook matters.',
        tag=None, arms=1,
        traits=['Eight lengths, 50–400&nbsp;mm', 'Upturned retention tip', 'Lowest cost per facing',
                '200 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='double-wire-pvc-tag', row=6, code='SX-01', name='Double Wire + PVC Price Tag',
        short='Double wire · PVC tag',
        lede='Twin arms with a stepped lower wire carrying a clear PVC label holder.',
        blurb='Two arms carry the product and a shorter lower wire carries the ticket. Because the tag '
              'rides below the facing rather than in front of it, price stays legible with the peg full '
              'and the front unit stays fully visible — the layout most planograms are drawn against.',
        best='Priced, ticketed and promoted lines where the label must survive a full peg.',
        tag='PVC label holder, 60 × 40 or 80 × 40&nbsp;mm', arms=2,
        traits=['Twin-arm anti-roll geometry', 'Stepped upper and lower wires',
                'Clear PVC ticket holder', '100 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='double-wire-metal-tag', row=9, code='SX-02', name='Double Wire + Metal Price Tag',
        short='Double wire · metal tag',
        lede='The same twin-arm body with a stamped metal ticket plate in place of PVC.',
        blurb='Specified where PVC holders get snapped off or sun-bleached: forecourts, trade counters, '
              'outdoor and high-traffic bays. The 75 × 25 or 54 × 25&nbsp;mm plate is stamped and finished '
              'with the hook, so it takes the same abuse the hook does.',
        best='High-traffic, outdoor or trade environments that chew through plastic ticket holders.',
        tag='Stamped metal plate, 75 × 25 or 54 × 25&nbsp;mm', arms=2,
        traits=['Stamped steel ticket plate', 'Finished with the hook body',
                'No plastic to snap or yellow', '100 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='u-wire', row=12, code='UX-01', name='U Wire', short='U wire',
        lede='A wire bent into a U so the facing sits inside the loop and cannot roll off.',
        blurb='The loop closes the load path. Round or square head, four to six millimetre wire, and a '
              'geometry that keeps heavy, awkward or slippery product captive on the arm instead of '
              'walking toward the tip as the peg empties.',
        best='Heavier, denser or unevenly balanced product that a flat arm lets creep forward.',
        tag=None, arms=2,
        traits=['Closed U load path', 'Square or round head', 'Ø4–6&nbsp;mm wire',
                '100 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='u-triple-pvc-tag', row=15, code='USX-01', name='U Triple Wire + PVC Price Tag',
        short='U triple · PVC tag',
        lede='U-wire load path plus a third upper wire carrying a PVC label holder.',
        blurb='Everything the U wire does, ticketed. A third wire runs above the loop to hold the label '
              'clear of the product, so you keep the captive load path on heavy stock without losing the '
              'price face when the peg is full.',
        best='Heavy ticketed lines — tools, hardware, automotive, pet and garden.',
        tag='PVC label holder, 60 × 40 or 80 × 40&nbsp;mm', arms=3,
        traits=['Captive U load path', 'Dedicated ticket wire', 'Square or round head',
                '100 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='u-triple-metal-tag', row=18, code='USX-02', name='U Triple Wire + Metal Price Tag',
        short='U triple · metal tag',
        lede='The heaviest-duty configuration in the range: U load path, metal ticket plate.',
        blurb='Where the product is heavy and the environment is hard. Triple-wire U geometry carries the '
              'weight, a stamped 75 × 25 or 54 × 32&nbsp;mm plate carries the price, and neither is going to '
              'be the thing that fails first.',
        best='Heavy stock in trade, industrial, outdoor and forecourt environments.',
        tag='Stamped metal plate, 75 × 25 or 54 × 32&nbsp;mm', arms=3,
        traits=['Captive U load path', 'Stamped steel ticket plate', 'Square or round head',
                '100 pcs / carton at Ø6&nbsp;mm'],
    ),
    dict(
        slug='ball-hook', row=21, code='DZ-01', name='Ball Hook', short='Ball hook',
        lede='A short Ø8&nbsp;mm stub carrying four to seven welded balls — one facing each.',
        blurb='A multi-facing hook in the footprint of a single one. Four to seven balls along a 20–35&nbsp;mm '
              'stub each hold a hanging item, so lightweight strap, cord and looped product merchandises in '
              'a fraction of the wall area a peg run would need.',
        best='Looped, strapped and hanging product — keyrings, cords, straps, small leather goods.',
        tag=None, arms=1,
        traits=['4 / 5 / 6 / 7 welded balls', 'Ø8&nbsp;mm stub',
                'Multiple facings in one footprint', '200 pcs / carton at Ø6&nbsp;mm'],
    ),
]

SPECIALTY = [
    dict(slug='display-stand', cell=('B', 25), name='Floor Display Stand',
         lede='Free-standing 600 or 900&nbsp;mm floor stand on a 250 × 300&nbsp;mm foot.',
         blurb='A self-supporting stand for aisle ends, counters and promotional islands where there is no '
               'wall to hang from. Ø7–8&nbsp;mm frame, weighted footprint, and the same finishing options as '
               'the wall range so a promotion reads as one family.',
         uses=['Counter-top and aisle-end promotions', 'Pop-up and seasonal islands',
               'Trade show stands']),
    dict(slug='hat-hook', cell=('C', 25), name='Hat Hook',
         lede='Shaped Ø4–6&nbsp;mm arm that holds a cap crown-up without creasing the brim.',
         blurb='A cap sitting on a straight peg deforms; a cap on a shaped arm holds its shape and its '
               'facing. Sized for structured and unstructured caps alike.',
         uses=['Headwear walls', 'Sportswear and team stores', 'Workwear and safety']),
    dict(slug='shoe-hook', cell=('D', 25), name='Shoe Hook',
         lede='Ø5.5&nbsp;mm arm with a 1&nbsp;mm stamped sole plate that presents footwear face-out.',
         blurb='A flat plate cradles the sole so footwear presents at the angle a shopper actually reads it '
               'from, instead of dangling by the heel. Pairs stay together and stay square.',
         uses=['Footwear walls', 'Sports and outdoor retail', 'Discount and value formats']),
    dict(slug='eyeglass-hook', cell=('E', 25), name='Eyeglass Hook',
         lede='200&nbsp;mm Ø3&nbsp;mm fine-wire arm sized to the bridge of a frame.',
         blurb='Fine wire so the arm disappears behind the product, and a length that carries a deep run of '
               'frames without the front pair masking the ones behind it.',
         uses=['Optical and sunglass displays', 'Pharmacy readers', 'Forecourt and travel retail']),
    dict(slug='towel-hook', cell=('F', 25), name='Towel Hook',
         lede='Wide-span Ø4–6&nbsp;mm arm on 25 or 50&nbsp;mm centres for folded textiles.',
         blurb='Folded and rolled textiles need span, not length. A wide bearing arm carries a bulky fold '
               'without the crease line a narrow peg presses into the pile.',
         uses=['Homeware and bath departments', 'Beach and seasonal textiles',
               'Hotel and contract supply']),
    dict(slug='sports-ball-rack', cell=('B', 29), name='Sports Ball Rack',
         lede='Ø140&nbsp;mm formed ring in Ø5–6&nbsp;mm wire that cradles an inflated ball.',
         blurb='A ring, not a hook. The ball sits in the cradle and stays there, so a wall of footballs, '
               'basketballs and volleyballs holds its planogram instead of ending up on the floor.',
         uses=['Sporting goods walls', 'Toy and leisure aisles', 'School and club supply']),
    dict(slug='tool-hook', cell=('C', 29), name='Power Tool Hook',
         lede='Heavy Ø5.8&nbsp;mm arm shaped to carry a tool by its handle or body.',
         blurb='Power tools are heavy, top-weighted and expensive. This arm is drawn for that load case: '
               'thick wire, a deliberate retention shape, and a geometry that stops the tool swinging into '
               'the facing beside it.',
         uses=['Power tool and DIY walls', 'Trade counters', 'Workshop and garage retail']),
    dict(slug='razor-hook', cell=('D', 29), name='Razor Hook',
         lede='Ø5–6&nbsp;mm arm sized for blister-packed razors and blade cartridges.',
         blurb='High-value, high-shrink, small-pack product. Sized so the pack sits tight to the panel with '
               'no slack to sweep, which is exactly what this category needs.',
         uses=['HBA and grooming bays', 'Pharmacy and drug store', 'Convenience and travel retail']),
    dict(slug='promotion-basket', cell=('E', 29), name='Promotion Basket',
         lede='800 × 520 × 700&nbsp;mm mobile wire dump basket on castors.',
         blurb='A rolling bulk bin for clearance, seasonal and dump merchandising. Welded wire body, castor '
               'base, and a footprint that moves through a standard aisle without re-planning the floor.',
         uses=['Clearance and markdown', 'Seasonal dump merchandising',
               'Forecourt and entrance offers']),
    dict(slug='wave-hook', cell=('F', 29), name='Wave Hook',
         lede='200&nbsp;mm Ø5&nbsp;mm arm formed into a wave so each pack seats in its own trough.',
         blurb='The waveform indexes the facings. Every pack sits in its own trough at a consistent pitch, '
               'so the run stays evenly spaced as it sells down instead of bunching at the tip.',
         uses=['Confectionery and snacking', 'Beauty and cosmetics', 'Stationery and small goods']),
]

FINISHES = [
    dict(name='Chrome', tone='#c9ced3',
         blurb='Bright mirror finish. The retail default — reads clean under store lighting and hides '
               'handling marks.'),
    dict(name='Nickel', tone='#b6b0a4',
         blurb='Softer, warmer lustre with strong corrosion resistance. Common on premium and optical '
               'fixtures.'),
    dict(name='Zinc', tone='#9aa0a6',
         blurb='Sacrificial galvanic protection. The value option for stockroom, back-of-house and damp '
               'environments.'),
    dict(name='Powder coated', tone='#26262a',
         blurb='Any RAL or Pantone colour, matt or gloss. Used for brand-matched fixtures and '
               'shop-in-shop builds.'),
]

STATS = [
    dict(value=18, suffix='+', label='Years manufacturing', sub='Founded 2008'),
    dict(value=6000, suffix='+', label='m² of factory floor', sub='Zhejiang, China'),
    dict(value=100000, suffix='+', label='Hooks per day', sub='Peak output'),
    dict(value=20, suffix='+', label='Countries served', sub='Four continents'),
]

MACHINES = [
    dict(n='30+', label='Stamping machines', img='assets/img/factory/stamping-hall',
         copy='Clips, ticket plates and sole plates are stamped in-house from coil, so clip geometry and '
              'wire forming stay under one roof and one tolerance.'),
    dict(n='30+', label='Wire forming machines', img='assets/img/factory/wireform-hall',
         copy='CNC wire formers run the arm geometry — lengths, U-bends, waveforms and ball stubs — with '
              'repeatable bend radii across production runs.'),
    dict(n='30+', label='Welding machines', img='assets/img/factory/welding-hall',
         copy='Dedicated welders join arm to clip and ball to stub. This joint is where cheap hooks fail, '
              'so it gets dedicated capacity rather than shared time.'),
    dict(n='1,500–2,000', label='m² of warehousing', img='assets/img/factory/warehouse',
         copy='Raw sheet and wire held in depth, plus finished-goods buffer stock, so a repeat order is a '
              'shipping decision rather than a production queue.'),
]

PROCESS = [
    dict(step='01', name='Raw material', img='assets/img/factory/raw-wire',
         copy='Steel wire and sheet held in stock by gauge. Buying in depth is what lets us quote a lead '
              'time honestly instead of quoting the mill’s.'),
    dict(step='02', name='Stamping', img='assets/img/factory/stamping-operator',
         copy='Clip bodies, price-tag plates and mounting backs blanked and formed on 30+ presses against '
              'hardened tooling.'),
    dict(step='03', name='Wire forming', img='assets/img/factory/wireform-machine',
         copy='Automatic formers cut and bend the arm — length, U-loop, wave, ball stub — to the drawing, '
              'run after run.'),
    dict(step='04', name='Welding', img='assets/img/factory/welding-line',
         copy='Arm-to-clip and ball-to-stub joints welded on dedicated machines, then pull-checked before '
              'the batch moves on.'),
    dict(step='05', name='Surface finish', img='assets/img/factory/plated-parts',
         copy='Chrome, nickel, zinc or powder coat to your specification, including brand-matched RAL and '
              'Pantone colours.'),
    dict(step='06', name='QC and assembly', img='assets/img/factory/assembly-bench',
         copy='Dimensional and finish inspection, price-tag holder fitting, and any private-label carding '
              'or bagging.'),
    dict(step='07', name='Packing and despatch', img='assets/img/factory/warehouse-2',
         copy='Cartoned to your count, private-labelled if required, and staged for consolidation or '
              'direct container loading.'),
]

CUSTOM = [
    dict(title='Draw it to your spec',
         copy='Dimensions, shape and load capacity worked from your drawing, a physical sample, or a photo '
              'of the fixture it has to live on.'),
    dict(title='Finish it to your brand',
         copy='Chrome, nickel and zinc plating, or powder coat in any RAL or Pantone — matched to the '
              'fixture, not to what happens to be on the line.'),
    dict(title='Pack it as your own',
         copy='Private label, custom carding, poly-bagging and carton counts. The hook can arrive ready '
              'for your shelf, under your name.'),
    dict(title='Prove it before you commit',
         copy='Fast prototyping and in-house mould development, so a small trial run can be proved out '
              'before it becomes a container.'),
]

COMPANY = dict(
    brand='HCGretail',
    parent='Wuyi Hongchanggu Hardware Products Co., Ltd.',
    founded=2008,
    address='No. 1, Building 13, Qingchuang Zhigu Industrial Park, No. 29 Yingchun Road, '
            'Baihuashan Industrial Zone, Zhejiang, China',
    email='sales@hcgretail.com',
    phone='+1 (000) 000-0000',
)

REGIONS = ['North America', 'South America', 'Europe', 'The Middle East', 'Southeast Asia']


# ------------------------------------------------------------------- assembly
def build():
    rows = read_sheet()
    with open(os.path.join(ROOT, 'build', 'images.json'), encoding='utf-8') as fh:
        images = json.load(fh)

    style_by = {s['slug']: s for s in STYLES}
    system_by = {s['slug']: s for s in SYSTEMS}
    products = []

    for st in STYLES:
        for sy in SYSTEMS:
            sku = '%s-%s' % (sy['code'], st['code'])
            slug = sku.lower()
            products.append(dict(
                sku=sku, slug=slug, kind='matrix',
                system=sy['slug'], style=st['slug'],
                name='%s %s' % (sy['short'], st['name']),
                lede=st['lede'],
                card_desc='%s on a %s.' % (st['short'], sy['back']), blurb=st['blurb'], uses=sy['uses'],
                specs=parse_specs(rows[st['row'] + 1].get(sy['col'], '')),
                images=images.get(slug, []),
                url='products/%s/%s/' % (sy['slug'], slug),
            ))

    for sp in SPECIALTY:
        col, r = sp['cell']
        products.append(dict(
            sku=rows[r + 1][col], slug=sp['slug'], kind='specialty',
            system='specialty', style=None, name=sp['name'],
            lede=sp['lede'], blurb=sp['blurb'], uses=sp['uses'],
            card_desc=sp['lede'],
            specs=parse_specs(rows[r + 2].get(col, '')),
            images=images.get(sp['slug'], []),
            url='products/specialty/%s/' % sp['slug'],
        ))

    by_slug = {p['slug']: p for p in products}
    for sy in SYSTEMS:
        sy['products'] = [p for p in products if p['system'] == sy['slug']]
    for st in STYLES:
        st['products'] = [p for p in products if p['style'] == st['slug']]

    return dict(systems=SYSTEMS, styles=STYLES, products=products, by_slug=by_slug,
                system_by=system_by, style_by=style_by, specialty=SPECIALTY,
                finishes=FINISHES, stats=STATS, machines=MACHINES, process=PROCESS,
                custom=CUSTOM, company=COMPANY, regions=REGIONS)


if __name__ == '__main__':
    d = build()
    print('products:', len(d['products']))
    print('with images:', sum(1 for p in d['products'] if p['images']))
    print('shots:', sum(len(p['images']) for p in d['products']))
    print('no images:', [p['sku'] for p in d['products'] if not p['images']])
    for s in d['by_slug']['cb-sx-01']['specs']:
        print('  %-24s %-8s %s' % (s['label'], s['unit'], ' / '.join(s['options'])))
