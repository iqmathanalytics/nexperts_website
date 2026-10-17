/**
 * Course catalog: nav mega-menu deep links + homepage search.
 */
(function () {
  function cardCats(card) {
    var raw = card.getAttribute("data-cats");
    if (raw && raw.trim()) {
      return raw.trim().split(/\s+/);
    }
    var single = card.getAttribute("data-cat") || "";
    return single ? [single] : [];
  }

  function cardMatchesFilter(card, filterCat) {
    if (!filterCat || filterCat === "all") return true;
    if (filterCat === "ai" && card.getAttribute("data-ai") === "1") return true;
    return cardCats(card).indexOf(filterCat) !== -1;
  }

  /** Match sparse-vendor layout: 1→n1, 2→n2, else full 3-col grid. */
  function syncBrandBlockSize(block, visible) {
    block.classList.remove("brand-block--n1", "brand-block--n2");
    if (visible === 1) block.classList.add("brand-block--n1");
    else if (visible === 2) block.classList.add("brand-block--n2");
    var label = block.querySelector(".bh-count");
    if (label && visible > 0) {
      label.innerHTML =
        "<span>" + visible + "</span> course" + (visible === 1 ? "" : "s");
    }
  }

  function applyCatalogFilter(cat, brand) {
    var section = document.getElementById("courses");
    if (!section) return;

    var filterCat = cat && cat !== "all" ? cat : "all";
    document.querySelectorAll(".ftab").forEach(function (btn) {
      btn.classList.toggle("on", btn.dataset.cat === filterCat);
    });
    document.querySelectorAll(".brand-block").forEach(function (block) {
      var visible = 0;
      block.querySelectorAll(".cc").forEach(function (c) {
        var match = cardMatchesFilter(c, filterCat);
        if (brand && block.dataset.brand !== brand) match = false;
        if (match) {
          c.classList.add("show");
          visible++;
        } else {
          c.classList.remove("show");
        }
      });
      block.classList.toggle("b-hide", visible === 0);
      if (visible > 0) syncBrandBlockSize(block, visible);
    });

    if (brand) {
      var target = document.querySelector(
        '.brand-block[data-brand="' + brand.replace(/"/g, '\\"') + '"]'
      );
      if (target) {
        setTimeout(function () {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 80);
      }
    }

    if (section) {
      setTimeout(function () {
        section.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 40);
    }
  }

  function cardText(card) {
    var name = card.querySelector(".cname2");
    var desc = card.querySelector(".cdesc2");
    return (
      (name ? name.textContent : "") +
      " " +
      (desc ? desc.textContent : "") +
      " " +
      (card.dataset.vendor || "") +
      " " +
      (card.dataset.brand || "") +
      " " +
      (card.dataset.level || "")
    ).toLowerCase();
  }

  function syncSearchInputs(q) {
    var value = q || "";
    var catalog = document.getElementById("catalogSearch");
    if (catalog) catalog.value = value;
    document
      .querySelectorAll("form[data-nx-course-search] input[name='q']")
      .forEach(function (el) {
        el.value = value;
      });
  }

  function runCatalogSearch(q) {
    var input = document.getElementById("catalogSearch");
    var meta = document.getElementById("catalogSearchMeta");
    var clearBtn = document.querySelector(".catalog-search-clear");
    if (!document.getElementById("courses")) return;

    q = (q || "").trim().toLowerCase();
    if (clearBtn) clearBtn.hidden = !q;

    var visibleCards = 0;
    var visibleBrands = 0;

    document.querySelectorAll(".brand-block").forEach(function (block) {
      var blockVisible = 0;
      block.querySelectorAll(".cc").forEach(function (card) {
        var match = !q || cardText(card).indexOf(q) !== -1;
        if (match) {
          card.classList.add("show");
          blockVisible++;
          visibleCards++;
        } else {
          card.classList.remove("show");
        }
      });
      if (blockVisible === 0) {
        block.classList.add("b-hide");
      } else {
        block.classList.remove("b-hide");
        syncBrandBlockSize(block, blockVisible);
        visibleBrands++;
      }
    });

    if (meta) {
      if (!q) {
        meta.textContent = "";
      } else if (visibleCards === 0) {
        meta.textContent =
          "No courses match your search. Try another keyword or vendor.";
      } else {
        meta.textContent =
          visibleCards +
          (visibleCards === 1 ? " course" : " courses") +
          " in " +
          visibleBrands +
          (visibleBrands === 1 ? " vendor" : " vendors");
      }
    }

    if (input && input.value.trim().toLowerCase() !== q) {
      input.value = q;
    }
  }

  function goToCatalogSearch(q) {
    q = (q || "").trim();
    syncSearchInputs(q);

    if (!document.getElementById("courses")) {
      if (q) sessionStorage.setItem("nxCatalogQ", q);
      else sessionStorage.removeItem("nxCatalogQ");
      var url = q
        ? "/?q=" + encodeURIComponent(q) + "#courses"
        : "/#courses";
      window.location.href = url;
      return;
    }

    document.querySelectorAll(".ftab").forEach(function (btn) {
      btn.classList.toggle("on", btn.dataset.cat === "all");
    });
    runCatalogSearch(q);
    var section = document.getElementById("courses");
    if (section) {
      setTimeout(function () {
        section.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 40);
    }
  }

  function readNavIntent() {
    var params = new URLSearchParams(window.location.search);
    var q = params.get("q") || sessionStorage.getItem("nxCatalogQ") || "";
    if (q) {
      sessionStorage.removeItem("nxCatalogQ");
      goToCatalogSearch(q);
      return;
    }

    var cat = params.get("cat") || sessionStorage.getItem("nxCatalogCat") || "";
    var brand =
      params.get("brand") || sessionStorage.getItem("nxCatalogBrand") || "";
    if (!cat && !brand) return;
    sessionStorage.removeItem("nxCatalogCat");
    sessionStorage.removeItem("nxCatalogBrand");
    applyCatalogFilter(cat || "all", brand || "");
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest(
      ".nav-courses-vendor, .nav-courses-section-link"
    );
    if (!link || !link.closest(".nav-courses-panel")) return;
    var cat = link.getAttribute("data-nav-cat") || "";
    var brand = link.getAttribute("data-nav-brand") || "";
    if (!document.getElementById("courses")) {
      sessionStorage.setItem("nxCatalogCat", cat);
      sessionStorage.setItem("nxCatalogBrand", brand);
      return;
    }
    e.preventDefault();
    applyCatalogFilter(cat, brand);
  });

  function initSearch() {
    var input = document.getElementById("catalogSearch");
    var clearBtn = document.querySelector(".catalog-search-clear");

    if (input) {
      input.addEventListener("input", function () {
        syncSearchInputs(input.value);
        runCatalogSearch(input.value);
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        syncSearchInputs("");
        if (input) input.focus();
        document.querySelectorAll(".ftab").forEach(function (btn) {
          btn.classList.toggle("on", btn.dataset.cat === "all");
        });
        document.querySelectorAll(".brand-block").forEach(function (block) {
          block.classList.remove("b-hide");
          var n = 0;
          block.querySelectorAll(".cc").forEach(function (c) {
            c.classList.add("show");
            n++;
          });
          syncBrandBlockSize(block, n);
        });
        runCatalogSearch("");
      });
    }

    document
      .querySelectorAll("form[data-nx-course-search]")
      .forEach(function (form) {
        form.addEventListener("submit", function (e) {
          e.preventDefault();
          var field = form.querySelector("input[name='q']");
          goToCatalogSearch(field ? field.value : "");
        });
      });

    document
      .querySelectorAll("[data-nx-search-hint]")
      .forEach(function (btn) {
        btn.addEventListener("click", function () {
          goToCatalogSearch(btn.getAttribute("data-nx-search-hint") || "");
        });
      });
  }

  function init() {
    document.querySelectorAll(".brand-block").forEach(function (block) {
      var n = block.querySelectorAll(".cc.show").length;
      if (!n) n = block.querySelectorAll(".cc").length;
      if (n) syncBrandBlockSize(block, n);
    });
    initSearch();
    readNavIntent();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
