/**
 * Related courses from the same vendor — injected at the bottom of #sec-overview.
 */
(function () {
  var ROOT_CANONICAL = {
    ccna: true,
    "python-bootcamp": true,
    "data-science-with-python": true,
    ceh: true,
  };

  var SLUG_ALIASES = {
    "ceh-v13-ai": "ceh",
  };

  function canonicalSlug(slug) {
    return SLUG_ALIASES[slug] || slug;
  }

  function coursePath(slug) {
    slug = canonicalSlug(slug);
    return ROOT_CANONICAL[slug] ? "/" + slug : "/courses/" + slug;
  }

  function slugFromPath(pathname) {
    var parts = pathname.replace(/\/+$/, "").split("/").filter(Boolean);
    if (!parts.length) return "";
    if (parts[0] === "courses" && parts[1]) return parts[1];
    if (parts.length === 1) return parts[0];
    return "";
  }

  function findBrandByLabel(data, label) {
    if (!label || !data.brand_meta) return "";
    var norm = label.trim().toLowerCase();
    var keys = Object.keys(data.brand_meta);
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      var meta = data.brand_meta[key];
      if (meta && meta.label && meta.label.toLowerCase() === norm) return key;
    }
    return "";
  }

  function detectBrand(data, course) {
    if (course && course.brand) return course.brand;

    var vendorEl = document.querySelector(".cb-vendor");
    if (vendorEl) {
      var vendorText = vendorEl.textContent.replace(/\s*Authorized\s*$/i, "").trim();
      var fromVendor = findBrandByLabel(data, vendorText);
      if (fromVendor) return fromVendor;
    }

    var rows = document.querySelectorAll(".smeta-row");
    for (var r = 0; r < rows.length; r++) {
      var label = rows[r].querySelector("span");
      if (label && /cert body/i.test(label.textContent)) {
        var strong = rows[r].querySelector("strong");
        if (strong) {
          var fromCert = findBrandByLabel(data, strong.textContent.trim());
          if (fromCert) return fromCert;
        }
      }
    }

    return "";
  }

  function renderRelated(data, brandKey, currentSlug) {
    var overview = document.getElementById("sec-overview");
    if (!overview || overview.querySelector(".related-courses")) return;

    var brand = data.brand_meta && data.brand_meta[brandKey];
    var related = (data.courses || []).filter(function (c) {
      if (!c || c.brand !== brandKey) return false;
      if (canonicalSlug(c.slug) === canonicalSlug(currentSlug)) return false;
      if (c.has_detail_page === false) return false;
      return true;
    });

    if (related.length < 1) return;

    related.sort(function (a, b) {
      return (a.name || a.slug).localeCompare(b.name || b.slug);
    });

    var accent = (brand && brand.color) || "#1d4ed8";
    var tint = (brand && brand.color_tint) || "rgba(29, 78, 216, 0.06)";
    var vendorLabel = (brand && brand.label) || "this vendor";

    var wrap = document.createElement("div");
    wrap.className = "related-courses";
    wrap.setAttribute("aria-label", "Related courses from " + vendorLabel);
    wrap.style.setProperty("--related-accent", accent);
    wrap.style.setProperty("--related-bg", tint);
    wrap.style.setProperty(
      "--related-border",
      accent.indexOf("#") === 0 ? accent + "38" : "rgba(29, 78, 216, 0.22)"
    );

    var head = document.createElement("div");
    head.className = "related-courses-head";
    head.innerHTML =
      '<p class="related-courses-eyebrow">Related courses</p>' +
      '<span class="related-courses-vendor">More from ' +
      escapeHtml(vendorLabel) +
      "</span>";

    var track = document.createElement("div");
    track.className = "related-courses-track";
    track.setAttribute("role", "list");

    related.forEach(function (c) {
      var a = document.createElement("a");
      a.className = "related-course-btn";
      a.href = coursePath(c.slug);
      a.setAttribute("role", "listitem");
      a.innerHTML =
        escapeHtml(c.name || c.slug) +
        ' <span class="related-course-btn-arrow" aria-hidden="true">→</span>';
      track.appendChild(a);
    });

    wrap.appendChild(head);
    wrap.appendChild(track);
    overview.appendChild(wrap);
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function init() {
    var slug = slugFromPath(window.location.pathname);
    if (!slug) return;

    fetch("/admin/admin-data.json", { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("catalog unavailable");
        return res.json();
      })
      .then(function (data) {
        var courses = data.courses || [];
        var current = null;
        for (var i = 0; i < courses.length; i++) {
          if (canonicalSlug(courses[i].slug) === canonicalSlug(slug)) {
            current = courses[i];
            break;
          }
        }
        var brandKey = detectBrand(data, current);
        if (!brandKey) return;
        renderRelated(data, brandKey, slug);
      })
      .catch(function () {
        /* silent — optional enhancement */
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
