(function () {
  /** Tablet/phone drawer (normal zoom). Desktop drawer only at 125%+ zoom via JS class. */
  var DRAWER_MAX_PX = 1024;
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

  function closeExplorePanels(nav) {
    nav.querySelectorAll(".nav-addons-wrap.is-open").forEach(function (wrap) {
      wrap.classList.remove("is-open");
      var panel = wrap.querySelector(".nav-addons-panel");
      var trigger = wrap.querySelector(".nav-addons-trigger");
      if (panel) panel.removeAttribute("hidden");
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    });
  }

  function closeMenu(nav, btn) {
    closeExplorePanels(nav);
    nav.classList.remove("site-nav-open");
    document.body.classList.remove("site-nav-open");
    if (btn) {
      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Open menu");
    }
  }

  /** Force hamburger on desktop only when browser zoom is 125% or more. */
  function shouldForceDrawerForZoom() {
    if (drawerMq.matches) return false;
    return getBrowserZoom() >= ZOOM_MENU_MIN - 0.005;
  }

  function syncDrawerForce() {
    var force = shouldForceDrawerForZoom();
    document.documentElement.classList.toggle("site-nav-drawer-force", force);
    return force;
  }

  function init() {
    var nav = document.querySelector("nav.site-nav");
    var btn = document.getElementById("siteNavMenuBtn");
    if (!nav || !btn) return;

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
      var hint = document.querySelector("nav.site-nav .nav-right .nav-ai-mobile-hint");
      if (!aiBtn || !hint) return;

      var btnRect = aiBtn.getBoundingClientRect();
      var centerX = btnRect.left + btnRect.width / 2;

      hint.style.left = Math.round(centerX) + "px";
      hint.style.top = Math.round(btnRect.bottom + 10) + "px";
      hint.style.transform = "translateX(-50%)";
    }

    var backdrop = nav.nextElementSibling;
    if (!backdrop || !backdrop.classList.contains("nav-drawer-backdrop")) {
      backdrop = null;
    }

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      if (!usesNavDrawer()) return;
      var open = nav.classList.toggle("site-nav-open");
      document.body.classList.toggle("site-nav-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      positionAiOverlay();
      positionAiMobileHint();
    });

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        closeMenu(nav, btn);
      });
    }

    nav.querySelectorAll("#sitePrimaryNav a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (usesNavDrawer()) {
          closeMenu(nav, btn);
        }
      });
    });

    nav.querySelectorAll(".nav-addons-trigger").forEach(function (trigger) {
      trigger.addEventListener("click", function (e) {
        if (!usesNavDrawer()) return;
        e.stopPropagation();
      });
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("site-nav-open")) {
        closeMenu(nav, btn);
        btn.focus();
      }
    });

    function onLayoutChange() {
      syncDrawerForce();
      positionAiOverlay();
      positionAiMobileHint();
      if (!usesNavDrawer()) {
        closeMenu(nav, btn);
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
