# Hook Business — Landing Site

Single-page wholesale hook distributor website targeting the US retail sector.
Dark/gold premium aesthetic. No frameworks, no build step — plain HTML, CSS, and vanilla JS.

---

## File Structure

```
hooksite/
├── index.html                  # Single-page site (all sections)
├── style.css                   # All styles (Tailwind overrides + custom)
├── script.js                   # Animations, mobile menu, product filter, form stub
└── siterip/
    ├── alibaba/
    │   └── images/             # Product photos and background images in use
    └── 1688/
        └── images/             # Additional product thumbnails (reference only)
```

---

## Tech Stack

| Dependency | Version | How loaded |
|---|---|---|
| Tailwind CSS | Play CDN | `<script src="https://cdn.tailwindcss.com">` |
| GSAP | 3.12.2 | cdnjs CDN |
| GSAP ScrollTrigger | 3.12.2 | cdnjs CDN |
| Font Awesome | 6.4.0 | cdnjs CDN |
| Cormorant Garamond | — | Google Fonts |
| Montserrat | — | Google Fonts |

No npm, no bundler. Open `index.html` directly in a browser or serve from any static host.

---

## Sections

| ID | Section | Notes |
|---|---|---|
| `#home` | Hero | Full-viewport header, two CTAs |
| `#about` | About | Single-column text, brand copy |
| *(no id)* | Stats band | Parallax background, count-up numbers |
| `#products` | Products | 9 product cards, filterable by category |
| `#distribution` | Distribution | 4-step process + 4 info panels |
| `#gallery` | In Application | 4-panel product photo grid |
| `#contact` | Contact | Info block + inquiry form |
| *(footer)* | Footer | Nav links, contact details, legal |

---

## Branding — What Needs Updating

Search for `TODO` in `index.html` and `script.js` to find every placeholder.
Key items:

| Placeholder | Location | Replace with |
|---|---|---|
| `[Brand Name]` | `<title>`, footer | Actual company name |
| `[Company Name]` | `data-brand-text`, footer copyright | Legal company name |
| `ZT` | `data-brand-short`, loader, nav | Brand initials or short wordmark |
| `info@yourdomain.com` | Contact section, footer | Real email |
| `sales@yourdomain.com` | Contact section | Real sales email |
| `+1 (000) 000-0000` | Contact section, footer | Real phone number |
| `[Business Address Line 1]` | Contact section | Real address |
| `[City, State, ZIP]` | Contact section, footer | Real location |
| Monday–Friday hours | Contact section | Real business hours |
| Social links (`href="#"`) | Contact section | Real LinkedIn / other URLs |

In `script.js`:
```js
const BRAND = {
  name:  "[Company Name]",   // ← update
  short: "ZT",               // ← update
};
```

---

## Product Catalog

9 products across 3 filter categories. Each card lives in `index.html` inside `#productGrid`
and carries a `data-category` attribute used by the JS filter.

| Category (`data-category`) | Products |
|---|---|
| `gridwall` | Metal Wire Gridwall Hooks, Pegboard Wire Hooks, Gridwall Hooks with Price Tag Holder |
| `slatwall` | Slatwall Display Hooks, Jewelry Slatwall Hooks, Adjustable Chrome Display Hook |
| `tube` | 7-Ball Tube Bar Hooks, Square Tube Garment Hooks, Heavy-Duty Crossbar Hook |

### Adding a New Product

Copy any existing `.product-card` block and update:
- `data-category` — one of `gridwall`, `slatwall`, `tube` (or add a new tab)
- `<img src>` — path to product image
- `<h3>` — product name
- `<p>` — description
- `<tbody>` spec table rows

To add a new filter category, add a `<button data-tab="newcategory">` to `#productTabs`
in `index.html` — the JS in `initProductFilter()` handles it automatically.

---

## Images

All product images are stored locally in `siterip/alibaba/images/`.
Paths in `index.html` are relative (e.g. `./siterip/alibaba/images/filename.jpg`).

### Images Currently in Use

| Used for | File |
|---|---|
| Hero + stats band background | `TB1k1Ive3oQMeJjy0FoXXcShVXa-1200-280.png` |
| Product 1 — Gridwall Hooks | `Metal-Display-Grid-Mesh-Display-Hooks-in.jpg_480x480.jpg` |
| Product 2 — Pegboard Hooks | `Custom-6-Inch-Metal-Wire-Display-Hooks.jpg_480x480.jpg` |
| Product 3 — Gridwall + Price Tag | `Convenient-Accessories-Goods-Display-Grid-Wall-Wire.jpg` |
| Product 4 — Slatwall Hooks | `Metal-Hanging-Hook-Slatwall-Display-Hook-Supermarket.jpg` |
| Product 5 — Jewelry Slatwall | `Chrome-Metal-Display-Slatwall-Hook-for-Jewelry.jpg` |
| Product 6 — Adjustable Chrome Hook | `Single-Hook-Adjustable-Chrome-Plated-Smooth-Polished.jpg_480x480.jpg` |
| Product 7 — 7-Ball Tube Bar | `Hot-Sale-Retail-7Balls-Hanging-Metal-Tube.jpg` |
| Product 8 — Square Tube Garment | `Supermarket-Metal-Chrome-Garment-Store-square-Tube.jpg` |
| Product 9 — Heavy-Duty Crossbar | `Heavy-Duty-Luxury-Metal-Steel-Hanging-Crossbar.jpg` |
| Gallery panel 1 | `Best-Sale-Supermarket-Metal-Chrome-Display-Hook.jpg_350x350.jpg` |
| Gallery panel 2 | `Chrome-Metal-Wall-Grid-Display-Hook-with.jpg` |
| Gallery panel 3 | `Supermarket-Square-Tube-Bar-Clothes-Hanging-Display.jpg` |
| Gallery panel 4 | `2023-Most-Popular-Steel-Metal-Grid-Display.jpg_350x350.jpg` |

### Replacing Images

1. Drop the new file into `siterip/alibaba/images/` (or any path under the site root).
2. Update the `src` attribute on the corresponding `<img>` tag in `index.html`.
3. Update the `alt` text to describe the new image.

When deploying, include the entire `siterip/` folder — it contains all assets the site loads.
If you move images to a different directory (e.g. `assets/images/`), do a find-and-replace
on `./siterip/alibaba/images/` in `index.html`.

---

## Contact Form

The form at `#contact` is a stub. It currently shows an `alert()` on submit.
To make it functional, choose one of these approaches and update `initContactForm()` in `script.js`:

**Option A — Formspree (simplest)**
```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST" id="contactForm">
```
Remove the `e.preventDefault()` call in `script.js`.

**Option B — Netlify Forms**
Add `data-netlify="true"` to the `<form>` tag and remove the JS submit handler.

**Option C — EmailJS**
```js
emailjs.send("SERVICE_ID", "TEMPLATE_ID", {
  firstName: form.firstName.value,
  email:     form.email.value,
  message:   form.message.value,
});
```

**Option D — Custom backend**
Set `action="https://yourapi.com/contact"` and `method="POST"` on the form,
or replace the stub with a `fetch()` call.

---

## Animations

Powered by GSAP + ScrollTrigger. Gracefully degrades when:
- GSAP fails to load (CDN down) — `showFallback()` makes all elements visible
- `prefers-reduced-motion` is set — all animations are skipped

### Animation inventory

| Animation | Trigger | Elements |
|---|---|---|
| Loader + hero reveal | Page load | `.loader-text`, `.loader`, `.reveal-on-load` |
| Slide in from left | Scroll (top 80%) | `[data-reveal="left"]` |
| Slide in from right | Scroll (top 80%) | `[data-reveal="right"]` |
| Stagger fade up | Scroll (top 75%) | `.product-card`, `.dist-step` |
| Hero parallax | Scroll scrub | `.hero-img` |
| Count-up numbers | Scroll (top 85%) | `[data-count]` |

### Count-up numbers

To change a stat, update `data-count` on the `<span>` in the stats band:
```html
<span data-count="500">0</span>  <!-- animates 0 → 500 -->
```

### Known fix — desktop scroll triggers

`ScrollTrigger.refresh()` is called inside the loader timeline's `onComplete` callback.
This forces ScrollTrigger to recalculate all element positions after the loader overlay
is removed from the DOM. Without this, triggers measured during the loader phase use
stale layout positions and don't fire on desktop.

---

## CSS Architecture

`style.css` provides:
- CSS custom properties (`--bg`, `--fg`, `--gold`) as the single source of color truth
- Tailwind utility class overrides (`!important`) for brand colors
- Component classes: `.product-card`, `.spec-table`, `.dist-step`, `.dist-step-icon`,
  `.glass-panel`, `.form-input`, `.gold-divider`, `.nav-link`, `.todo-banner`
- Overflow lockdown: `overflow-x: hidden` on both `html` and `body`;
  `overflow-x: clip` on `section`, `header`, `footer`, `main` to prevent
  GSAP x-axis animations from leaking horizontal scroll

### Brand colors

| Variable | Hex | Usage |
|---|---|---|
| `--gold` / `brand.gold` | `#C5A059` | Accents, borders, CTAs |
| `--bg` / `brand.dark` | `#121212` | Page background |
| `brand.gray` | `#2A2A2A` | Alternate section background |
| `--fg` / `brand.light` | `#F5F5F0` | Body text |

To change the gold accent, update `--gold` in `:root` in `style.css` AND
`brand.gold` in the `tailwind.config` block in `index.html`.

---

## Deployment

The site is fully static. Any static host works:

**Netlify / Vercel**
Drag and drop the `hooksite/` folder, or connect the GitHub repo.
Publish directory: `/` (root). No build command needed.

**GitHub Pages**
Push to a `gh-pages` branch or enable Pages from the repo's main branch.

**Self-hosted / VPS**
Copy all files to the web root. No server-side processing required.

**Important:** The `siterip/` folder must be included in the deployment —
it contains all the product images the site loads. The HTML and siterip folder
must be at the same directory level.

---

## Git Branch

Active development branch: `claude/professional-hook-business-site-nADKq`

Commit history summary:
1. `c16c8d4` — Initial build from Obsidian Gold template
2. `f871a29` — Siterip assets added
3. `b336cf7` — All placeholder content replaced with real product data
4. `ad83d20` — Image scaling fixes; distribution panel expanded to 4 columns
5. `d17fb8f` — Stripped all supplier/platform references; rewritten as US distributor
6. `44bcb84` — Removed quality assurance image overlay
7. `c8dc7a2` — Removed about section image entirely
8. `3788274` — Fixed desktop scroll trigger timing; locked down mobile horizontal overflow

---

## Outstanding TODOs (priority order)

1. **Brand identity** — company name, logo asset, brand initials
2. **Contact details** — address, phone, emails, business hours
3. **Form backend** — wire contact form to Formspree / Netlify / custom endpoint
4. **Social links** — LinkedIn and any other platforms
5. **MOQ confirmation** — verify all spec table figures with supplier
6. **Product photography** — replace siterip images with owned/licensed photos
7. **Privacy Policy / Terms of Sale** — pages linked in footer
8. **Meta tags** — update `<title>` and `<meta name="description">` once brand is set
9. **Favicon** — add `<link rel="icon">` once logo is available
