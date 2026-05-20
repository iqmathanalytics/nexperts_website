/**
 * Explore dropdown: hover on desktop (with close delay + gap bridge), click on mobile.
 */
(function () {
  function init() {
    document.querySelectorAll(".nav-addons-wrap").forEach(function (wrap) {
      if (wrap.dataset.nxAddonsInit) return;
      wrap.dataset.nxAddonsInit = "1";

      var btn = wrap.querySelector(".nav-addons-trigger");
      var panel = wrap.querySelector(".nav-addons-panel");
      if (!btn || !panel) return;

      var mq = window.matchMedia("(max-width: 1024px)");
      var closeTimer = null;
      var CLOSE_DELAY_MS = 220;

      function isDrawerMode() {
        return (
          mq.matches ||
          document.documentElement.classList.contains("site-nav-drawer-force")
        );
      }

      function syncPanelHidden() {
        if (isDrawerMode()) {
          panel.removeAttribute("hidden");
        } else {
          panel.hidden = !wrap.classList.contains("is-open");
        }
      }

      function close() {
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }
        wrap.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
        syncPanelHidden();
      }

      function open() {
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }
        wrap.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
        syncPanelHidden();
      }

      function scheduleClose() {
        if (closeTimer) clearTimeout(closeTimer);
        closeTimer = setTimeout(close, CLOSE_DELAY_MS);
      }

      function cancelClose() {
        if (closeTimer) {
          clearTimeout(closeTimer);
          closeTimer = null;
        }
      }

      function toggle() {
        if (wrap.classList.contains("is-open")) close();
        else open();
      }

      btn.addEventListener("click", function (e) {
        if (!isDrawerMode()) return;
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        toggle();
      });

      wrap.addEventListener("mouseenter", function () {
        if (isDrawerMode()) return;
        cancelClose();
        open();
      });

      wrap.addEventListener("mouseleave", function (e) {
        if (isDrawerMode()) return;
        var related = e.relatedTarget;
        if (related && wrap.contains(related)) return;
        scheduleClose();
      });

      panel.addEventListener("mouseenter", function () {
        if (isDrawerMode()) return;
        cancelClose();
        open();
      });

      panel.addEventListener("mouseleave", function (e) {
        if (isDrawerMode()) return;
        var related = e.relatedTarget;
        if (related && wrap.contains(related)) return;
        scheduleClose();
      });

      btn.addEventListener("keydown", function (e) {
        if (e.key === "Escape") close();
        if (e.key === "Enter" || e.key === " ") {
          if (isDrawerMode()) {
            e.preventDefault();
            toggle();
          }
        }
      });

      document.addEventListener("click", function (e) {
        if (!isDrawerMode()) return;
        if (!wrap.contains(e.target)) close();
      });

      mq.addEventListener("change", function () {
        close();
        syncPanelHidden();
      });

      syncPanelHidden();
      btn.setAttribute("aria-expanded", "false");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
