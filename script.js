(() => {
  "use strict";

  // TODO: Update brand info with actual company name and details
  const BRAND = {
    name:  "[Company Name]",
    short: "YK",
  };

  const prefersReducedMotion =
    window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches ?? false;

  const hasGSAP         = typeof window.gsap !== "undefined";
  const hasScrollTrigger = typeof window.ScrollTrigger !== "undefined";

  function applyBrand() {
    document.querySelectorAll("[data-brand-text]").forEach((el) => (el.textContent = BRAND.name));
    document.querySelectorAll("[data-brand-short]").forEach((el) => (el.textContent = BRAND.short));

    const yearEl = document.querySelector("[data-year]");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  }

  // -----------------------------------------------------------------------
  // Mobile menu
  // -----------------------------------------------------------------------
  function initMobileMenu() {
    const menuRoot    = document.getElementById("mobileMenu");
    const menuBtn     = document.getElementById("menuBtn");
    const menuCloseBtn = document.getElementById("menuCloseBtn");
    const panel       = menuRoot?.querySelector("[data-menu-panel]");
    const backdrop    = menuRoot?.querySelector("[data-menu-backdrop]");
    const menuLinks   = menuRoot?.querySelectorAll("[data-menu-link]") || [];

    let menuOpen = false;

    const lockScroll = (lock) => {
      document.documentElement.style.overflow = lock ? "hidden" : "";
    };

    const setA11y = (open) => {
      menuBtn?.setAttribute("aria-expanded", String(open));
    };

    const openMenu = () => {
      if (!menuRoot || !panel || !backdrop || menuOpen) return;
      menuOpen = true;
      setA11y(true);
      lockScroll(true);
      menuRoot.style.pointerEvents = "auto";

      if (!prefersReducedMotion && hasGSAP) {
        window.gsap.to(backdrop, { opacity: 1, duration: 0.25, ease: "power2.out" });
        window.gsap.to(panel, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out", overwrite: true });
      } else {
        backdrop.style.opacity = "1";
        panel.style.opacity    = "1";
        panel.style.transform  = "translateY(0)";
      }
    };

    const closeMenu = () => {
      if (!menuRoot || !panel || !backdrop || !menuOpen) return;
      menuOpen = false;
      setA11y(false);
      lockScroll(false);

      if (!prefersReducedMotion && hasGSAP) {
        window.gsap.to(backdrop, { opacity: 0, duration: 0.2, ease: "power2.out" });
        window.gsap.to(panel, {
          opacity: 0,
          y: -24,
          duration: 0.25,
          ease: "power2.in",
          onComplete: () => { menuRoot.style.pointerEvents = "none"; },
        });
      } else {
        backdrop.style.opacity   = "0";
        panel.style.opacity      = "0";
        panel.style.transform    = "translateY(-24px)";
        menuRoot.style.pointerEvents = "none";
      }
    };

    menuBtn?.addEventListener("click", openMenu);
    menuCloseBtn?.addEventListener("click", closeMenu);
    backdrop?.addEventListener("click", closeMenu);
    menuLinks.forEach((a) => a.addEventListener("click", closeMenu));
    window.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
  }

  // -----------------------------------------------------------------------
  // Navbar scroll behavior
  // -----------------------------------------------------------------------
  function initNavbarScroll() {
    const nav = document.getElementById("navbar");
    if (!nav) return;

    const onScroll = () => {
      if (window.scrollY > 50) nav.classList.add("bg-black/90", "backdrop-blur-md", "shadow-lg");
      else                      nav.classList.remove("bg-black/90", "backdrop-blur-md", "shadow-lg");
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // -----------------------------------------------------------------------
  // Product category filter tabs
  // -----------------------------------------------------------------------
  function initProductFilter() {
    const tabs = document.querySelectorAll(".tab-btn");
    const cards = document.querySelectorAll("#productGrid [data-category]");

    if (!tabs.length) return;

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const selected = tab.getAttribute("data-tab");

        // Update tab styles
        tabs.forEach((t) => {
          const isActive = t === tab;
          t.classList.toggle("bg-brand-gold",  isActive);
          t.classList.toggle("text-black",     isActive);
          t.classList.toggle("border-brand-gold", isActive);
          t.classList.toggle("text-white/60",  !isActive);
          t.classList.toggle("border-white/20", !isActive);
          t.setAttribute("aria-selected", String(isActive));
        });

        // Show/hide cards
        cards.forEach((card) => {
          const category = card.getAttribute("data-category");
          const visible  = selected === "all" || category === selected;

          if (visible) {
            card.style.display = "";
            if (!prefersReducedMotion && hasGSAP) {
              window.gsap.fromTo(card, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.35, ease: "power2.out" });
            }
          } else {
            card.style.display = "none";
          }
        });
      });
    });
  }

  // -----------------------------------------------------------------------
  // Contact form (non-functional stub — wire to backend)
  // -----------------------------------------------------------------------
  function initContactForm() {
    const form = document.getElementById("contactForm");
    if (!form) return;

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      // TODO: Replace this stub with actual form submission logic.
      // Options: Formspree, Netlify Forms, EmailJS, or a custom backend endpoint.
      alert("Thank you for your inquiry. We will be in touch within 1-2 business days.");
      form.reset();
    });
  }

  // -----------------------------------------------------------------------
  // Animations
  // -----------------------------------------------------------------------
  function showFallback() {
    document.querySelector(".loader")?.remove();
    document.querySelectorAll(".reveal-on-load").forEach((el) => {
      el.style.opacity   = "1";
      el.style.transform = "none";
    });
  }

  function initAnimations() {
    if (prefersReducedMotion || !hasGSAP) {
      showFallback();
      return;
    }

    if (hasScrollTrigger) {
      window.gsap.registerPlugin(window.ScrollTrigger);
    }

    // Loader + hero reveal
    const tl = window.gsap.timeline();
    tl.to(".loader-text",    { opacity: 1, y: 0, duration: 0.9, ease: "power2.out" })
      .to(".loader",         { y: "-100%", duration: 0.9, delay: 0.4, ease: "power4.inOut" })
      .to(".reveal-on-load", { opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: "power2.out" }, "-=0.15");

    if (!hasScrollTrigger) return;

    // Left/right reveals
    document.querySelectorAll('[data-reveal="left"]').forEach((el) => {
      window.gsap.from(el, {
        scrollTrigger: { trigger: el, start: "top 80%", toggleActions: "play none none reverse" },
        x: -50, opacity: 0, duration: 0.9, ease: "power3.out",
      });
    });

    document.querySelectorAll('[data-reveal="right"]').forEach((el) => {
      window.gsap.from(el, {
        scrollTrigger: { trigger: el, start: "top 80%", toggleActions: "play none none reverse" },
        x: 50, opacity: 0, duration: 0.9, delay: 0.1, ease: "power3.out",
      });
    });

    // Product cards
    window.gsap.from(".product-card", {
      scrollTrigger: { trigger: "#products", start: "top 75%" },
      y: 40, opacity: 0, duration: 0.7, stagger: 0.12, ease: "power2.out",
    });

    // Distribution steps
    window.gsap.from(".dist-step", {
      scrollTrigger: { trigger: "#distribution", start: "top 75%" },
      y: 30, opacity: 0, duration: 0.6, stagger: 0.1, ease: "power2.out",
    });

    // Hero parallax
    window.gsap.to(".hero-img", {
      scrollTrigger: { trigger: "#home", start: "top top", end: "bottom top", scrub: true },
      y: 90, scale: 1.08,
    });

    // Count-up stats
    document.querySelectorAll("[data-count]").forEach((el) => {
      const end = Number(el.getAttribute("data-count") || "0");
      const obj = { val: 0 };
      window.gsap.to(obj, {
        val: end,
        duration: 1.2,
        ease: "power1.out",
        snap: { val: 1 },
        onUpdate: () => { el.textContent = String(Math.round(obj.val)); },
        scrollTrigger: { trigger: el, start: "top 85%" },
      });
    });
  }

  // -----------------------------------------------------------------------
  // Boot
  // -----------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", () => {
    applyBrand();
    initMobileMenu();
    initNavbarScroll();
    initProductFilter();
    initContactForm();

    try {
      initAnimations();
    } catch {
      showFallback();
    }
  });
})();
