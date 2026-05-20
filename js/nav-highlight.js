/**
 * Sliding highlight for .nav-links — only top-level items + Explore trigger.
 * Ignores links inside .nav-addons-panel so the bar does not jump on dropdown hover.
 */
(function () {
  function navHighlightTargets(navLinks) {
    var targets = Array.prototype.slice.call(
      navLinks.querySelectorAll(":scope > li > a")
    );
    var addonsBtn = navLinks.querySelector(".nav-addons-trigger");
    if (addonsBtn) targets.push(addonsBtn);
    return targets;
  }

  function setupNavHighlight() {
    var navLinks = document.querySelector(".nav-links");
    if (!navLinks) return;
    var links = navHighlightTargets(navLinks);
    var indicator = navLinks.querySelector(".nav-highlight");
    if (!indicator || !links.length) return;

    var activeLink = null;
    var hoverLink = null;
    var rafId = 0;
    var pendingMove = null;

    function moveTo(link, animate) {
      if (animate === undefined) animate = true;
      if (!link || !indicator) return;
      var navRect = navLinks.getBoundingClientRect();
      var linkRect = link.getBoundingClientRect();
      if (!animate) indicator.style.transition = "none";
      indicator.style.left = linkRect.left - navRect.left + "px";
      indicator.style.width = linkRect.width + "px";
      indicator.style.opacity = "1";
      if (!animate) {
        requestAnimationFrame(function () {
          indicator.style.transition = "";
        });
      }
    }

    function queueMove(link, animate) {
      pendingMove = { link: link, animate: animate };
      if (rafId) return;
      rafId = requestAnimationFrame(function () {
        rafId = 0;
        if (pendingMove) moveTo(pendingMove.link, pendingMove.animate);
        pendingMove = null;
      });
    }

    function setActive(link, animate) {
      if (animate === undefined) animate = true;
      if (!link) return;
      if (activeLink === link) {
        if (!hoverLink) queueMove(link, animate);
        return;
      }
      if (activeLink) activeLink.classList.remove("active");
      activeLink = link;
      activeLink.classList.add("active");
      if (!hoverLink) queueMove(activeLink, animate);
    }

    var initial =
      links.find(function (a) {
        return a.classList.contains("active");
      }) ||
      links.find(function (a) {
        var href = (a.getAttribute("href") || "").trim();
        return href === "/" || href === "";
      }) ||
      links[0];
    setActive(initial, false);

    var sectionLinks = links
      .map(function (a) {
        return { a: a, id: (a.getAttribute("href") || "").replace("#", "") };
      })
      .filter(function (x) {
        return x.id && document.getElementById(x.id);
      });

    var heroSection = document.querySelector(".hero.hero-split");
    var homeLink =
      links.find(function (a) {
        var href = (a.getAttribute("href") || "").trim();
        return (
          href === "/" ||
          href === "" ||
          a.textContent.trim().toLowerCase() === "home"
        );
      }) || links[0];

    function refreshActiveByScroll() {
      if (!sectionLinks.length && !heroSection) return;
      var scrollTop = window.scrollY || document.documentElement.scrollTop || 0;
      var hardHeroZone = window.innerHeight * 0.72;
      if (scrollTop <= hardHeroZone) {
        setActive(homeLink);
        return;
      }
      if (heroSection) {
        var heroRect = heroSection.getBoundingClientRect();
        var navMarkerY = window.innerHeight * 0.32;
        if (heroRect.top <= navMarkerY && heroRect.bottom >= navMarkerY) {
          setActive(homeLink);
          return;
        }
      }
      if (scrollTop <= 24) {
        setActive(homeLink);
        return;
      }
      if (!sectionLinks.length) return;
      var marker = scrollTop + window.innerHeight * 0.32;
      var current = null;
      sectionLinks.forEach(function (item) {
        var section = document.getElementById(item.id);
        if (section && section.offsetTop <= marker) current = item;
      });
      if (current) setActive(current.a);
      else setActive(homeLink);
    }

    var ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(function () {
          refreshActiveByScroll();
          ticking = false;
        });
      },
      { passive: true }
    );
    if (sectionLinks.length || heroSection) {
      refreshActiveByScroll();
      window.addEventListener("load", refreshActiveByScroll);
      window.addEventListener("pageshow", refreshActiveByScroll);
      window.addEventListener("hashchange", refreshActiveByScroll);
    }

    links.forEach(function (link) {
      link.addEventListener("mouseenter", function () {
        hoverLink = link;
        queueMove(link, true);
      });
      link.addEventListener("focus", function () {
        hoverLink = link;
        queueMove(link, true);
      });
      link.addEventListener("click", function () {
        setActive(link);
      });
    });

    navLinks.addEventListener("mouseleave", function () {
      hoverLink = null;
      if (activeLink) queueMove(activeLink, true);
    });

    window.addEventListener("resize", function () {
      if (activeLink) queueMove(activeLink, false);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupNavHighlight);
  } else {
    setupNavHighlight();
  }
})();
