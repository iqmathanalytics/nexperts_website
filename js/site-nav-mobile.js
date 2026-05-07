(function () {
  function closeMenu(nav, btn) {
    nav.classList.remove('site-nav-open');
    document.body.classList.remove('site-nav-open');
    if (btn) {
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Open menu');
    }
  }

  function openMenu(nav, btn) {
    nav.classList.add('site-nav-open');
    document.body.classList.add('site-nav-open');
    if (btn) {
      btn.setAttribute('aria-expanded', 'true');
      btn.setAttribute('aria-label', 'Close menu');
    }
  }

  function init() {
    var nav = document.querySelector('nav.site-nav');
    var btn = document.getElementById('siteNavMenuBtn');
    if (!nav || !btn) return;

    // Keep the "Nexperts AI" overlay precisely centered under the nav button.
    function positionAiOverlay() {
      var aiBtn = document.querySelector('nav.site-nav .nav-right .nav-ai');
      var overlay = document.querySelector('.hero-ai-overlay');
      if (!aiBtn || !overlay) return;

      var navRect = nav.getBoundingClientRect();
      var btnRect = aiBtn.getBoundingClientRect();
      var centerX = btnRect.left + btnRect.width / 2;

      overlay.style.left = Math.round(centerX) + 'px';
      overlay.style.right = 'auto';
      overlay.style.transform = 'translateX(-50%)';
      overlay.style.top = Math.round(navRect.bottom + 18) + 'px';
    }

    // Mobile-only: keep the small "Click here" hint centered under the same button.
    function positionAiMobileHint() {
      if (!window.matchMedia('(max-width: 560px)').matches) return;
      var aiBtn = document.querySelector('nav.site-nav .nav-right .nav-ai');
      var hint = document.querySelector('nav.site-nav .nav-right .nav-ai-mobile-hint');
      if (!aiBtn || !hint) return;

      var btnRect = aiBtn.getBoundingClientRect();
      var centerX = btnRect.left + btnRect.width / 2;

      hint.style.left = Math.round(centerX) + 'px';
      hint.style.top = Math.round(btnRect.bottom + 10) + 'px';
      hint.style.transform = 'translateX(-50%)';
    }

    var backdrop = nav.nextElementSibling;
    if (!backdrop || !backdrop.classList.contains('nav-drawer-backdrop')) {
      backdrop = null;
    }

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var open = nav.classList.toggle('site-nav-open');
      document.body.classList.toggle('site-nav-open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      positionAiOverlay();
      positionAiMobileHint();
    });

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        closeMenu(nav, btn);
      });
    }

    nav.querySelectorAll('#sitePrimaryNav a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.matchMedia('(max-width: 1024px)').matches) {
          closeMenu(nav, btn);
        }
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('site-nav-open')) {
        closeMenu(nav, btn);
        btn.focus();
      }
    });

    window.addEventListener(
      'resize',
      function () {
        positionAiOverlay();
        positionAiMobileHint();
        if (!window.matchMedia('(max-width: 1024px)').matches) {
          closeMenu(nav, btn);
        }
      },
      { passive: true }
    );

    // Initial + late (fonts/layout) positioning
    positionAiOverlay();
    positionAiMobileHint();
    window.requestAnimationFrame(positionAiOverlay);
    window.requestAnimationFrame(positionAiMobileHint);
    window.addEventListener('scroll', positionAiMobileHint, { passive: true });
    window.addEventListener('load', positionAiOverlay, { passive: true });
    window.addEventListener('load', positionAiMobileHint, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
