/* Admin overlay — applies localStorage edits to the public site.
 *
 * Loaded by:
 *   - index.html   (catalog cards: name + description + per-brand order)
 *   - course_pages/*.html (sidebar: duration, next intake, price, original price)
 *
 * Storage key: nexperts_admin_v1   (written by /admin/)
 *
 * Safe to run when storage is empty — silently no-ops.
 */
(function () {
  "use strict";

  const STORAGE_KEY = "nexperts_admin_v1";

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const obj = JSON.parse(raw);
      return {
        courses: (obj && obj.courses) || {},
        card_order: (obj && obj.card_order) || {},
      };
    } catch (e) {
      return null;
    }
  }

  function setText(el, text) {
    if (!el || el.textContent === text) return;
    el.textContent = text;
  }

  function applyCatalogOverrides(state) {
    const cards = document.querySelectorAll(".cc[data-slug]");
    if (!cards.length) return;

    cards.forEach(card => {
      const slug = card.dataset.slug;
      const ov = state.courses[slug];
      if (!ov) return;
      if (ov.name) setText(card.querySelector(".cname2"), ov.name);
      if (ov.description) setText(card.querySelector(".cdesc2"), ov.description);
    });

    // Reorder cards within each brand-grid based on the saved order.
    const grids = document.querySelectorAll(".brand-grid");
    grids.forEach(grid => {
      const block = grid.closest(".brand-block");
      if (!block) return;
      const brand = block.dataset.brand;
      const desired = state.card_order[brand];
      if (!desired || !desired.length) return;

      const bySlug = {};
      Array.from(grid.children).forEach(child => {
        if (child.dataset && child.dataset.slug) bySlug[child.dataset.slug] = child;
      });

      // Append in desired order; keep any unknowns at the tail.
      desired.forEach(slug => {
        const node = bySlug[slug];
        if (node) {
          grid.appendChild(node);
          delete bySlug[slug];
        }
      });
      Object.values(bySlug).forEach(node => grid.appendChild(node));
    });
  }

  function applyDetailOverrides(state) {
    const path = (location.pathname || "").toLowerCase();
    const m = path.match(/\/course_pages\/([^/]+)\.html?$/);
    if (!m) return;
    const slug = decodeURIComponent(m[1]);
    const ov = state.courses[slug];
    if (!ov) return;

    // The detail-page <h1> uses rich markup (<br>, <em>) for typography —
    // leave it alone to avoid breaking the visual hierarchy. Name/description
    // edits flow to the catalog card on the landing page (where the same
    // course is identified by data-slug).
    if (ov.price) {
      const el = document.querySelector(".price");
      if (el) setText(el, ov.price);
    }
    if (ov.price_original) {
      const el = document.querySelector(".price-orig");
      if (el) setText(el, ov.price_original);
    }
    if (ov.duration) replaceMetaRow("Duration", ov.duration);
    if (ov.next_intake) replaceMetaRow("Next intake", ov.next_intake);
  }

  function replaceMetaRow(label, value) {
    document.querySelectorAll(".smeta-row").forEach(row => {
      const lbl = row.querySelector("span");
      if (lbl && lbl.textContent.trim().toLowerCase() === label.toLowerCase()) {
        const strong = row.querySelector("strong");
        if (strong) setText(strong, value);
      }
    });
  }

  function run() {
    const state = load();
    if (!state) return;
    applyCatalogOverrides(state);
    applyDetailOverrides(state);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  } else {
    run();
  }

  // Live-sync: update other tabs when admin saves.
  window.addEventListener("storage", e => {
    if (e.key === STORAGE_KEY) run();
  });
})();
