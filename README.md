# HCGretail — retail display hook sales site

A static, generated marketing and specification site for HCGretail, the North American office of
Wuyi Hongchanggu Hardware Products Co., Ltd.

Every page is generated from the two source files in `new content/`, so the published
specifications can never drift from the master product list.

## Source of truth

| Source | Feeds |
| --- | --- |
| `new content/Hook product list.xlsx` | All part codes and every specification value |
| `new content/Product picture/**` | All 139 product photographs |
| `new content/公司介绍0613.pptm` | Company narrative, statistics, factory photography |

`build/data.py` reads the spreadsheet at build time and normalises it: Chinese full-width colons
are split off, labels are mapped to English retail terminology (`lenth` → Length, `surface
handling` → Surface finish), and slash-separated values become selectable option chips. Editorial
copy lives alongside that data in the same module.

## Catalogue structure

The 45 products are a 7 × 5 matrix plus 10 standalone fixtures:

- **5 mounting systems** — Slatwall (`CB`), Pegboard (`DB`), Tube snap (`FG`),
  Wire grid bow clip (`WJ-SG`), Wire grid long strip (`WJ-DG`)
- **7 hook styles** — Single wire (`DX-01`), Double wire + PVC tag (`SX-01`), Double wire + metal
  tag (`SX-02`), U wire (`UX-01`), U triple + PVC tag (`USX-01`), U triple + metal tag (`USX-02`),
  Ball hook (`DZ-01`)
- **10 specialty fixtures** — display stand, hat, shoe, eyeglass, towel, sports ball rack, power
  tool, razor, promotion basket, wave hook

The site lets a buyer drill in from either axis: pick the wall (`/products/<system>/`) or pick the
geometry (`/styles/<style>/`), and both converge on the same 45 specification pages.

### Products without photography

Eight matrix codes exist in the spreadsheet but have no photo folder: `FG-UX-01`, `FG-USX-02`,
`DB-USX-02`, `WJ-SG-DZ-01`, `WJ-SG-UX-01`, `WJ-SG-USX-01`, `WJ-SG-USX-02`, `WJ-DG-USX-02`. Their
pages render a "made to order" panel that cross-links to the same geometry on a system that does
have photography. Drop folders into `new content/Product picture/` and rebuild to fill them in.

## Building

```sh
python build/optimize.py   # 429 MB of JPEGs -> 18 MB of WebP at 440 / 900 / 1600 px
python build/gen.py        # renders 64 HTML pages + sitemap.xml
python build/verify.py     # asserts every href, src and srcset resolves on disk
```

`optimize.py` skips derivatives that already exist, so reruns are cheap. `gen.py` deletes and
recreates the generated directories on every run — do not hand-edit output HTML, edit the
generator.

`verify.py` exits non-zero if any reference is broken, any template token is left unsubstituted,
or any optimised photograph is not referenced by at least one page.

## Layout

```
index.html                              home
products/                               finder — filter by system and style
products/<system>/                      5 mounting system pages
products/<system>/<sku>/                35 matrix specification pages
products/specialty/                     specialty overview
products/specialty/<slug>/              10 specialty specification pages
styles/<style>/                         7 hook style pages
capabilities/  custom/  about/  contact/
assets/css/site.css                     design system
assets/js/site.js                       interaction layer (vanilla, no dependencies)
assets/img/                             generated WebP derivatives
build/                                  data, generator, image pipeline, verifier
```

## Design

White editorial canvas, oversized Archivo display type, Inter for body copy, and a single
vermilion accent (`--accent: #d33f22`). Product photography is studio-on-white, so it sits directly
on the page ground with no card chrome.

Interaction is progressive — the page is fully readable with JavaScript disabled. `site.js` adds
scroll reveals, the mega menu and mobile drawer, count-up statistics, draggable card rails, the
product gallery and lightbox, the catalogue filter (which reflects state into the query string so
filtered views are linkable), and the quote form's `mailto:` composition. Everything is disabled
under `prefers-reduced-motion`.

## Contact details

`build/data.py` → `COMPANY`. The phone number is still a placeholder; the email
(`sales@hcgretail.com`) should be confirmed before launch. Change them there and rebuild rather
than editing HTML.
