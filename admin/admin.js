/* Admin · Course Manager
 * --------------------------------------------------------------
 *  Storage model:
 *    localStorage["nexperts_admin_v1"] = {
 *      version: 1,
 *      courses: { [slug]: { name, description, duration, next_intake,
 *                           price, price_original } },
 *      card_order: { [brand]: [slug, slug, ...] },     // optional override
 *      brand_order: [brand, brand, ...]                // optional override
 *    }
 *
 *  Public site reads the same storage via overlay.js to apply edits.
 * -------------------------------------------------------------- */

const STORAGE_KEY = "nexperts_admin_v1";
const SESSION_KEY = "nexperts_admin_session_v1";
const DATA_URL = "admin-data.json";

// Demo credentials. Note: this is a client-side gate — real
// security should run on a server. For the current "no backend"
// stage these creds are good enough to deter casual access.
const ADMIN_USER = "admin";
const ADMIN_PASS = "admin123";
const SESSION_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

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

let baseline = null;          // { brand_meta, brand_order, card_order, courses[] }
let courseBySlug = {};        // slug -> course object (baseline)
let overrides = {};           // mutable working copy in memory
let activeSlug = null;
let activeFilter = "all";

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const escapeHTML = (s = "") =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
   .replace(/"/g, "&quot;").replace(/'/g, "&#039;");

// ---------------------------------------------------------------
// Storage helpers
// ---------------------------------------------------------------
function loadOverrides() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { version: 1, courses: {}, card_order: {}, brand_order: null };
    const obj = JSON.parse(raw);
    return {
      version: 1,
      courses: obj.courses || {},
      card_order: obj.card_order || {},
      brand_order: obj.brand_order || null,
    };
  } catch (e) {
    console.warn("admin: failed to parse storage, starting fresh", e);
    return { version: 1, courses: {}, card_order: {}, brand_order: null };
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

function updateStorageStatus() {
  const total = countEditedCourses();
  const reordered = countReorderedBrands();
  $("#kpiEdited").textContent = total;
  $("#kpiReordered").textContent = reordered;
  const status = $("#adStorageStatus");
  if (!total && !reordered) {
    status.textContent = "No overrides — using baseline";
    status.style.color = "var(--ink4)";
  } else {
    status.textContent = `${total} field edit${total === 1 ? "" : "s"} · ${reordered} brand${reordered === 1 ? "" : "s"} reordered`;
    status.style.color = "var(--blue)";
  }
}

function countEditedCourses() {
  return Object.values(overrides.courses).filter(o => Object.keys(o).length > 0).length;
}
function countReorderedBrands() {
  if (!overrides.card_order) return 0;
  let n = 0;
  for (const k in overrides.card_order) {
    const a = overrides.card_order[k];
    const b = baseline.card_order[k];
    if (!b) continue;
    if (a.length !== b.length || a.some((x, i) => x !== b[i])) n++;
  }
  return n;
}

// ---------------------------------------------------------------
// Resolved course (baseline + override)
// ---------------------------------------------------------------
function resolveCourse(slug) {
  const base = courseBySlug[slug];
  if (!base) return null;
  const ov = overrides.courses[slug] || {};
  return { ...base, ...ov };
}

function isEdited(slug) {
  return !!(overrides.courses[slug] && Object.keys(overrides.courses[slug]).length);
}

// ---------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------
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

  courseBySlug = Object.fromEntries(baseline.courses.map(c => [c.slug, c]));
  overrides = loadOverrides();
  pruneStaleOverrides();

  $("#kpiBrands").textContent = baseline.brand_order.length;
  $("#kpiCourses").textContent = baseline.courses.length;
  $("#kpiPhase1").textContent = baseline.courses.filter(c => c.has_detail_page).length;

  renderBoard();
  bindUI();
  updateStorageStatus();
}

function pruneStaleOverrides() {
  // drop entries whose slug no longer exists
  for (const slug in overrides.courses) {
    if (!courseBySlug[slug]) delete overrides.courses[slug];
  }
  for (const brand in overrides.card_order) {
    overrides.card_order[brand] = overrides.card_order[brand]
      .filter(s => courseBySlug[s]);
  }
}

// ---------------------------------------------------------------
// Render
// ---------------------------------------------------------------
function renderBoard() {
  const board = $("#adBoard");
  board.innerHTML = "";
  const brandOrder = overrides.brand_order || baseline.brand_order;

  brandOrder.forEach(brandKey => {
    const meta = baseline.brand_meta[brandKey];
    if (!meta) return;
    const slugs = (overrides.card_order[brandKey] || baseline.card_order[brandKey] || []).slice();
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

  const initials = meta.label.split(/\s+/).slice(0, 2).map(w => w[0]).join("").toUpperCase();

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

  const editedBadge = isEdited(slug) ? `<span class="acc-edited">Edited</span>` : "";
  const detailBits = c.has_detail_page
    ? [
        ["Duration", c.duration],
        ["Intake", c.next_intake],
        ["Price", c.price],
      ].map(([k, v]) => `<i class="${v ? "has-val" : ""}">${escapeHTML(k)}: ${escapeHTML(v || "—")}</i>`).join("")
    : `<i class="no-detail">Catalog-only · no detail page</i>`;

  card.innerHTML = `
    <div class="acc-head">
      <div class="acc-handle" title="Drag to reorder" draggable="true">⋮⋮</div>
      <div class="acc-vendor">
        ${escapeHTML(c.vendor)} · ${escapeHTML(c.badge)}
        ${editedBadge}
      </div>
    </div>
    <div class="acc-name">${escapeHTML(c.name)}</div>
    <div class="acc-desc">${escapeHTML(c.description)}</div>
    <div class="acc-meta">${detailBits}</div>
    <div class="acc-actions">
      <button class="acc-edit" data-slug="${slug}">✎ Edit course</button>
      <button class="acc-revert" data-slug="${slug}" ${isEdited(slug) ? "" : "disabled style='opacity:.4;cursor:not-allowed'"}>Revert</button>
    </div>
  `;
  return card;
}

function refreshCardInPlace(slug) {
  const old = $(`.acc[data-slug="${CSS.escape(slug)}"]`);
  if (!old) return;
  const block = old.closest(".bblock");
  const meta = baseline.brand_meta[block.dataset.brand];
  const fresh = renderCard(slug, meta);
  old.replaceWith(fresh);
  applyFilter();
}

// ---------------------------------------------------------------
// Filter / search
// ---------------------------------------------------------------
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
      const matchEdited = !onlyEdited || isEdited(slug);
      const ok = matchCat && matchSearch && matchEdited;
      card.style.display = ok ? "" : "none";
      if (ok) visible++;
    });
    block.classList.toggle("b-hide", visible === 0);
  });
}

// ---------------------------------------------------------------
// Drag & drop (within the same brand grid only)
// ---------------------------------------------------------------
let dragSrc = null;

function onDragStart(e) {
  const handle = e.target;
  if (!handle.classList.contains("acc-handle")) return;
  const card = handle.closest(".acc");
  if (!card) return;
  dragSrc = card;
  card.classList.add("dragging");
  e.dataTransfer.effectAllowed = "move";
  // Some browsers require non-empty data
  try { e.dataTransfer.setData("text/plain", card.dataset.slug); } catch (_) {}
}

function onDragOver(e) {
  if (!dragSrc) return;
  const card = e.target.closest(".acc");
  if (!card || card === dragSrc) return;
  if (card.dataset.brand !== dragSrc.dataset.brand) return; // same brand only
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
  if (!target || target === dragSrc) { cleanupDrag(); return; }
  if (target.dataset.brand !== dragSrc.dataset.brand) { cleanupDrag(); return; }
  e.preventDefault();

  const grid = target.parentNode;
  const rect = target.getBoundingClientRect();
  const before = (e.clientY - rect.top) < rect.height / 2;
  grid.insertBefore(dragSrc, before ? target : target.nextSibling);

  // Persist new order for this brand
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

// ---------------------------------------------------------------
// Drawer (edit form)
// ---------------------------------------------------------------
function openDrawer(slug) {
  activeSlug = slug;
  const c = resolveCourse(slug);
  if (!c) return;

  $("#adDrawerEyebrow").textContent = `${c.vendor} · ${c.badge}`;
  $("#adDrawerTitle").textContent = c.name;

  const body = $("#adDrawerBody");
  let html = "";

  // Catalog fields (always shown)
  html += `<div class="ad-section"><h4>Catalog card <span class="ad-section-tag">Visible on landing page</span></h4>`;
  FIELDS_CATALOG.forEach(f => { html += renderField(f, c[f] || ""); });
  html += `</div>`;

  // Detail fields (Phase 1 only get a useful preview surface)
  html += `<div class="ad-section"><h4>Course detail page <span class="ad-section-tag">${c.has_detail_page ? `course_pages/${c.slug}.html` : "Not yet published"}</span></h4>`;
  if (!c.has_detail_page) {
    html += `<div class="ad-no-detail">This course doesn't have a detail page yet — these fields will be ready when the page is added in a future phase.</div>`;
  }
  FIELDS_DETAIL.forEach(f => { html += renderField(f, c[f] || ""); });
  html += `</div>`;

  body.innerHTML = html;

  // Live "edited" preview as you type
  body.addEventListener("input", onDrawerInput);

  $("#adDrawer").classList.add("show");
  $("#adDrawer").setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";

  setTimeout(() => body.querySelector("input,textarea")?.focus(), 200);
}

function renderField(f, val) {
  const label = FIELD_LABELS[f];
  const placeholder = FIELD_PLACEHOLDERS[f];
  const baseVal = courseBySlug[activeSlug]?.[f] || "";
  const changed = val !== baseVal;
  const input = (f === "description")
    ? `<textarea data-field="${f}" placeholder="${escapeHTML(placeholder)}">${escapeHTML(val)}</textarea>`
    : `<input type="text" data-field="${f}" value="${escapeHTML(val)}" placeholder="${escapeHTML(placeholder)}">`;
  const help = changed ? `<span class="ad-field-help" style="color:var(--blue)">● modified from baseline</span>` : "";
  return `<div class="ad-field"><label>${escapeHTML(label)} ${help}</label>${input}</div>`;
}

function onDrawerInput(e) {
  const f = e.target.dataset.field;
  if (!f) return;
  const baseVal = courseBySlug[activeSlug]?.[f] || "";
  const changed = e.target.value !== baseVal;
  const help = e.target.closest(".ad-field").querySelector(".ad-field-help");
  if (changed && !help) {
    e.target.closest(".ad-field").querySelector("label")
      .insertAdjacentHTML("beforeend", ` <span class="ad-field-help" style="color:var(--blue)">● modified from baseline</span>`);
  } else if (!changed && help) {
    help.remove();
  }
}

function closeDrawer() {
  $("#adDrawer").classList.remove("show");
  $("#adDrawer").setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
  $("#adDrawerBody").removeEventListener("input", onDrawerInput);
  activeSlug = null;
}

function applyDrawer() {
  if (!activeSlug) return;
  const slug = activeSlug;
  const updates = {};
  $$("#adDrawerBody [data-field]").forEach(el => {
    const f = el.dataset.field;
    const v = el.value.trim();
    const baseVal = courseBySlug[slug]?.[f] || "";
    if (v !== baseVal) updates[f] = v;
  });

  if (Object.keys(updates).length) {
    overrides.courses[slug] = updates;
  } else {
    delete overrides.courses[slug];
  }
  saveOverrides();
  refreshCardInPlace(slug);
  closeDrawer();
}

function revertCard(slug) {
  if (!isEdited(slug)) return;
  if (!confirm(`Revert "${courseBySlug[slug].name}" to baseline?`)) return;
  delete overrides.courses[slug];
  saveOverrides();
  refreshCardInPlace(slug);
}

// ---------------------------------------------------------------
// Reset / Export / Import
// ---------------------------------------------------------------
function resetAll() {
  if (!confirm("Reset ALL course edits and order changes back to the shipped baseline?")) return;
  overrides = { version: 1, courses: {}, card_order: {}, brand_order: null };
  saveOverrides(false);
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
        version: 1,
        courses: obj.courses || {},
        card_order: obj.card_order || {},
        brand_order: obj.brand_order || null,
      };
      pruneStaleOverrides();
      saveOverrides(false);
      renderBoard();
      toast("Imported overrides · saved", "success");
    } catch (e) {
      toast("Invalid JSON file", "error");
      console.error(e);
    }
  };
  reader.readAsText(file);
}

// ---------------------------------------------------------------
// Toast
// ---------------------------------------------------------------
let toastTimer = null;
function toast(msg, kind = "") {
  const el = $("#adToast");
  el.textContent = msg;
  el.className = "ad-toast show " + kind;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.classList.remove("show"); }, 2400);
}

// ---------------------------------------------------------------
// UI binding
// ---------------------------------------------------------------
function bindUI() {
  // Filter chips
  $$(".ad-chip").forEach(b => b.addEventListener("click", () => {
    $$(".ad-chip").forEach(x => x.classList.remove("on"));
    b.classList.add("on");
    activeFilter = b.dataset.cat;
    applyFilter();
  }));

  // Search & toggle
  $("#adSearch").addEventListener("input", () => applyFilter());
  $("#adShowEditedOnly").addEventListener("change", () => applyFilter());

  // Card actions (delegated)
  document.addEventListener("click", e => {
    const editBtn = e.target.closest(".acc-edit");
    if (editBtn) { openDrawer(editBtn.dataset.slug); return; }
    const revertBtn = e.target.closest(".acc-revert");
    if (revertBtn && !revertBtn.disabled) { revertCard(revertBtn.dataset.slug); return; }
  });

  // Drawer
  $("#adDrawerClose").addEventListener("click", closeDrawer);
  $("#adDrawerShade").addEventListener("click", closeDrawer);
  $("#adDrawerApply").addEventListener("click", applyDrawer);
  $("#adDrawerRevert").addEventListener("click", () => {
    if (!activeSlug) return;
    revertCard(activeSlug);
    closeDrawer();
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && $("#adDrawer").classList.contains("show")) closeDrawer();
  });

  // Save (manually persists; auto-save also runs on changes)
  $("#adBtnSave").addEventListener("click", () => saveOverrides());

  // Reset / Export / Import
  $("#adBtnReset").addEventListener("click", resetAll);
  $("#adBtnExport").addEventListener("click", exportJSON);
  $("#adBtnImport").addEventListener("click", () => $("#adFile").click());
  $("#adFile").addEventListener("change", e => {
    const f = e.target.files?.[0];
    if (f) importJSON(f);
    e.target.value = "";
  });

  // Drag & drop on board
  const board = $("#adBoard");
  board.addEventListener("dragstart", onDragStart);
  board.addEventListener("dragover", onDragOver);
  board.addEventListener("dragleave", onDragLeave);
  board.addEventListener("drop", onDrop);
  board.addEventListener("dragend", cleanupDrag);
}

// ---------------------------------------------------------------
// Auth gate
// ---------------------------------------------------------------
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
  // re-trigger shake animation
  err.style.animation = "none";
  err.offsetHeight; // reflow
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

// Boot: gate first.
bindLogin();
if (readSession()) {
  hideLogin();
  bootApp();
} else {
  showLogin();
}
