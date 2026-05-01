/* Admin overlay — applies localStorage edits to the public site.
 *
 * Loaded by:
 *   - index.html   (catalog cards: name + description + order + custom cards/brands)
 *   - course_pages/*.html (sidebar + optional curriculum HTML override)
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
      if (!obj || typeof obj !== "object") return null;
      return {
        courses: obj.courses || {},
        card_order: obj.card_order || {},
        brand_order: obj.brand_order || null,
        custom_brands: obj.custom_brands || {},
        custom_courses: Array.isArray(obj.custom_courses) ? obj.custom_courses : [],
      };
    } catch (e) {
      return null;
    }
  }

  function mergedBrandOrder(state) {
    const base = [];
    document.querySelectorAll("#courses .cg > .brand-block").forEach(b => {
      if (b.dataset.brand) base.push(b.dataset.brand);
    });
    const order =
      state.brand_order && state.brand_order.length ? state.brand_order.slice() : base.slice();
    const seen = new Set(order);
    (state.custom_courses || []).forEach(c => {
      if (c.brand && !seen.has(c.brand)) {
        order.push(c.brand);
        seen.add(c.brand);
      }
    });
    Object.keys(state.custom_brands || {}).forEach(k => {
      if (!seen.has(k)) {
        order.push(k);
        seen.add(k);
      }
    });
    return order;
  }

  function escapeText(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function sanitizeHtml(html) {
    return String(html || "")
      .replace(/<script[\s\S]*?>[\s\S]*?<\/script>/gi, "")
      .replace(/<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi, "")
      .replace(/\son\w+\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)/gi, "")
      .replace(/javascript:/gi, "");
  }

  function formatEnrolled(n) {
    const x = Number(n) || 0;
    return x.toLocaleString("en-US") + "+ enrolled";
  }

  function mergedCourseFields(state, slug) {
    const cust = (state.custom_courses || []).find(c => c.slug === slug);
    const ov = state.courses[slug] || {};
    return Object.assign({}, cust || {}, ov);
  }

  function normalizeCurriculumStruct(raw) {
    if (!raw || typeof raw !== "object")
      return { eyebrow: "", headline_main: "", headline_em: "", intro: "", modules: [] };
    const eyebrow = String(raw.eyebrow || "").trim();
    const headline_main = String(raw.headline_main != null ? raw.headline_main : raw.headline || "").trim();
    const headline_em = String(raw.headline_em || "").trim();
    const intro = String(raw.intro || "").trim();
    const modules = (Array.isArray(raw.modules) ? raw.modules : [])
      .map(mod => ({
        title: String(mod && mod.title != null ? mod.title : "").trim(),
        topics: (Array.isArray(mod && mod.topics) ? mod.topics : [])
          .map(t => String(t != null ? t : "").trim())
          .filter(Boolean),
      }))
      .filter(mod => mod.title || mod.topics.length);
    return { eyebrow, headline_main, headline_em, intro, modules };
  }

  function curriculumStructHasContent(st) {
    const n = normalizeCurriculumStruct(st);
    return !!(
      n.eyebrow ||
      n.headline_main ||
      n.headline_em ||
      n.intro ||
      n.modules.length
    );
  }

  function getCurriculumStaticEls(sec) {
    const modulesEl = sec.querySelector(".modules");
    if (!modulesEl) return null;
    const kids = Array.from(sec.children);
    const modIx = kids.indexOf(modulesEl);
    const slice = modIx >= 0 ? kids.slice(0, modIx) : kids;
    const eyebrowEl =
      slice.find(el => el.classList && el.classList.contains("eyebrow")) ||
      sec.querySelector(":scope > .eyebrow");
    const h2El =
      slice.find(el => el.matches && el.matches("h2.sec-head")) ||
      sec.querySelector(":scope > h2.sec-head");
    let introEl = null;
    if (
      modulesEl.previousElementSibling &&
      modulesEl.previousElementSibling.classList.contains("body-text")
    ) {
      introEl = modulesEl.previousElementSibling;
    }
    return { eyebrowEl, h2El, introEl, modulesEl };
  }

  function removeInjected() {
    document.querySelectorAll("[data-nexperts-injected]").forEach(el => el.remove());
  }

  function getBrandMetaForInject(state, brandKey) {
    const cb = (state.custom_brands || {})[brandKey];
    if (cb && (cb.label || cb.key)) return cb;
    const block = document.querySelector(`#courses .brand-block[data-brand="${CSS.escape(brandKey)}"]`);
    if (block) {
      const nameEl = block.querySelector(".bh-name");
      const tagEl = block.querySelector(".bh-tag");
      const cs = getComputedStyle(block);
      return {
        key: brandKey,
        label: nameEl ? nameEl.textContent.trim() : brandKey,
        tagline: tagEl ? tagEl.textContent.trim() : "",
        color: block.style.getPropertyValue("--bk").trim() || cs.getPropertyValue("--bk").trim() || "#1d4ed8",
        color_tint:
          block.style.getPropertyValue("--bk-tint").trim() ||
          cs.getPropertyValue("--bk-tint").trim() ||
          "#eff6ff",
      };
    }
    return {
      key: brandKey,
      label: brandKey,
      tagline: "",
      color: "#1d4ed8",
      color_tint: "#eff6ff",
    };
  }

  function createBrandBlock(cg, meta, state) {
    const block = document.createElement("div");
    block.className = "brand-block";
    block.dataset.brand = meta.key;
    block.dataset.nexpertsInjected = "1";
    block.style.setProperty("--bk", meta.color || "#1d4ed8");
    block.style.setProperty("--bk-tint", meta.color_tint || "#eff6ff");
    const parts = String(meta.label || "").trim().split(/\s+/).filter(Boolean);
    const initials = (parts[0]?.[0] || "N") + (parts[1]?.[0] || "");
    block.innerHTML =
      '<div class="brand-head">' +
      '<div class="bh-mark" aria-hidden="true">' +
      escapeText(initials.toUpperCase()) +
      "</div>" +
      '<div class="bh-text">' +
      '<div class="bh-name">' +
      escapeText(meta.label || meta.key) +
      "</div>" +
      '<div class="bh-tag">' +
      escapeText(meta.tagline || "") +
      "</div>" +
      "</div>" +
      '<div class="bh-count"><span>0</span> courses</div>' +
      "</div>" +
      '<div class="brand-grid"></div>';
    const order = mergedBrandOrder(state);
    const idx = order.indexOf(meta.key);
    let insertBefore = null;
    const start = idx < 0 ? order.length : idx + 1;
    for (let i = start; i < order.length; i++) {
      const next = cg.querySelector(
        ":scope > .brand-block[data-brand=\"" + CSS.escape(order[i]) + "\"]"
      );
      if (next) {
        insertBefore = next;
        break;
      }
    }
    if (insertBefore) cg.insertBefore(block, insertBefore);
    else cg.appendChild(block);
    return block;
  }

  function updateBhCount(block) {
    const n = block.querySelectorAll(".brand-grid .cc").length;
    const span = block.querySelector(".bh-count span");
    if (span) span.textContent = String(n);
  }

  function buildCatalogCard(c, state) {
    const m = mergedCourseFields(state, c.slug);
    const link = String(m.card_href || m.detail_href || "").trim();
    const href =
      link || (m.has_detail_page ? "course_pages/" + c.slug + ".html" : "#");
    const vendor = m.vendor || c.vendor || "";
    const badge = m.badge || c.badge || "Cert";
    const badgeVariant = m.badge_variant || c.badge_variant || "";
    const badgeNw = badgeVariant === "nw" ? " nw" : "";
    const name = m.name || c.name || "";
    const desc = m.description || c.description || "";
    const rating = Number(m.rating != null ? m.rating : c.rating) || 4.8;
    const reviews = Number(m.reviews != null ? m.reviews : c.reviews) || 0;
    const enrolled = m.enrolled != null ? m.enrolled : c.enrolled;
    const level = m.level || c.level || "Foundation";
    const cat = m.category || c.category || "cert";
    const brand = m.brand || c.brand || "";

    const a = document.createElement("a");
    a.href = href;
    a.className = "cc show";
    a.dataset.cat = cat;
    a.dataset.brand = brand;
    a.dataset.slug = c.slug;
    a.dataset.vendor = vendor;
    a.dataset.level = level;
    a.dataset.nexpertsInjected = "1";
    a.innerHTML =
      '<div class="cv2">' +
      escapeText(vendor) +
      " <span class=\"cbadge" +
      badgeNw +
      '">' +
      escapeText(badge) +
      "</span></div>" +
      '<div class="cname2">' +
      escapeText(name) +
      "</div>" +
      '<div class="cdesc2">' +
      escapeText(desc) +
      "</div>" +
      '<div class="c-stats">' +
      '  <span class="c-rate"><span class="c-star">★</span> ' +
      escapeText(String(rating)) +
      " <em>(" +
      escapeText(String(reviews)) +
      ")</em></span>" +
      '  <span class="c-enrol"><span class="c-people">👥</span> ' +
      escapeText(formatEnrolled(enrolled)) +
      "</span>" +
      "</div>" +
      '<div class="cmeta">' +
      '  <span class="clevel">' +
      escapeText(level) +
      "</span>" +
      '  <span class="c-cta">View Details <span class="cta-arr">→</span></span>' +
      "</div>";
    return a;
  }

  function injectCustomCatalog(state) {
    const cg = document.querySelector("#courses .cg");
    if (!cg || !(state.custom_courses || []).length) return;

    (state.custom_courses || []).forEach(c => {
      if (!c.slug || !c.brand) return;
      if (document.querySelector(".cc[data-slug=\"" + CSS.escape(c.slug) + "\"]")) return;

      let meta = (state.custom_brands || {})[c.brand];
      if (!meta || !meta.label) meta = getBrandMetaForInject(state, c.brand);

      let block = document.querySelector(
        "#courses .brand-block[data-brand=\"" + CSS.escape(c.brand) + "\"]"
      );
      if (!block) block = createBrandBlock(cg, meta, state);

      const grid = block.querySelector(".brand-grid");
      if (!grid) return;
      grid.appendChild(buildCatalogCard(c, state));
      updateBhCount(block);
    });

    document.querySelectorAll("#courses .brand-block").forEach(updateBhCount);
  }

  function setText(el, text) {
    if (!el || el.textContent === text) return;
    el.textContent = text;
  }

  function parseCurrencyNumber(input) {
    if (!input) return null;
    const normalized = String(input).replace(/,/g, "");
    const m = normalized.match(/(\d+(?:\.\d+)?)/);
    if (!m) return null;
    const v = Number(m[1]);
    return Number.isFinite(v) ? v : null;
  }

  function formatSaveLabel(price, priceOriginal) {
    if (!(price > 0) || !(priceOriginal > 0) || priceOriginal <= price) return null;
    const pct = Math.round(((priceOriginal - price) / priceOriginal) * 100);
    if (pct <= 0) return null;
    return `Save ${pct}%`;
  }

  function applyCatalogOverrides(state) {
    const cards = document.querySelectorAll(".cc[data-slug]");
    if (!cards.length) return;

    cards.forEach(card => {
      const slug = card.dataset.slug;
      const isCustom = !!(state.custom_courses || []).find(c => c.slug === slug);
      const hasOv = !!(state.courses[slug] && Object.keys(state.courses[slug]).length);
      if (!isCustom && !hasOv) return;
      const m = mergedCourseFields(state, slug);
      if (m.name) setText(card.querySelector(".cname2"), m.name);
      if (m.description) setText(card.querySelector(".cdesc2"), m.description);
    });

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

  function wireCurriculumModules(root) {
    if (!root) return;
    root.querySelectorAll(".module").forEach(btn => {
      btn.addEventListener(
        "click",
        function (ev) {
          ev.preventDefault();
          if (typeof window.toggleModule === "function") window.toggleModule(this);
        },
        { passive: false }
      );
    });
  }

  function applyCurriculumOverride(state, slug) {
    const sec = document.getElementById("sec-curriculum");
    if (!sec) return;

    const m = mergedCourseFields(state, slug);
    const st = getCurriculumStaticEls(sec);
    if (!st) return;
    const { eyebrowEl, h2El, introEl, modulesEl } = st;

    const clearMount = () => {
      const mount = sec.querySelector("#nexperts-curriculum-admin-mount");
      if (mount) mount.remove();
      sec.querySelectorAll("[data-nexperts-cv-hidden]").forEach(el => {
        el.removeAttribute("data-nexperts-cv-hidden");
        el.style.removeProperty("display");
      });
      [eyebrowEl, h2El, introEl, modulesEl].forEach(el => {
        if (el) el.style.removeProperty("display");
      });
    };

    const struct = normalizeCurriculumStruct(m.curriculum_struct);
    if (curriculumStructHasContent(struct)) {
      clearMount();
      [eyebrowEl, h2El, introEl, modulesEl].forEach(el => {
        if (!el) return;
        el.setAttribute("data-nexperts-cv-hidden", "1");
        el.style.display = "none";
      });

      const mount = document.createElement("div");
      mount.id = "nexperts-curriculum-admin-mount";
      mount.className = "nexperts-admin-curriculum";
      sec.insertBefore(mount, modulesEl);

      const eb = document.createElement("div");
      eb.className = "eyebrow";
      eb.textContent = struct.eyebrow || "Course Curriculum";
      mount.appendChild(eb);

      const h2 = document.createElement("h2");
      h2.className = "sec-head";
      if (struct.headline_em) {
        if (struct.headline_main) h2.appendChild(document.createTextNode(struct.headline_main + " "));
        const em = document.createElement("em");
        em.textContent = struct.headline_em;
        h2.appendChild(em);
      } else {
        h2.textContent = struct.headline_main || "";
      }
      mount.appendChild(h2);

      if (struct.intro) {
        const p = document.createElement("p");
        p.className = "body-text";
        p.textContent = struct.intro;
        mount.appendChild(p);
      }

      const wrap = document.createElement("div");
      wrap.className = "modules";
      struct.modules.forEach((mod, i) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "module" + (i === 0 ? " open" : "");
        const mh = document.createElement("div");
        mh.className = "module-header";
        const num = document.createElement("span");
        num.className = "module-num";
        num.textContent = String(i + 1).padStart(2, "0");
        const h4 = document.createElement("h4");
        h4.textContent = mod.title || "Module";
        const cnt = document.createElement("span");
        cnt.className = "module-count";
        const tc = mod.topics.length;
        cnt.textContent = tc + " topic" + (tc === 1 ? "" : "s");
        const arr = document.createElement("span");
        arr.className = "module-arrow";
        arr.textContent = "›";
        mh.appendChild(num);
        mh.appendChild(h4);
        mh.appendChild(cnt);
        mh.appendChild(arr);
        btn.appendChild(mh);
        const mb = document.createElement("div");
        mb.className = "module-body";
        const mt = document.createElement("div");
        mt.className = "module-topics";
        mod.topics.forEach(topic => {
          const d = document.createElement("div");
          d.className = "topic";
          d.textContent = topic;
          mt.appendChild(d);
        });
        mb.appendChild(mt);
        btn.appendChild(mb);
        wrap.appendChild(btn);
      });
      mount.appendChild(wrap);
      wireCurriculumModules(mount);
      return;
    }

    const raw = m.curriculum_html;
    if (!raw || !String(raw).trim()) {
      clearMount();
      return;
    }

    const html = sanitizeHtml(raw);
    if (!html.trim()) {
      clearMount();
      return;
    }

    clearMount();
    if (introEl) {
      introEl.setAttribute("data-nexperts-cv-hidden", "1");
      introEl.style.display = "none";
    }
    modulesEl.setAttribute("data-nexperts-cv-hidden", "1");
    modulesEl.style.display = "none";

    const mount = document.createElement("div");
    mount.id = "nexperts-curriculum-admin-mount";
    mount.className = "nexperts-admin-curriculum";
    sec.insertBefore(mount, modulesEl);
    mount.innerHTML = html;
    wireCurriculumModules(mount);
  }

  function applyDetailOverrides(state) {
    const path = (location.pathname || "").toLowerCase();
    const m = path.match(/\/course_pages\/([^/]+)\.html?$/);
    if (!m) return;
    const slug = decodeURIComponent(m[1]);
    const isCustom = !!(state.custom_courses || []).find(c => c.slug === slug);
    const hasCourseOv = !!(state.courses[slug] && Object.keys(state.courses[slug]).length);
    const ov = mergedCourseFields(state, slug);
    const hasCurriculum =
      curriculumStructHasContent(ov.curriculum_struct) ||
      !!(ov.curriculum_html && String(ov.curriculum_html).trim());
    if (!isCustom && !hasCourseOv && !hasCurriculum) return;

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

    syncSaveBadge(ov);
    applyCurriculumOverride(state, slug);
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

  function syncSaveBadge(ov) {
    const saveEl = document.querySelector(".price-save");
    if (!saveEl) return;

    const currentPriceEl = document.querySelector(".price");
    const currentOrigEl = document.querySelector(".price-orig");
    if (!currentPriceEl || !currentOrigEl) return;

    const priceNum = parseCurrencyNumber(ov.price || currentPriceEl.textContent);
    const originalNum = parseCurrencyNumber(ov.price_original || currentOrigEl.textContent);
    const label = formatSaveLabel(priceNum, originalNum);
    if (!label) return;

    setText(saveEl, label);
  }

  function run() {
    const state = load();
    if (!state) return;
    const onLanding = !!document.querySelector("#courses .cg");
    if (onLanding) {
      removeInjected();
      injectCustomCatalog(state);
      applyCatalogOverrides(state);
    }
    applyDetailOverrides(state);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run, { once: true });
  } else {
    run();
  }

  window.addEventListener("storage", e => {
    if (e.key === STORAGE_KEY) run();
  });
})();
