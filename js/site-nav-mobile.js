(function () {
  /**
   * Drawer nav when:
   * - viewport ≤ 1280px (links would clip on the glass pill bar), or
   * - browser zoom ≥ 125%, or
   * - desktop width but .nav-links still overflow horizontally.
   *
   * While open, #sitePrimaryNav is moved onto <body> so menu taps hit the panel
   * instead of the dimmed backdrop (fixed panel inside a short header fails on
   * iOS/WebKit hit-testing).
   */
  var DRAWER_MAX_PX = 1280;
  var ZOOM_MENU_MIN = 1.25;
  var drawerMq = window.matchMedia("(max-width: " + DRAWER_MAX_PX + "px)");

  function getBrowserZoom() {
    var vv = window.visualViewport;
    if (vv && typeof vv.scale === "number" && vv.scale > 0) {
      return vv.scale;
    }
    var ow = window.outerWidth;
    var iw = window.innerWidth;
    if (iw > 0 && ow > iw) {
      var ratio = ow / iw;
      if (ratio >= 1.05 && ratio <= 3) return ratio;
    }
    return 1;
  }

  function usesNavDrawer() {
    return (
      drawerMq.matches ||
      document.documentElement.classList.contains("site-nav-drawer-force")
    );
  }

  function closeExplorePanels(scope) {
    var root = scope || document;
    root.querySelectorAll(".nav-addons-wrap.is-open").forEach(function (wrap) {
      wrap.classList.remove("is-open");
      var panel = wrap.querySelector(".nav-addons-panel");
      var trigger = wrap.querySelector(".nav-addons-trigger");
      if (panel) panel.removeAttribute("hidden");
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function shouldForceDrawerForZoom() {
    if (drawerMq.matches) return false;
    return getBrowserZoom() >= ZOOM_MENU_MIN - 0.005;
  }

  function measureOverflowWithoutForce(nav) {
    if (drawerMq.matches || !nav) return false;
    var html = document.documentElement;
    var wasForced = html.classList.contains("site-nav-drawer-force");
    if (wasForced) html.classList.remove("site-nav-drawer-force");
    void nav.offsetWidth;
    var links = nav.querySelector(".nav-links");
    var overflow = !!(links && links.scrollWidth > links.clientWidth + 2);
    if (wasForced) html.classList.add("site-nav-drawer-force");
    return overflow;
  }

  function syncDrawerForce(nav) {
    // Don't measure the pill row while the list is portaled onto <body>.
    if (document.body.classList.contains("site-nav-open")) {
      return document.documentElement.classList.contains("site-nav-drawer-force");
    }
    var force =
      shouldForceDrawerForZoom() ||
      measureOverflowWithoutForce(nav || document.querySelector("nav.site-nav"));
    document.documentElement.classList.toggle("site-nav-drawer-force", force);
    return force;
  }

  function init() {
    var nav = document.querySelector("nav.site-nav");
    var btn = document.getElementById("siteNavMenuBtn");
    var links = document.getElementById("sitePrimaryNav");
    if (!nav || !btn || !links) return;

    var linksHome = links.parentElement;
    var backdrop = document.querySelector(".nav-drawer-backdrop");

    function positionAiOverlay() {
      var aiBtn = document.querySelector("nav.site-nav .nav-right .nav-ai");
      var overlay = document.querySelector(".hero-ai-overlay");
      if (!aiBtn || !overlay) return;

      var btnRect = aiBtn.getBoundingClientRect();
      var gap = 8;
      var anchorLeft = btnRect.left - gap;
      var centerY = btnRect.top + btnRect.height / 2;

      overlay.style.left = Math.round(anchorLeft) + "px";
      overlay.style.right = "auto";
      overlay.style.transform = "translate(-100%, -50%)";
      overlay.style.top = Math.round(centerY) + "px";
    }

    function positionAiMobileHint() {
      if (!window.matchMedia("(max-width: 560px)").matches) return;
      var aiBtn = document.querySelector("nav.site-nav .nav-right .nav-ai");
      var hint = document.querySelector(
        "nav.site-nav .nav-right .nav-ai-mobile-hint"
      );
      if (!aiBtn || !hint) return;

      var btnRect = aiBtn.getBoundingClientRect();
      var centerX = btnRect.left + btnRect.width / 2;

      hint.style.left = Math.round(centerX) + "px";
      hint.style.top = Math.round(btnRect.bottom + 10) + "px";
      hint.style.transform = "translateX(-50%)";
    }

    function mountDrawer(open) {
      if (open) {
        if (links.parentElement !== document.body) {
          document.body.appendChild(links);
        }
        links.classList.add("site-nav-drawer-panel");
      } else {
        links.classList.remove("site-nav-drawer-panel");
        if (linksHome && links.parentElement !== linksHome) {
          linksHome.appendChild(links);
        }
      }
    }

    function setMenuOpen(open) {
      if (open) {
        mountDrawer(true);
        nav.classList.add("site-nav-open");
        document.body.classList.add("site-nav-open");
      } else {
        closeExplorePanels(links);
        nav.classList.remove("site-nav-open");
        document.body.classList.remove("site-nav-open");
        mountDrawer(false);
      }
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (backdrop) {
        backdrop.setAttribute("aria-hidden", open ? "false" : "true");
      }
    }

    function closeMenu() {
      setMenuOpen(false);
    }

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (!usesNavDrawer()) return;
      setMenuOpen(!nav.classList.contains("site-nav-open"));
      positionAiOverlay();
      positionAiMobileHint();
    });

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        closeMenu();
      });
    }

    // Delegation stays valid after the list is moved to <body>.
    links.addEventListener("click", function (e) {
      if (!usesNavDrawer()) return;
      if (!document.body.classList.contains("site-nav-open")) return;

      var link = e.target.closest && e.target.closest("a[href]");
      if (!link || !links.contains(link)) return;

      var hrefAttr = link.getAttribute("href");
      if (!hrefAttr || hrefAttr === "#") {
        e.preventDefault();
        closeMenu();
        return;
      }

      var dest = link.href;

      // Let courses-catalog.js run first; then close and finish navigation.
      window.setTimeout(function () {
        if (e.defaultPrevented) {
          closeMenu();
          return;
        }

        closeMenu();

        if (hrefAttr.charAt(0) === "#") return;

        try {
          if (dest && dest !== window.location.href) {
            window.location.assign(dest);
          }
        } catch (_) {
          if (dest) window.location.href = dest;
        }
      }, 10);
    });

    links.querySelectorAll(".nav-addons-trigger").forEach(function (trigger) {
      trigger.addEventListener("click", function (e) {
        if (!usesNavDrawer()) return;
        e.stopPropagation();
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("site-nav-open")) {
        closeMenu();
        btn.focus();
      }
    });

    function onLayoutChange() {
      // Measure overflow only with the list back in the header.
      if (nav.classList.contains("site-nav-open") && !usesNavDrawer()) {
        closeMenu();
      } else if (!nav.classList.contains("site-nav-open")) {
        mountDrawer(false);
      }
      syncDrawerForce(nav);
      positionAiOverlay();
      positionAiMobileHint();
      if (!usesNavDrawer() && nav.classList.contains("site-nav-open")) {
        closeMenu();
      }
    }

    window.addEventListener("resize", onLayoutChange, { passive: true });
    drawerMq.addEventListener("change", onLayoutChange);
    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", onLayoutChange);
      window.visualViewport.addEventListener("scroll", onLayoutChange, {
        passive: true,
      });
    }

    onLayoutChange();
    window.requestAnimationFrame(onLayoutChange);
    window.addEventListener("scroll", positionAiMobileHint, { passive: true });
    window.addEventListener("load", onLayoutChange, { passive: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
