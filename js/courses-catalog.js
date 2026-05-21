/**
 * Course catalog: nav mega-menu deep links + homepage search.
 */
(function () {
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
        var match = filterCat === "all" || c.dataset.cat === filterCat;
        if (brand && block.dataset.brand !== brand) match = false;
        if (match) {
          c.classList.add("show");
          visible++;
        } else {
          c.classList.remove("show");
        }
      });
      block.classList.toggle("b-hide", visible === 0);
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

  function readNavIntent() {
    var params = new URLSearchParams(window.location.search);
    var cat = params.get("cat") || sessionStorage.getItem("nxCatalogCat") || "";
    var brand = params.get("brand") || sessionStorage.getItem("nxCatalogBrand") || "";
    if (!cat && !brand) return;
    sessionStorage.removeItem("nxCatalogCat");
    sessionStorage.removeItem("nxCatalogBrand");
    applyCatalogFilter(cat || "all", brand || "");
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest(".nav-courses-vendor, .nav-courses-section-link");
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
    var meta = document.getElementById("catalogSearchMeta");
    var clearBtn = document.querySelector(".catalog-search-clear");
    if (!input) return;

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

    function runSearch() {
      var q = input.value.trim().toLowerCase();
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
          visibleBrands++;
        }
      });

      if (meta) {
        if (!q) {
          meta.textContent = "";
        } else if (visibleCards === 0) {
          meta.textContent = "No courses match your search. Try another keyword or vendor.";
        } else {
          meta.textContent =
            visibleCards +
            (visibleCards === 1 ? " course" : " courses") +
            " in " +
            visibleBrands +
            (visibleBrands === 1 ? " vendor" : " vendors");
        }
      }
    }

    input.addEventListener("input", runSearch);
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        input.value = "";
        input.focus();
        document.querySelectorAll(".ftab").forEach(function (btn) {
          btn.classList.toggle("on", btn.dataset.cat === "all");
        });
        document.querySelectorAll(".brand-block").forEach(function (block) {
          block.classList.remove("b-hide");
          block.querySelectorAll(".cc").forEach(function (c) {
            c.classList.add("show");
          });
        });
        runSearch();
      });
    }
  }

  function init() {
    readNavIntent();
    initSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
