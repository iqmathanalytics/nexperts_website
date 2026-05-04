/**
 * contact.html: pre-select course from URL and/or sessionStorage, scroll to #enquire.
 *
 * URL: ?course=<slug>&title=<optional>&intent=corporate#enquire
 * sessionStorage (set by course pages when clicking Enquire): nx_enquiry_course, nx_enquiry_title, nx_enquiry_intent
 */
(function () {
  "use strict";

  var SS_COURSE = "nx_enquiry_course";
  var SS_TITLE = "nx_enquiry_title";
  var SS_INTENT = "nx_enquiry_intent";

  function decodeSafe(s) {
    try {
      return decodeURIComponent(String(s || "").trim());
    } catch (_) {
      return String(s || "").trim();
    }
  }

  function getCourseSelect() {
    return (
      document.getElementById("nxEnquiryCourse") ||
      (function () {
        var form = document.getElementById("enquiryForm");
        if (!form) return null;
        var el = form.elements.namedItem("course");
        return el && el.tagName === "SELECT" ? el : null;
      })()
    );
  }

  function clearSession() {
    try {
      sessionStorage.removeItem(SS_COURSE);
      sessionStorage.removeItem(SS_TITLE);
      sessionStorage.removeItem(SS_INTENT);
    } catch (_) {}
  }

  function selectCourse(sel, slug, titleDecoded, curriculumExact) {
    var pathFromSlug = slug ? "course_pages/" + String(slug).replace(/^\/+/, "") + ".html" : "";

    if (curriculumExact) {
      var byExact = sel.querySelector('option[data-curriculum="' + curriculumExact + '"]');
      if (byExact) {
        byExact.selected = true;
        sel.dispatchEvent(new Event("change", { bubbles: true }));
        return true;
      }
    }

    if (slug && !/[\r\n]/.test(slug)) {
      var byPath = sel.querySelector('option[data-curriculum="' + pathFromSlug + '"]');
      if (byPath) {
        byPath.selected = true;
        sel.dispatchEvent(new Event("change", { bubbles: true }));
        return true;
      }
      var opts = sel.querySelectorAll("option[data-curriculum]");
      for (var k = 0; k < opts.length; k++) {
        var dc = opts[k].getAttribute("data-curriculum") || "";
        if (dc.indexOf("/" + slug + ".html") !== -1 || dc === pathFromSlug) {
          opts[k].selected = true;
          sel.dispatchEvent(new Event("change", { bubbles: true }));
          return true;
        }
      }
    }

    var course = decodeSafe(slug);
    if (course) {
      for (var i = 0; i < sel.options.length; i++) {
        var o = sel.options[i];
        var t = String(o.textContent || "").trim();
        if (o.value === course || t === course) {
          sel.selectedIndex = i;
          sel.dispatchEvent(new Event("change", { bubbles: true }));
          return true;
        }
        if (t.indexOf(course) === 0) {
          sel.selectedIndex = i;
          sel.dispatchEvent(new Event("change", { bubbles: true }));
          return true;
        }
      }
    }

    if (slug && pathFromSlug) {
      var label = titleDecoded || slug;
      var opt = document.createElement("option");
      opt.setAttribute("data-curriculum", pathFromSlug);
      opt.textContent = label;
      var ref = sel.options[1] || null;
      if (ref) sel.insertBefore(opt, ref);
      else sel.appendChild(opt);
      opt.selected = true;
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    }

    return false;
  }

  function applyIntent(form, intent) {
    if (String(intent || "").toLowerCase().trim() !== "corporate") return;
    var tsel = form.elements.namedItem("type");
    if (!tsel || tsel.tagName !== "SELECT") return;
    var j;
    for (j = 0; j < tsel.options.length; j++) {
      if (String(tsel.options[j].textContent || "").indexOf("Corporate") !== -1) {
        tsel.selectedIndex = j;
        tsel.dispatchEvent(new Event("change", { bubbles: true }));
        break;
      }
    }
  }

  function apply() {
    try {
      var params = new URLSearchParams(window.location.search || "");

      var slug = params.get("course") || "";
      var titleP = params.get("title") || "";
      var curriculum = params.get("curriculum") || "";
      var intent = params.get("intent") || "";

      try {
        if (!slug) slug = sessionStorage.getItem(SS_COURSE) || "";
        if (!titleP) titleP = sessionStorage.getItem(SS_TITLE) || "";
        if (!intent) intent = sessionStorage.getItem(SS_INTENT) || "";
      } catch (_) {}

      slug = String(slug || "").trim();
      curriculum = curriculum ? decodeSafe(curriculum) : "";
      var titleDecoded = titleP ? decodeSafe(titleP) : "";

      if (!slug && !curriculum) return;

      var form = document.getElementById("enquiryForm");
      if (!form) return;
      var sel = getCourseSelect();
      if (!sel) return;

      selectCourse(sel, slug || "", titleDecoded, curriculum || "");
      applyIntent(form, intent);

      clearSession();

      try {
        if (window.location.hash !== "#enquire") {
          history.replaceState(
            null,
            "",
            window.location.pathname + window.location.search + "#enquire"
          );
        }
      } catch (_) {
        try {
          window.location.hash = "enquire";
        } catch (_) {}
      }

      var sec = document.getElementById("enquire");
      if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (_) {
      /* ignore */
    }
  }

  function bind() {
    apply();
    window.addEventListener("load", function () {
      apply();
    });
    setTimeout(apply, 50);
    setTimeout(apply, 300);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
