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
        if (!window.matchMedia('(max-width: 1024px)').matches) {
          closeMenu(nav, btn);
        }
      },
      { passive: true }
    );
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
