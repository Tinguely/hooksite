/* HCGretail — interaction layer. Vanilla, no dependencies. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ------------------------------------------------------------- reveals */
  function reveals() {
    var els = $$('[data-reveal], [data-clip]');
    if (reduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -9% 0px', threshold: 0.08 });

    els.forEach(function (el) {
      // Stagger siblings that share a parent group.
      var group = el.closest('[data-stagger]');
      if (group && !el.style.getPropertyValue('--i')) {
        var kids = $$('[data-reveal]', group);
        el.style.setProperty('--i', Math.min(kids.indexOf(el), 11));
      }
      io.observe(el);
    });
  }

  /* --------------------------------------------------- split display type */
  function splitWords() {
    $$('[data-words]').forEach(function (el) {
      if (el.dataset.split) return;
      el.dataset.split = '1';
      var html = el.innerHTML.split(/(<[^>]+>)/);
      var out = '', i = 0;
      html.forEach(function (chunk) {
        if (chunk.charAt(0) === '<') { out += chunk; return; }
        chunk.split(/(\s+)/).forEach(function (w) {
          if (!w.trim()) { out += w; return; }
          out += '<span class="wordfx"><span style="--w:' + (i++) + '">' + w + '</span></span>';
        });
      });
      el.innerHTML = out;
    });
  }

  /* -------------------------------------------------------------- header */
  function header() {
    var hdr = $('.hdr');
    if (!hdr) return;
    var last = 0;
    function onScroll() {
      var y = window.scrollY;
      hdr.classList.toggle('is-stuck', y > 8);
      if (!document.body.classList.contains('nav-open')) {
        hdr.classList.toggle('is-hidden', y > 320 && y > last + 4);
      }
      last = y;
      var bar = $('.progress');
      if (bar) {
        var max = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.transform = 'scaleX(' + (max > 0 ? y / max : 0) + ')';
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Desktop mega menus
    $$('.nav-item.has-mega').forEach(function (item) {
      var close;
      function open(state) {
        clearTimeout(close);
        if (state) $$('.nav-item.is-open').forEach(function (o) { if (o !== item) o.classList.remove('is-open'); });
        item.classList.toggle('is-open', state);
      }
      item.addEventListener('mouseenter', function () { open(true); });
      item.addEventListener('mouseleave', function () { close = setTimeout(function () { open(false); }, 120); });
      item.addEventListener('focusin', function () { open(true); });
      item.addEventListener('focusout', function (e) {
        if (!item.contains(e.relatedTarget)) open(false);
      });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') $$('.nav-item.is-open').forEach(function (o) { o.classList.remove('is-open'); });
    });

    // Mobile drawer
    var burger = $('.burger');
    if (burger) {
      burger.addEventListener('click', function () {
        var open = document.body.classList.toggle('nav-open');
        burger.setAttribute('aria-expanded', String(open));
        hdr.classList.remove('is-hidden');
      });
    }
    $$('.dsec > button').forEach(function (b) {
      b.addEventListener('click', function () {
        var sec = b.parentElement;
        var open = sec.classList.toggle('is-open');
        b.setAttribute('aria-expanded', String(open));
      });
    });
  }

  /* ---------------------------------------------------------- accordions */
  function accordions() {
    $$('.acc-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var acc = btn.closest('.acc');
        var open = acc.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', String(open));
      });
    });
  }

  /* ---------------------------------------------------------- count-ups */
  function counters() {
    var els = $$('[data-count]');
    if (!els.length) return;
    if (reduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.textContent = fmt(+el.dataset.count); });
      return;
    }
    function fmt(n) { return n.toLocaleString('en-US'); }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var el = e.target, target = +el.dataset.count, t0 = null;
        io.unobserve(el);
        (function tick(ts) {
          if (t0 === null) t0 = ts;
          var p = Math.min((ts - t0) / 1500, 1);
          var eased = 1 - Math.pow(1 - p, 3);
          el.textContent = fmt(Math.round(target * eased));
          if (p < 1) requestAnimationFrame(tick);
        })(performance.now());
      });
    }, { threshold: 0.4 });
    els.forEach(function (el) { el.textContent = '0'; io.observe(el); });
    window.fmtCount = fmt;
  }

  /* --------------------------------------------------------------- rails */
  function rails() {
    $$('[data-rail]').forEach(function (rail) {
      var prev = $('[data-rail-prev]', rail.parentElement) || $('[data-rail-prev="' + rail.id + '"]');
      var next = $('[data-rail-next]', rail.parentElement) || $('[data-rail-next="' + rail.id + '"]');
      var scope = rail.closest('section') || document;
      prev = prev || $('[data-rail-prev]', scope);
      next = next || $('[data-rail-next]', scope);

      function step() {
        var first = rail.firstElementChild;
        return first ? first.getBoundingClientRect().width + 20 : 320;
      }
      function sync() {
        if (!prev || !next) return;
        prev.disabled = rail.scrollLeft < 6;
        next.disabled = rail.scrollLeft > rail.scrollWidth - rail.clientWidth - 6;
      }
      if (prev) prev.addEventListener('click', function () { rail.scrollBy({ left: -step(), behavior: 'smooth' }); });
      if (next) next.addEventListener('click', function () { rail.scrollBy({ left: step(), behavior: 'smooth' }); });
      rail.addEventListener('scroll', sync, { passive: true });
      window.addEventListener('resize', sync);
      sync();

      // Pointer drag
      var down = false, sx = 0, sl = 0, moved = 0;
      rail.addEventListener('pointerdown', function (e) {
        if (e.pointerType === 'touch') return;
        down = true; moved = 0; sx = e.clientX; sl = rail.scrollLeft;
      });
      rail.addEventListener('pointermove', function (e) {
        if (!down) return;
        var d = e.clientX - sx;
        moved = Math.max(moved, Math.abs(d));
        if (moved > 5) rail.classList.add('is-dragging');
        rail.scrollLeft = sl - d;
      });
      ['pointerup', 'pointerleave', 'pointercancel'].forEach(function (ev) {
        rail.addEventListener(ev, function () {
          down = false;
          setTimeout(function () { rail.classList.remove('is-dragging'); }, 0);
        });
      });
    });
  }

  /* ------------------------------------------------------------- gallery */
  function gallery() {
    var main = $('.gal-main');
    if (!main) return;
    var slides = $$('img', main);
    var thumbs = $$('.gal-thumb');
    var idx = 0;

    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) { s.classList.toggle('is-active', n === idx); });
      thumbs.forEach(function (t, n) {
        t.classList.toggle('is-active', n === idx);
        t.setAttribute('aria-selected', String(n === idx));
      });
      if (lbImg && lb.classList.contains('is-open')) paint();
    }
    thumbs.forEach(function (t, n) {
      t.addEventListener('click', function () { show(n); });
      t.addEventListener('mouseenter', function () { show(n); });
    });

    // Lightbox
    var lb = $('.lb'), lbImg = lb && $('img', lb), count = lb && $('.lb-count');
    if (!lb) return;
    var full = slides.map(function (s) { return s.dataset.full || s.currentSrc || s.src; });

    function paint() {
      lbImg.src = full[idx];
      lbImg.alt = slides[idx].alt;
      if (count) count.textContent = (idx + 1) + ' / ' + full.length;
    }
    function open() { paint(); lb.classList.add('is-open'); document.body.style.overflow = 'hidden'; }
    function close() { lb.classList.remove('is-open'); document.body.style.overflow = ''; }

    main.addEventListener('click', open);
    $('.lb-close', lb).addEventListener('click', close);
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    $('.lb-prev', lb).addEventListener('click', function () { show(idx - 1); });
    $('.lb-next', lb).addEventListener('click', function () { show(idx + 1); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    show(0);
  }

  /* -------------------------------------------------------------- finder */
  function finder() {
    var grid = $('[data-finder]');
    if (!grid) return;
    var cards = $$('.card', grid);
    var out = $('[data-finder-count]');
    var empty = $('[data-finder-empty]');
    var state = {};

    function apply(animate) {
      var shown = 0;
      cards.forEach(function (card) {
        var ok = Object.keys(state).every(function (k) {
          return !state[k] || card.dataset[k] === state[k];
        });
        card.classList.toggle('is-hidden', !ok);
        card.classList.remove('is-shown');
        if (ok) {
          shown++;
          if (animate && !reduced) {
            card.style.animationDelay = Math.min(shown * 22, 260) + 'ms';
            card.classList.add('is-shown');
          }
        }
      });
      if (out) out.textContent = shown;
      if (empty) empty.hidden = shown > 0;

      var q = Object.keys(state).filter(function (k) { return state[k]; })
        .map(function (k) { return k + '=' + state[k]; }).join('&');
      history.replaceState(null, '', q ? '?' + q : location.pathname);
    }

    $$('.fbtn[data-filter]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var key = btn.dataset.filter, val = btn.dataset.value;
        state[key] = state[key] === val ? '' : val;
        $$('.fbtn[data-filter="' + key + '"]').forEach(function (b) {
          b.setAttribute('aria-pressed', String(b.dataset.value === state[key]));
        });
        apply(true);
      });
    });
    $$('[data-filter-clear]').forEach(function (b) {
      b.addEventListener('click', function () {
        state = {};
        $$('.fbtn[data-filter]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        apply(true);
      });
    });

    // Hydrate from the query string so filtered views are linkable.
    new URLSearchParams(location.search).forEach(function (v, k) {
      var btn = $('.fbtn[data-filter="' + k + '"][data-value="' + v + '"]');
      if (btn) { state[k] = v; btn.setAttribute('aria-pressed', 'true'); }
    });
    apply(false);
  }

  /* ---------------------------------------------------------------- form */
  function quoteForm() {
    var form = $('[data-quote]');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var lines = [];
      data.forEach(function (v, k) {
        if (!String(v).trim()) return;
        var i = lines.findIndex(function (l) { return l.k === k; });
        if (i > -1) lines[i].v.push(v); else lines.push({ k: k, v: [v] });
      });
      var body = lines.map(function (l) {
        return l.k.replace(/_/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); }) +
          ': ' + l.v.join(', ');
      }).join('\n');
      var to = form.dataset.quote;
      window.location.href = 'mailto:' + to + '?subject=' +
        encodeURIComponent('Quote request — HCGretail') + '&body=' + encodeURIComponent(body);
      var note = $('[data-quote-note]', form);
      if (note) note.hidden = false;
    });

    // Pre-fill the SKU field when arriving from a product page.
    var sku = new URLSearchParams(location.search).get('sku');
    var field = $('[name="products"]', form);
    if (sku && field && !field.value) field.value = sku;
  }

  /* -------------------------------------------------------------- parallax */
  function parallax() {
    var els = $$('[data-parallax]');
    if (!els.length || reduced) return;
    var ticking = false;
    function frame() {
      var vh = window.innerHeight;
      els.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var p = (r.top + r.height / 2 - vh / 2) / vh;
        el.style.transform = 'translate3d(0,' + (p * (+el.dataset.parallax || 14) * -1) + 'px,0)';
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(frame); }
    }, { passive: true });
    frame();
  }

  /* ---------------------------------------------------------------- init */
  function init() {
    splitWords();
    reveals();
    header();
    accordions();
    counters();
    rails();
    gallery();
    finder();
    quoteForm();
    parallax();
    document.documentElement.classList.add('js-ready');
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
