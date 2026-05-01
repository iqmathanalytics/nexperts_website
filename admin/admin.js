/* Admin · Course Manager
 * --------------------------------------------------------------
 *  Storage model (localStorage["nexperts_admin_v1"]):
 *    {
 *      version: 2,
 *      courses: { [slug]: { …, curriculum_struct?: { intro, modules:[{title,topics[]}] },
 *                           curriculum_html? (legacy) } },
 *      card_order: { [brand]: [slug, ...] },
 *      brand_order: [brand, ...] | null,
 *      custom_brands: { [key]: { key, label, tagline, color, color_tint } },
 *      custom_courses: [ { slug, brand, category, vendor, badge, badge_variant,
 *                          name, description, level, rating, reviews, enrolled,
 *                          card_href } ]
 *    }
 *  Public site reads the same storage via overlay.js.
 * -------------------------------------------------------------- */

const STORAGE_KEY = "nexperts_admin_v1";
const SESSION_KEY = "nexperts_admin_session_v1";
const DATA_URL = "/admin/admin-data.json";

const ADMIN_USER = "admin";
const ADMIN_PASS = "admin123";
const SESSION_TTL_MS = 24 * 60 * 60 * 1000;

const FIELDS_CATALOG = ["name", "description"];
const FIELDS_DETAIL = ["duration", "next_intake", "price", "price_original"];

const FIELD_LABELS = {
  name: "Course name",
  description: "Description",
  duration: "Duration",
  next_intake: "Next intake",
  price: "Price (current)",
  price_original: "Price (original)",
};
const FIELD_PLACEHOLDERS = {
  name: "e.g. CEH v13 AI",
  description: "Short, punchy description shown on the catalog card",
  duration: "e.g. 5 days / 40 hrs",
  next_intake: "e.g. 12 May 2026",
  price: "e.g. RM 3,800",
  price_original: "e.g. RM 4,500",
};

let baseline = null;
let courseBySlug = {};
let overrides = {};
let activeSlug = null;
let activeFilter = "all";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const escapeHTML = (s = "") =>
  String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

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

function curriculumStructIsEmpty(s) {
  const n = normalizeCurriculumStruct(s);
  return (
    !n.eyebrow &&
    !n.headline_main &&
    !n.headline_em &&
    !n.intro &&
    !n.modules.length
  );
}

function curriculumEditorNeedsFetch(struct) {
  return curriculumStructIsEmpty(struct);
}

function splitH2ForStruct(h2) {
  if (!h2) return { headline_main: "", headline_em: "" };
  const em = h2.querySelector("em");
  if (em) {
    const clone = h2.cloneNode(true);
    clone.querySelectorAll("em").forEach(e => e.remove());
    return {
      headline_main: clone.textContent.replace(/\s+/g, " ").trim(),
      headline_em: em.textContent.replace(/\s+/g, " ").trim(),
    };
  }
  return { headline_main: h2.textContent.replace(/\s+/g, " ").trim(), headline_em: "" };
}

async function fetchCurriculumFromDetailHtml(slug) {
  const url = `../course_pages/${encodeURIComponent(slug)}.html`;
  try {
    const res = await fetch(url, { cache: "no-cache" });
    if (!res.ok) return null;
    const html = await res.text();
    const doc = new DOMParser().parseFromString(html, "text/html");
    const sec = doc.querySelector("#sec-curriculum");
    if (!sec) return null;

    const eyebrowEl = sec.querySelector(":scope > .eyebrow");
    const h2 = sec.querySelector(":scope > h2.sec-head");
    const hParts = splitH2ForStruct(h2);
    const modulesEl = sec.querySelector(":scope > .modules");
    let intro = "";
    if (modulesEl && modulesEl.previousElementSibling) {
      const prev = modulesEl.previousElementSibling;
      if (prev.tagName === "P" && prev.classList.contains("body-text")) {
        intro = prev.textContent.replace(/\s+/g, " ").trim();
      }
    }

    const eyebrow = eyebrowEl?.textContent?.replace(/\s+/g, " ").trim() || "";
    const modules = [];
    if (modulesEl) {
      modulesEl.querySelectorAll(":scope > button.module").forEach(btn => {
        const h4 = btn.querySelector(".module-header h4, h4");
        const title = h4?.textContent?.replace(/\s+/g, " ").trim() || "";
        const topics = [...btn.querySelectorAll(".module-topics .topic, .topic")]
          .map(t => t.textContent.replace(/\s+/g, " ").trim())
          .filter(Boolean);
        modules.push({ title, topics });
      });
    }

    return {
      eyebrow,
      headline_main: hParts.headline_main,
      headline_em: hParts.headline_em,
      intro,
      modules,
    };
  } catch (e) {
    console.warn("admin: could not fetch curriculum HTML", slug, e);
    return null;
  }
}

function fillCurriculumEditorForm(struct) {
  const s = normalizeCurriculumStruct(struct);
  const eb = $("#adCvEyebrow");
  const hm = $("#adCvHeadMain");
  const he = $("#adCvHeadEm");
  const intro = $("#adCvIntro");
  const modsRoot = $("#adCvMods");
  if (eb) eb.value = s.eyebrow;
  if (hm) hm.value = s.headline_main;
  if (he) he.value = s.headline_em;
  if (intro) intro.value = s.intro;
  if (modsRoot) {
    const mods = s.modules.length ? s.modules : [{ title: "", topics: [""] }];
    modsRoot.innerHTML = mods.map((m, i) => renderCurriculumModuleHTML(m, i)).join("");
    renumberCurriculumModules();
  }
  $("#adCvLoading")?.remove();
  $("#adCvFetchErr")?.remove();
}

function renderCurriculumModuleHTML(mod, index) {
  const title = escapeHTML(mod.title || "");
  const topics = mod.topics && mod.topics.length ? mod.topics : [""];
  const topicsHtml = topics
    .map(
      t =>
        `<div class="ad-cv-topic-row"><input type="text" class="ad-cv-topic-input" value="${escapeHTML(t)}" placeholder="Topic"><button type="button" class="ad-cv-topic-del" data-cv="topic-del" aria-label="Remove">×</button></div>`
    )
    .join("");
  return `<div class="ad-cv-mod" data-cv-mod>
    <div class="ad-cv-mod-toolbar">
      <span class="ad-cv-mod-label">Module <span class="ad-cv-mod-ix">${index + 1}</span></span>
      <button type="button" class="ad-btn ad-btn-link ad-cv-tmini" data-cv="mod-up">Up</button>
      <button type="button" class="ad-btn ad-btn-link ad-cv-tmini" data-cv="mod-down">Down</button>
      <button type="button" class="ad-btn ad-btn-link ad-cv-tmini" data-cv="mod-del">Remove</button>
    </div>
    <div class="ad-field ad-cv-mod-title-wrap">
      <label>Module title</label>
      <input type="text" class="ad-cv-mod-title" value="${title}" placeholder="e.g. Mobile Devices, Networking">
    </div>
    <div class="ad-cv-topics">${topicsHtml}</div>
    <button type="button" class="ad-btn ad-btn-ghost ad-cv-add-topic" data-cv="topic-add">＋ Topic</button>
  </div>`;
}

function renderCurriculumEditorHTML(struct, slug, hasLegacyHtml, showLoadingFetch) {
  const s = normalizeCurriculumStruct(struct);
  const modules = s.modules.length ? s.modules : [{ title: "", topics: [""] }];
  const modsHtml = modules.map((m, i) => renderCurriculumModuleHTML(m, i)).join("");
  const legacy = hasLegacyHtml
    ? `<div class="ad-cv-legacy">A legacy HTML curriculum override exists. Saving here replaces it with this structured curriculum.</div>`
    : "";
  const loading = showLoadingFetch
    ? `<div id="adCvLoading" class="ad-cv-loading">Loading curriculum from <code>course_pages/${escapeHTML(slug)}.html</code>…</div>`
    : "";
  return `<div class="ad-section" id="adCvSection">
    <h4>Curriculum <span class="ad-section-tag">Detail page · #sec-curriculum</span></h4>
    <p class="ad-curriculum-note">These fields mirror the public course page. When no override is saved yet, we load the current HTML automatically (requires the site to be served over HTTP, not file://).</p>
    ${loading}
    <p id="adCvFetchErr" class="ad-cv-fetch-err" hidden></p>
    ${legacy}
    <div class="ad-field-row">
      <div class="ad-field">
        <label>Section eyebrow</label>
        <input type="text" id="adCvEyebrow" value="${escapeHTML(s.eyebrow)}" placeholder="e.g. Course Curriculum">
      </div>
    </div>
    <div class="ad-field">
      <label>Heading — main line <span class="ad-field-help">before italic part</span></label>
      <input type="text" id="adCvHeadMain" value="${escapeHTML(s.headline_main)}" placeholder="e.g. Two exams.">
    </div>
    <div class="ad-field">
      <label>Heading — emphasis <span class="ad-field-help">optional · renders inside &lt;em&gt;</span></label>
      <input type="text" id="adCvHeadEm" value="${escapeHTML(s.headline_em)}" placeholder="e.g. One foundation.">
    </div>
    <div class="ad-field">
      <label>Introduction paragraph</label>
      <textarea id="adCvIntro" rows="4" placeholder="Opening paragraph under the heading">${escapeHTML(s.intro)}</textarea>
    </div>
    <div class="ad-cv-mods-head"><span>Modules</span><button type="button" class="ad-btn ad-btn-ghost" data-cv="add-mod">＋ Add module</button></div>
    <div id="adCvMods">${modsHtml}</div>
  </div>`;
}

function collectCurriculumStructFromDrawer() {
  const eyebrow = ($("#adCvEyebrow")?.value || "").trim();
  const headline_main = ($("#adCvHeadMain")?.value || "").trim();
  const headline_em = ($("#adCvHeadEm")?.value || "").trim();
  const intro = ($("#adCvIntro")?.value || "").trim();
  const mods = [];
  $$("#adCvMods [data-cv-mod]").forEach(wrap => {
    const title = (wrap.querySelector(".ad-cv-mod-title")?.value || "").trim();
    const topics = $$(".ad-cv-topic-input", wrap)
      .map(inp => (inp.value || "").trim())
      .filter(Boolean);
    if (title || topics.length) mods.push({ title, topics });
  });
  return { eyebrow, headline_main, headline_em, intro, modules: mods };
}

function renumberCurriculumModules() {
  $$("#adCvMods .ad-cv-mod-ix").forEach((el, i) => {
    el.textContent = String(i + 1);
  });
}

let curriculumClickHandler = null;

function bindCurriculumEditor() {
  const body = $("#adDrawerBody");
  if (!body || !$("#adCvMods")) return;
  curriculumClickHandler = e => {
    const btn = e.target.closest("[data-cv]");
    if (!btn) return;
    const act = btn.dataset.cv;
    const mod = btn.closest("[data-cv-mod]");
    const modsRoot = $("#adCvMods");
    if (act === "add-mod") {
      e.preventDefault();
      if (!modsRoot) return;
      const n = modsRoot.querySelectorAll("[data-cv-mod]").length;
      modsRoot.insertAdjacentHTML("beforeend", renderCurriculumModuleHTML({ title: "", topics: [""] }, n));
      renumberCurriculumModules();
      return;
    }
    if (act === "topic-add" && mod) {
      mod.querySelector(".ad-cv-topics").insertAdjacentHTML(
        "beforeend",
        `<div class="ad-cv-topic-row"><input type="text" class="ad-cv-topic-input" value="" placeholder="Topic"><button type="button" class="ad-cv-topic-del" data-cv="topic-del" aria-label="Remove">×</button></div>`
      );
      return;
    }
    if (act === "topic-del") {
      const row = btn.closest(".ad-cv-topic-row");
      const topicsWrap = row?.parentElement;
      if (row && topicsWrap && topicsWrap.querySelectorAll(".ad-cv-topic-row").length > 1) row.remove();
      return;
    }
    if (act === "mod-del" && mod && modsRoot) {
      if (modsRoot.querySelectorAll("[data-cv-mod]").length > 1) mod.remove();
      renumberCurriculumModules();
      return;
    }
    if (act === "mod-up" && mod && mod.previousElementSibling) {
      mod.parentNode.insertBefore(mod, mod.previousElementSibling);
      renumberCurriculumModules();
      return;
    }
    if (act === "mod-down" && mod && mod.nextElementSibling) {
      mod.parentNode.insertBefore(mod.nextElementSibling, mod);
      renumberCurriculumModules();
    }
  };
  body.addEventListener("click", curriculumClickHandler);
}

function unbindCurriculumEditor() {
  const body = $("#adDrawerBody");
  if (body && curriculumClickHandler) {
    body.removeEventListener("click", curriculumClickHandler);
    curriculumClickHandler = null;
  }
}

function defaultOverrides() {
  return {
    version: 2,
    courses: {},
    card_order: {},
    brand_order: null,
    custom_brands: {},
    custom_courses: [],
  };
}

function loadOverrides() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaultOverrides();
    const obj = JSON.parse(raw);
    if (!obj || typeof obj !== "object") return defaultOverrides();
    return {
      version: 2,
      courses: obj.courses || {},
      card_order: obj.card_order || {},
      brand_order: obj.brand_order || null,
      custom_brands: obj.custom_brands || {},
      custom_courses: Array.isArray(obj.custom_courses) ? obj.custom_courses : [],
    };
  } catch (e) {
    console.warn("admin: failed to parse storage, starting fresh", e);
    return defaultOverrides();
  }
}

function saveOverrides(showToast = true) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
    updateStorageStatus();
    if (showToast) toast("Saved · changes will appear on landing & course pages", "success");
  } catch (e) {
    toast("Could not save (storage quota?). Try Export & Import.", "error");
    console.error(e);
  }
}

function rebuildCourseIndex() {
  courseBySlug = Object.fromEntries(
    baseline.courses.map(c => [c.slug, { ...c, is_custom: false }])
  );
  (overrides.custom_courses || []).forEach(c => {
    if (!c.slug) return;
    const href = (c.card_href || c.detail_href || "#").trim() || "#";
    courseBySlug[c.slug] = {
      vendor: c.vendor || "",
      badge: c.badge || "Cert",
      badge_variant: c.badge_variant || "",
      name: c.name || "",
      description: c.description || "",
      level: c.level || "Foundation",
      rating: Number(c.rating) || 4.8,
      reviews: Number(c.reviews) || 0,
      enrolled: Number(c.enrolled) || 1000,
      has_detail_page: !!c.has_detail_page,
      slug: c.slug,
      brand: c.brand || "",
      category: c.category || "cert",
      card_href: href,
      detail_href: href,
      duration: c.duration || "",
      next_intake: c.next_intake || "",
      price: c.price || "",
      price_original: c.price_original || "",
      curriculum_html: c.curriculum_html || "",
      curriculum_struct: c.curriculum_struct,
      is_custom: true,
    };
  });
  for (const slug in overrides.courses) {
    const ov = overrides.courses[slug];
    if (!ov || !courseBySlug[slug]) continue;
    courseBySlug[slug] = { ...courseBySlug[slug], ...ov };
  }
}

function getBrandMeta(brandKey) {
  return baseline.brand_meta[brandKey] || (overrides.custom_brands || {})[brandKey] || null;
}

function getMergedBrandOrder() {
  const base = baseline.brand_order.slice();
  const order =
    overrides.brand_order && overrides.brand_order.length ? overrides.brand_order.slice() : base.slice();
  const seen = new Set(order);
  (overrides.custom_courses || []).forEach(c => {
    if (c.brand && !seen.has(c.brand)) {
      order.push(c.brand);
      seen.add(c.brand);
    }
  });
  Object.keys(overrides.custom_brands || {}).forEach(k => {
    if (!seen.has(k)) {
      order.push(k);
      seen.add(k);
    }
  });
  return order;
}

function slugsForBrand(brandKey) {
  const co = overrides.card_order[brandKey];
  if (co && co.length) return co.slice();
  const bc = baseline.card_order[brandKey];
  if (bc && bc.length) return bc.slice();
  return (overrides.custom_courses || []).filter(c => c.brand === brandKey).map(c => c.slug);
}

function updateStorageStatus() {
  const total = countEditedCourses();
  const reordered = countReorderedBrands();
  $("#kpiEdited").textContent = total;
  $("#kpiReordered").textContent = reordered;
  const status = $("#adStorageStatus");
  const customN = (overrides.custom_courses || []).length;
  if (!total && !reordered && !customN) {
    status.textContent = "No overrides — using baseline";
    status.style.color = "var(--ink4)";
  } else {
    status.textContent = `${total} field edit${total === 1 ? "" : "s"} · ${reordered} brand${reordered === 1 ? "" : "s"} reordered${customN ? ` · ${customN} custom course${customN === 1 ? "" : "s"}` : ""}`;
    status.style.color = "var(--blue)";
  }
}

function hasOverrides(slug) {
  return !!(overrides.courses[slug] && Object.keys(overrides.courses[slug]).length);
}

function isShownAsEdited(slug) {
  return hasOverrides(slug) || !!courseBySlug[slug]?.is_custom;
}

function countEditedCourses() {
  const s = new Set();
  for (const slug in overrides.courses) {
    if (hasOverrides(slug)) s.add(slug);
  }
  (overrides.custom_courses || []).forEach(c => {
    if (c.slug) s.add(c.slug);
  });
  return s.size;
}

function countReorderedBrands() {
  if (!overrides.card_order) return 0;
  let n = 0;
  for (const k in overrides.card_order) {
    const a = overrides.card_order[k];
    const b = baseline.card_order[k];
    if (!b) {
      if (a && a.length) n++;
      continue;
    }
    if (a.length !== b.length || a.some((x, i) => x !== b[i])) n++;
  }
  return n;
}

function resolveCourse(slug) {
  const base = courseBySlug[slug];
  if (!base) return null;
  const ov = overrides.courses[slug] || {};
  return { ...base, ...ov };
}

async function init() {
  try {
    const res = await fetch(DATA_URL, { cache: "no-cache" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    baseline = await res.json();
  } catch (e) {
    console.error(e);
    document.body.innerHTML = `<div style="padding:60px;text-align:center;color:#991b1b">
      <h2 style="font-family:'Fraunces',serif;font-weight:300;font-size:1.8rem;margin-bottom:8px">
        Could not load admin baseline data.</h2>
      <p>The admin panel needs to be served via a local HTTP server (not file://) so it can fetch <code>admin-data.json</code>.</p>
      <p style="margin-top:18px;font-size:.85rem;color:#7a8194">Try: <code>python -m http.server 8765</code> from the project root, then open <code>http://localhost:8765/admin/</code>.</p>
    </div>`;
    return;
  }

  overrides = loadOverrides();
  rebuildCourseIndex();
  pruneStaleOverrides();
  rebuildCourseIndex();

  $("#kpiBrands").textContent = baseline.brand_order.length;
  const customCount = (overrides.custom_courses || []).length;
  $("#kpiCourses").textContent = String(baseline.courses.length + customCount);
  $("#kpiPhase1").textContent = baseline.courses.filter(c => c.has_detail_page).length;

  renderBoard();
  bindUI();
  updateStorageStatus();
}

function pruneStaleOverrides() {
  const valid = new Set(Object.keys(courseBySlug));
  for (const slug in overrides.courses) {
    if (!valid.has(slug)) delete overrides.courses[slug];
  }
  for (const brand in overrides.card_order) {
    overrides.card_order[brand] = (overrides.card_order[brand] || []).filter(s => valid.has(s));
  }
  overrides.custom_courses = (overrides.custom_courses || []).filter(c => c && c.slug && c.brand);
}

function renderBoard() {
  const board = $("#adBoard");
  board.innerHTML = "";

  getMergedBrandOrder().forEach(brandKey => {
    const meta = getBrandMeta(brandKey);
    if (!meta) return;
    const slugs = slugsForBrand(brandKey);
    if (!slugs.length) return;
    board.appendChild(renderBrandBlock(meta, slugs));
  });

  applyFilter();
}

function renderBrandBlock(meta, slugs) {
  const block = document.createElement("section");
  block.className = "bblock";
  block.dataset.brand = meta.key;
  block.style.setProperty("--bk", meta.color);
  block.style.setProperty("--bk-tint", meta.color_tint);

  const initials = meta.label
    .split(/\s+/)
    .slice(0, 2)
    .map(w => w[0])
    .join("")
    .toUpperCase();

  block.innerHTML = `
    <header class="bblock-head">
      <div class="bh-mark">${escapeHTML(initials)}</div>
      <div class="bh-text">
        <div class="bh-name">${escapeHTML(meta.label)}</div>
        <div class="bh-tag">${escapeHTML(meta.tagline)}</div>
      </div>
      <div class="bh-count"><b>${slugs.length}</b> course${slugs.length === 1 ? "" : "s"}</div>
    </header>
    <div class="bgrid"></div>
  `;
  const grid = block.querySelector(".bgrid");
  slugs.forEach(slug => grid.appendChild(renderCard(slug, meta)));
  return block;
}

function renderCard(slug, meta) {
  const c = resolveCourse(slug);
  if (!c) return document.createComment(`missing ${slug}`);

  const card = document.createElement("article");
  card.className = "acc";
  card.dataset.slug = slug;
  card.dataset.brand = c.brand;
  card.dataset.cat = c.category;
  card.dataset.searchKey = `${c.name} ${c.vendor} ${c.slug}`.toLowerCase();
  card.draggable = false;

  const editedBadge = hasOverrides(slug) ? `<span class="acc-edited">Edited</span>` : "";
  const customBadge = c.is_custom ? `<span class="acc-edited" style="background:var(--amberL);color:#92400e">Custom</span>` : "";
  const detailBits = c.has_detail_page
    ? [
        ["Duration", c.duration],
        ["Intake", c.next_intake],
        ["Price", c.price],
      ]
        .map(([k, v]) => `<i class="${v ? "has-val" : ""}">${escapeHTML(k)}: ${escapeHTML(v || "—")}</i>`)
        .join("")
    : `<i class="no-detail">Catalog-only · no detail page</i>`;

  card.innerHTML = `
    <div class="acc-head">
      <div class="acc-handle" title="Drag to reorder" draggable="true">⋮⋮</div>
      <div class="acc-vendor">
        ${escapeHTML(c.vendor)} · ${escapeHTML(c.badge)}
        ${editedBadge}${customBadge}
      </div>
    </div>
    <div class="acc-name">${escapeHTML(c.name)}</div>
    <div class="acc-desc">${escapeHTML(c.description)}</div>
    <div class="acc-meta">${detailBits}</div>
    <div class="acc-actions">
      <button class="acc-edit" data-slug="${slug}">✎ Edit course</button>
      <button class="acc-revert" data-slug="${slug}" ${hasOverrides(slug) ? "" : "disabled style='opacity:.4;cursor:not-allowed'"}>Revert</button>
    </div>
  `;
  return card;
}

function refreshCardInPlace(slug) {
  const old = $(`.acc[data-slug="${CSS.escape(slug)}"]`);
  if (!old) return;
  const block = old.closest(".bblock");
  const meta = getBrandMeta(block.dataset.brand);
  if (!meta) return;
  const fresh = renderCard(slug, meta);
  old.replaceWith(fresh);
  applyFilter();
}

function applyFilter() {
  const q = ($("#adSearch").value || "").trim().toLowerCase();
  const onlyEdited = $("#adShowEditedOnly").checked;
  const cat = activeFilter;

  $$(".bblock").forEach(block => {
    let visible = 0;
    block.querySelectorAll(".acc").forEach(card => {
      const slug = card.dataset.slug;
      const matchCat = cat === "all" || card.dataset.cat === cat;
      const matchSearch = !q || card.dataset.searchKey.includes(q);
      const matchEdited = !onlyEdited || isShownAsEdited(slug);
      const ok = matchCat && matchSearch && matchEdited;
      card.style.display = ok ? "" : "none";
      if (ok) visible++;
    });
    block.classList.toggle("b-hide", visible === 0);
  });
}

let dragSrc = null;

function onDragStart(e) {
  const handle = e.target;
  if (!handle.classList.contains("acc-handle")) return;
  const card = handle.closest(".acc");
  if (!card) return;
  dragSrc = card;
  card.classList.add("dragging");
  e.dataTransfer.effectAllowed = "move";
  try {
    e.dataTransfer.setData("text/plain", card.dataset.slug);
  } catch (_) {}
}

function onDragOver(e) {
  if (!dragSrc) return;
  const card = e.target.closest(".acc");
  if (!card || card === dragSrc) return;
  if (card.dataset.brand !== dragSrc.dataset.brand) return;
  e.preventDefault();
  e.dataTransfer.dropEffect = "move";
  $$(".acc.drop-target").forEach(el => el !== card && el.classList.remove("drop-target"));
  card.classList.add("drop-target");
}

function onDragLeave(e) {
  const card = e.target.closest(".acc");
  if (card) card.classList.remove("drop-target");
}

function onDrop(e) {
  if (!dragSrc) return;
  const target = e.target.closest(".acc");
  if (!target || target === dragSrc) {
    cleanupDrag();
    return;
  }
  if (target.dataset.brand !== dragSrc.dataset.brand) {
    cleanupDrag();
    return;
  }
  e.preventDefault();

  const grid = target.parentNode;
  const rect = target.getBoundingClientRect();
  const before = e.clientY - rect.top < rect.height / 2;
  grid.insertBefore(dragSrc, before ? target : target.nextSibling);

  const brand = dragSrc.dataset.brand;
  const newOrder = $$(".acc", grid).map(c => c.dataset.slug);
  overrides.card_order[brand] = newOrder;
  saveOverrides();
  toast("Order updated · saved");

  cleanupDrag();
}

function cleanupDrag() {
  if (dragSrc) dragSrc.classList.remove("dragging");
  $$(".acc.drop-target").forEach(el => el.classList.remove("drop-target"));
  dragSrc = null;
}

async function openDrawer(slug) {
  activeSlug = slug;
  const c = resolveCourse(slug);
  if (!c) return;

  $("#adDrawerEyebrow").textContent = `${c.vendor} · ${c.badge}`;
  $("#adDrawerTitle").textContent = c.name;

  const body = $("#adDrawerBody");
  let html = "";

  html += `<div class="ad-section"><h4>Catalog card <span class="ad-section-tag">Visible on landing page</span></h4>`;
  FIELDS_CATALOG.forEach(f => {
    html += renderField(f, c[f] || "");
  });
  html += `</div>`;

  html += `<div class="ad-section"><h4>Course detail page <span class="ad-section-tag">${c.has_detail_page ? `course_pages/${c.slug}.html` : "Not yet published"}</span></h4>`;
  if (!c.has_detail_page) {
    html += `<div class="ad-no-detail">This course doesn't have a detail page yet — duration, intake and pricing will apply when a page exists.</div>`;
  }
  FIELDS_DETAIL.forEach(f => {
    html += renderField(f, c[f] || "");
  });
  html += `</div>`;

  let initStruct = normalizeCurriculumStruct(c.curriculum_struct);
  const hasLegacy = !!(c.curriculum_html && String(c.curriculum_html).trim());
  const needFetch = c.has_detail_page && curriculumEditorNeedsFetch(initStruct) && !hasLegacy;

  if (c.has_detail_page) {
    html += renderCurriculumEditorHTML(initStruct, slug, hasLegacy, needFetch);
  }

  body.innerHTML = html;
  body.addEventListener("input", onDrawerInput);
  bindCurriculumEditor();

  $("#adDrawer").classList.add("show");
  $("#adDrawer").setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";

  setTimeout(() => body.querySelector("input,textarea")?.focus(), 200);

  if (needFetch) {
    const fetched = await fetchCurriculumFromDetailHtml(slug);
    if (activeSlug !== slug) return;
    if (fetched) {
      fillCurriculumEditorForm(fetched);
    } else {
      const err = $("#adCvFetchErr");
      if (err) {
        err.hidden = false;
        err.textContent =
          "Could not load the detail page (open admin via your local server, e.g. http://localhost:8765/admin/). You can still enter curriculum below.";
      }
      $("#adCvLoading")?.remove();
    }
  }
}

function renderField(f, val) {
  const label = FIELD_LABELS[f];
  const placeholder = FIELD_PLACEHOLDERS[f];
  const baseVal = courseBySlug[activeSlug]?.[f] ?? "";
  const changed = val !== baseVal;
  const help = changed ? `<span class="ad-field-help" style="color:var(--blue)">● modified from baseline</span>` : "";

  const input =
    f === "description"
      ? `<textarea data-field="${f}" placeholder="${escapeHTML(placeholder)}">${escapeHTML(val)}</textarea>`
      : `<input type="text" data-field="${f}" value="${escapeHTML(val)}" placeholder="${escapeHTML(placeholder)}">`;
  return `<div class="ad-field"><label>${escapeHTML(label)} ${help}</label>${input}</div>`;
}

function onDrawerInput(e) {
  const f = e.target.dataset.field;
  if (!f) return;
  const baseVal = courseBySlug[activeSlug]?.[f] ?? "";
  const changed = e.target.value !== baseVal;
  const wrap = e.target.closest(".ad-field");
  if (!wrap) return;
  let help = wrap.querySelector(".ad-field-help");
  if (changed && !help) {
    wrap.querySelector("label")?.insertAdjacentHTML(
      "beforeend",
      ` <span class="ad-field-help" style="color:var(--blue)">● modified from baseline</span>`
    );
  } else if (!changed && help) {
    help.remove();
  }
}

function closeDrawer() {
  $("#adDrawer").classList.remove("show");
  $("#adDrawer").setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  unbindCurriculumEditor();
  $("#adDrawerBody").removeEventListener("input", onDrawerInput);
  activeSlug = null;
}

function applyDrawer() {
  if (!activeSlug) return;
  const slug = activeSlug;
  const merged = { ...(overrides.courses[slug] || {}) };

  $$("#adDrawerBody [data-field]").forEach(el => {
    const f = el.dataset.field;
    const v = el.value.trim();
    const baseVal = courseBySlug[slug]?.[f] ?? "";
    if (v === baseVal) delete merged[f];
    else merged[f] = v;
  });

  if ($("#adCvMods")) {
    const norm = normalizeCurriculumStruct(collectCurriculumStructFromDrawer());
    const baseNorm = normalizeCurriculumStruct(courseBySlug[slug]?.curriculum_struct);
    if (JSON.stringify(norm) !== JSON.stringify(baseNorm)) {
      if (curriculumStructIsEmpty(norm)) delete merged.curriculum_struct;
      else {
        merged.curriculum_struct = norm;
        delete merged.curriculum_html;
      }
    }
  }

  if (Object.keys(merged).length) overrides.courses[slug] = merged;
  else delete overrides.courses[slug];

  saveOverrides();
  rebuildCourseIndex();
  refreshCardInPlace(slug);
  closeDrawer();
}

function revertCard(slug) {
  if (!hasOverrides(slug)) return;
  if (!confirm(`Revert "${courseBySlug[slug].name}" field overrides to baseline?`)) return;
  delete overrides.courses[slug];
  saveOverrides(false);
  rebuildCourseIndex();
  refreshCardInPlace(slug);
}

function resetAll() {
  if (!confirm("Reset ALL course edits, custom courses, custom brands and order changes?")) return;
  overrides = defaultOverrides();
  saveOverrides(false);
  rebuildCourseIndex();
  renderBoard();
  toast("Restored to baseline", "success");
}

function exportJSON() {
  const data = JSON.stringify(overrides, null, 2);
  const blob = new Blob([data], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `nexperts-admin-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  toast("Exported overrides JSON", "success");
}

function importJSON(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const obj = JSON.parse(reader.result);
      if (!obj || typeof obj !== "object") throw new Error("not an object");
      overrides = {
        version: 2,
        courses: obj.courses || {},
        card_order: obj.card_order || {},
        brand_order: obj.brand_order || null,
        custom_brands: obj.custom_brands || {},
        custom_courses: Array.isArray(obj.custom_courses) ? obj.custom_courses : [],
      };
      rebuildCourseIndex();
      pruneStaleOverrides();
      rebuildCourseIndex();
      saveOverrides(false);
      renderBoard();
      const customCount = (overrides.custom_courses || []).length;
      $("#kpiCourses").textContent = String(baseline.courses.length + customCount);
      toast("Imported overrides · saved", "success");
    } catch (e) {
      toast("Invalid JSON file", "error");
      console.error(e);
    }
  };
  reader.readAsText(file);
}

function slugify(s) {
  const t = String(s || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return t || "course";
}

function uniqueSlug(base) {
  let s = base;
  let i = 2;
  while (courseBySlug[s]) {
    s = `${base}-${i++}`;
  }
  return s;
}

function populateAcBrandSelect() {
  const sel = $("#acBrandExisting");
  if (!sel) return;
  sel.innerHTML = "";
  getMergedBrandOrder().forEach(key => {
    const m = getBrandMeta(key);
    if (!m) return;
    const opt = document.createElement("option");
    opt.value = key;
    opt.textContent = m.label;
    sel.appendChild(opt);
  });
}

function openAddModal() {
  populateAcBrandSelect();
  $("#acModal")?.classList.add("show");
  $("#acModal")?.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
  setTimeout(() => $("#acName")?.focus(), 100);
}

function closeAddModal() {
  $("#acModal")?.classList.remove("show");
  $("#acModal")?.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

function submitAddCourse() {
  const name = ($("#acName").value || "").trim();
  if (!name) {
    toast("Course name is required", "error");
    return;
  }

  const category = ($("#acCategory").value || "cert").trim();
  const vendor = ($("#acVendor").value || "").trim() || "Vendor";
  const badge = ($("#acBadge").value || "Cert").trim();
  const badgeVariant = ($("#acBadgeVariant").value || "").trim();
  const description = ($("#acDesc").value || "").trim();
  const level = ($("#acLevel").value || "").trim() || "Foundation";
  const rating = Number($("#acRating").value) || 4.8;
  const reviews = Number($("#acReviews").value) || 0;
  const enrolled = Number($("#acEnrolled").value) || 1000;
  const cardHref = ($("#acCardHref").value || "").trim() || "#";

  const mode =
    (document.querySelector('input[name="acBrandMode"]:checked') || {}).value || "existing";
  let brandKey;

  if (mode === "new") {
    brandKey = slugify($("#acNewBrandKey").value || $("#acNewBrandLabel").value);
    if (!brandKey || brandKey.length < 2) {
      toast("New vendor key is invalid (use letters, numbers, hyphens)", "error");
      return;
    }
    if (baseline.brand_meta[brandKey]) {
      toast("That vendor key already exists — pick another or use Existing vendor", "error");
      return;
    }
    const label = ($("#acNewBrandLabel").value || "").trim() || brandKey;
    const tagline = ($("#acNewBrandTag").value || "").trim();
    const color = ($("#acNewBrandColor").value || "").trim() || "#1d4ed8";
    const tint = ($("#acNewBrandTint").value || "").trim() || "#eff6ff";
    overrides.custom_brands[brandKey] = {
      key: brandKey,
      label,
      tagline,
      color,
      color_tint: tint,
    };
  } else {
    brandKey = ($("#acBrandExisting").value || "").trim();
    if (!brandKey) {
      toast("Select a vendor section", "error");
      return;
    }
  }

  const baseSlug = slugify($("#acSlug").value || name);
  const slug = uniqueSlug(baseSlug);

  const row = {
    slug,
    brand: brandKey,
    category,
    vendor,
    badge,
    badge_variant: badgeVariant,
    name,
    description,
    level,
    rating,
    reviews,
    enrolled,
    has_detail_page: false,
    card_href: cardHref,
  };

  overrides.custom_courses = overrides.custom_courses || [];
  overrides.custom_courses.push(row);

  const prevOrder =
    overrides.card_order[brandKey] || baseline.card_order[brandKey] || [];
  overrides.card_order[brandKey] = prevOrder.includes(slug) ? prevOrder : [...prevOrder, slug];

  rebuildCourseIndex();
  saveOverrides(false);
  renderBoard();
  $("#kpiCourses").textContent = String(baseline.courses.length + (overrides.custom_courses || []).length);
  updateStorageStatus();
  toast("Custom course added", "success");
  closeAddModal();
}

let toastTimer = null;
function toast(msg, kind = "") {
  const el = $("#adToast");
  el.textContent = msg;
  el.className = "ad-toast show " + kind;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.remove("show");
  }, 2400);
}

function bindUI() {
  $$(".ad-chip").forEach(b =>
    b.addEventListener("click", () => {
      $$(".ad-chip").forEach(x => x.classList.remove("on"));
      b.classList.add("on");
      activeFilter = b.dataset.cat;
      applyFilter();
    })
  );

  $("#adSearch").addEventListener("input", () => applyFilter());
  $("#adShowEditedOnly").addEventListener("change", () => applyFilter());

  document.addEventListener("click", e => {
    const editBtn = e.target.closest(".acc-edit");
    if (editBtn) {
      void openDrawer(editBtn.dataset.slug);
      return;
    }
    const revertBtn = e.target.closest(".acc-revert");
    if (revertBtn && !revertBtn.disabled) {
      revertCard(revertBtn.dataset.slug);
      return;
    }
  });

  $("#adDrawerClose").addEventListener("click", closeDrawer);
  $("#adDrawerShade").addEventListener("click", closeDrawer);
  $("#adDrawerApply").addEventListener("click", applyDrawer);
  $("#adDrawerRevert").addEventListener("click", () => {
    if (!activeSlug) return;
    revertCard(activeSlug);
    closeDrawer();
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      if ($("#acModal")?.classList.contains("show")) closeAddModal();
      if ($("#adDrawer").classList.contains("show")) closeDrawer();
    }
  });

  $("#adBtnSave").addEventListener("click", () => saveOverrides());

  $("#adBtnReset").addEventListener("click", resetAll);
  $("#adBtnExport").addEventListener("click", exportJSON);
  $("#adBtnImport").addEventListener("click", () => $("#adFile").click());
  $("#adFile").addEventListener("change", e => {
    const f = e.target.files?.[0];
    if (f) importJSON(f);
    e.target.value = "";
  });

  $("#adBtnAddCourse")?.addEventListener("click", openAddModal);
  $("#acModalClose")?.addEventListener("click", closeAddModal);
  $("#acModalShade")?.addEventListener("click", closeAddModal);
  $("#acCancel")?.addEventListener("click", closeAddModal);
  $("#acSubmit")?.addEventListener("click", submitAddCourse);

  $$('input[name="acBrandMode"]').forEach(r => {
    r.addEventListener("change", () => {
      const mode =
        (document.querySelector('input[name="acBrandMode"]:checked') || {}).value || "existing";
      $("#acBrandExistingWrap").style.display = mode === "existing" ? "" : "none";
      $("#acBrandNewWrap").style.display = mode === "new" ? "" : "none";
    });
  });

  const board = $("#adBoard");
  board.addEventListener("dragstart", onDragStart);
  board.addEventListener("dragover", onDragOver);
  board.addEventListener("dragleave", onDragLeave);
  board.addEventListener("drop", onDrop);
  board.addEventListener("dragend", cleanupDrag);
}

function readSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY) || sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj || obj.user !== ADMIN_USER) return null;
    if (obj.expiresAt && Date.now() > obj.expiresAt) return null;
    return obj;
  } catch (e) {
    return null;
  }
}

function writeSession(remember) {
  const obj = {
    user: ADMIN_USER,
    issuedAt: Date.now(),
    expiresAt: remember ? Date.now() + SESSION_TTL_MS : null,
  };
  if (remember) localStorage.setItem(SESSION_KEY, JSON.stringify(obj));
  else sessionStorage.setItem(SESSION_KEY, JSON.stringify(obj));
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(SESSION_KEY);
}

function showLogin() {
  document.body.classList.add("ad-locked");
  setTimeout(() => $("#alUser")?.focus(), 60);
}

function hideLogin() {
  document.body.classList.remove("ad-locked");
}

function flashError(msg) {
  const err = $("#alError");
  err.hidden = false;
  err.textContent = msg;
  err.style.animation = "none";
  err.offsetHeight;
  err.style.animation = "";
}

function bindLogin() {
  const form = $("#adLoginForm");
  if (!form) return;
  form.addEventListener("submit", e => {
    e.preventDefault();
    const u = ($("#alUser").value || "").trim();
    const p = $("#alPass").value || "";
    const remember = $("#alRemember").checked;
    if (u === ADMIN_USER && p === ADMIN_PASS) {
      writeSession(remember);
      hideLogin();
      $("#alError").hidden = true;
      $("#alPass").value = "";
      bootApp();
    } else {
      flashError("Incorrect username or password.");
      $("#alPass").select();
    }
  });

  const toggle = $("#alPwdToggle");
  toggle?.addEventListener("click", () => {
    const inp = $("#alPass");
    const showing = inp.type === "text";
    inp.type = showing ? "password" : "text";
    toggle.classList.toggle("on", !showing);
    toggle.setAttribute("aria-label", showing ? "Show password" : "Hide password");
  });
}

let booted = false;
async function bootApp() {
  if (booted) return;
  booted = true;
  await init();
  $("#adBtnLogout")?.addEventListener("click", () => {
    if (!confirm("Sign out of the admin panel?")) return;
    clearSession();
    location.reload();
  });
}

bindLogin();
if (readSession()) {
  hideLogin();
  bootApp();
} else {
  showLogin();
}
