# -*- coding: utf-8 -*-
"""Shared site navigation markup for home and inner pages."""
from __future__ import annotations

import html as html_lib

# Label for the mega-menu trigger (was “Add-ons”)
NAV_EXPLORE_LABEL = "Explore"

ADDON_SECTIONS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Workshops & Events",
        [
            ("Workshops", "/workshops"),
            ("Upcoming Events", "/upcoming-events"),
            ("Past Events", "/past-events"),
        ],
    ),
    (
        "Blog",
        [
            ("Blog Home", "/blog"),
            (
                "Data Science Insights",
                "/blog/unlocking-the-power-of-data-science-applications-and-challenges",
            ),
            (
                "CCNA Certification Guide",
                "/blog/ccna-certification-guide",
            ),
            (
                "Network+ Certification Guide",
                "/blog/comptia-network-plus-certification-guide",
            ),
            (
                "Data Science Institutes 2026",
                "/blog/top-data-science-training-institutes-malaysia",
            ),
        ],
    ),
    (
        "Community",
        [
            ("Catalyst for Change", "/catalyst-for-change"),
            ("Empowering Community", "/empowering-community-throught-technology"),
            ("Chinese New Year Event", "/chinese-new-year"),
            ("Tan Boon Heong Event", "/tan-boon-heong-event"),
            ("Nexperts × UiTM", "/nexpert-x-universiti-teknologi-mara"),
        ],
    ),
]

INNER_LINKS: list[tuple[str, str, str]] = [
    ("Home", "/", ""),
    ("Courses", "/#courses", ""),
    ("Roadmaps", "/#roadmap", ""),
    ("Verify", "/#verify", ""),
    ("Career Paths", "/#paths", ""),
    ("Clients", "/#clients", ""),
    ("Beyond", "/Nexperts beyond.html", ""),
    ("Contact", "/contact-us", ""),
    ("About", "/about", ""),
]

HOME_LINKS: list[tuple[str, str, str]] = [
    ("Home", "/", "active"),
    ("Courses", "#courses", ""),
    ("Roadmaps", "#roadmap", ""),
    ("Verify", "#verify", ""),
    ("Career Paths", "#paths", ""),
    ("Clients", "#clients", ""),
    ("Beyond", "Nexperts beyond.html", ""),
    ("Contact", "/contact-us", ""),
    ("About", "/about", ""),
]

COURSE_ROOT_PATHS = frozenset(
    {
        "/ceh",
        "/ccna",
        "/python-bootcamp",
        "/data-science-with-python",
    }
)


def _esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def is_course_path(path: str) -> bool:
    norm = path.rstrip("/") or "/"
    return norm.startswith("/courses/") or norm in COURSE_ROOT_PATHS


def _nav_sep() -> str:
    return '    <li class="nav-sep" aria-hidden="true"><span></span></li>'


NAV_SEP_AFTER = frozenset({"Beyond"})


def _count_label(n: int) -> str:
    return f"{n} course" if n == 1 else f"{n} courses"


COURSE_CATALOG_SECTIONS: list[tuple[str, str]] = [
    ("cert", "Industry Certifications"),
    ("skill", "Skill-Based Programs"),
    ("spec", "Specialized & Compliance"),
]


def _catalog_menu_data() -> tuple[dict[str, dict[str, int]], dict[str, str]]:
    import sys
    from collections import defaultdict
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from _build_catalog import BRANDS, CARDS  # noqa: WPS433

    brand_labels = {key: label for key, label, *_ in BRANDS}
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for brand_key, cat, *_rest in CARDS:
        counts[cat][brand_key] += 1
    return counts, brand_labels


def courses_dropdown_li(*, variant: str, current_path: str = "") -> str:
    counts, brand_labels = _catalog_menu_data()
    courses_href = "#courses" if variant == "home" else "/#courses"
    cols: list[str] = []
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from _build_catalog import BRANDS  # noqa: WPS433

    sections: list[str] = []
    for cat_key, title in COURSE_CATALOG_SECTIONS:
        section_counts = counts.get(cat_key, {})
        total = sum(section_counts.values())
        vendors: list[str] = []
        for brand_key, brand_label, *_rest in BRANDS:
            n = section_counts.get(brand_key, 0)
            if n <= 0:
                continue
            vendors.append(
                f'          <a href="{_esc(courses_href)}" class="nav-courses-vendor" role="menuitem" '
                f'data-nav-cat="{_esc(cat_key)}" data-nav-brand="{_esc(brand_key)}">'
                f'{_esc(brand_label)}<span class="nav-courses-count">{n}</span></a>'
            )
        sections.append(
            f'      <div class="nav-courses-section">\n'
            f'        <div class="nav-courses-section-head">\n'
            f'          <p class="nav-courses-section-title">{_esc(title)}</p>\n'
            f'          <a href="{_esc(courses_href)}" class="nav-courses-section-link" role="menuitem" '
            f'data-nav-cat="{_esc(cat_key)}">{_count_label(total)}</a>\n'
            f'        </div>\n'
            f'        <div class="nav-courses-vendors">\n'
            + "\n".join(vendors)
            + "\n        </div>\n"
            f"      </div>"
        )
    stack = "\n".join(sections)
    trigger_active = " active" if is_course_path(current_path) else ""
    return f"""    <li class="nav-addons-wrap nav-courses-wrap">
      <button type="button" class="nav-addons-trigger nav-courses-trigger nav-addons-trigger--mega{trigger_active}" aria-expanded="false" aria-haspopup="true" aria-controls="navCoursesPanel">
        <span class="nav-trigger-label">Courses</span>
        <span class="nav-trigger-glyph nav-trigger-glyph--grid" aria-hidden="true"></span>
        <span class="nav-addons-caret" aria-hidden="true">▾</span>
      </button>
      <div class="nav-addons-panel nav-courses-panel nav-panel--courses" id="navCoursesPanel" role="menu" hidden>
        <div class="nav-panel-head nav-panel-head--courses">
          <p class="nav-panel-eyebrow">Certification catalog</p>
          <p class="nav-panel-title">Browse 110+ courses</p>
        </div>
        <div class="nav-courses-stack">
{stack}
        </div>
      </div>
    </li>"""


def addons_dropdown_li(*, variant: str = "inner", current_path: str = "") -> str:
    path = current_path.rstrip("/") or "/"
    cols: list[str] = []
    for title, links in ADDON_SECTIONS:
        items = []
        for label, href in links:
            active = ' class="active"' if path == href.rstrip("/") or path == href else ""
            items.append(f'        <a href="{_esc(href)}" role="menuitem"{active}>{_esc(label)}</a>')
        cols.append(
            f'      <div class="nav-addons-col">\n'
            f'        <p class="nav-addons-col-title">{_esc(title)}</p>\n'
            + "\n".join(items)
            + "\n      </div>"
        )
    grid = "\n".join(cols)
    return f"""    <li class="nav-addons-wrap">
      <button type="button" class="nav-addons-trigger nav-addons-trigger--explore" aria-expanded="false" aria-haspopup="true" aria-controls="navAddonsPanel">
        <span class="nav-trigger-label">{html_lib.escape(NAV_EXPLORE_LABEL)}</span>
        <span class="nav-trigger-glyph nav-trigger-glyph--spark" aria-hidden="true"></span>
        <span class="nav-addons-caret" aria-hidden="true">▾</span>
      </button>
      <div class="nav-addons-panel nav-panel--explore" id="navAddonsPanel" role="menu" hidden>
        <div class="nav-panel-head nav-panel-head--explore">
          <p class="nav-panel-eyebrow">Discover Nexperts</p>
          <p class="nav-panel-title">Workshops, blog &amp; community</p>
        </div>
        <div class="nav-addons-grid">
{grid}
        </div>
      </div>
    </li>"""


def _nav_links(variant: str, current_path: str) -> str:
    links = HOME_LINKS if variant == "home" else INNER_LINKS
    path = current_path.rstrip("/") or "/"
    parts: list[str] = ['    <span class="nav-highlight" aria-hidden="true"></span>']
    for label, href, forced in links:
        if label == "Courses":
            parts.append(courses_dropdown_li(variant=variant, current_path=path))
            parts.append(_nav_sep())
            continue
        if label == "Contact":
            parts.append(addons_dropdown_li(variant=variant, current_path=path))
            cls = forced
            if not cls:
                norm = href.rstrip("/")
                if path == norm or (norm != "/" and path == norm):
                    cls = "active"
            ac = f' class="{cls}"' if cls else ""
            parts.append(f'    <li><a href="{_esc(href)}"{ac}>{_esc(label)}</a></li>')
            continue
        cls = forced
        if not cls:
            norm = href.rstrip("/")
            if norm.startswith("#"):
                cls = ""
            elif path == norm or (norm != "/" and path == norm):
                cls = "active"
        ac = f' class="{cls}"' if cls else ""
        parts.append(f'    <li><a href="{_esc(href)}"{ac}>{_esc(label)}</a></li>')
        if label in NAV_SEP_AFTER:
            parts.append(_nav_sep())
    return "\n".join(parts)


def _nav_ai_block(*, show_mobile_hint: bool) -> str:
    hint = ""
    if show_mobile_hint:
        hint = (
            '<span class="nav-ai-mobile-hint"><span class="nav-ai-mobile-up">&uarr;</span>'
            '<span class="nav-ai-mobile-text">Click here</span></span>'
        )
    return (
        f'<div class="nav-ai-wrap">{hint}'
        '<a href="https://nexpertsai.com" class="nav-ai">'
        '<span class="ldot"></span><span class="nav-ai-label">Nexperts AI</span></a></div>'
    )


def render_site_nav(
    *,
    variant: str = "inner",
    current_path: str = "",
    enroll_href: str = "/contact-us#enquire",
    enroll_onclick: str = "",
    logo_prefix: str = "",
) -> str:
    """Full header nav matching beyond.html (variant home | inner)."""
    links = _nav_links(variant, current_path)
    onclick = f' onclick="{enroll_onclick}"' if enroll_onclick else ""
    nav_class = "site-nav site-nav--home" if variant == "home" else "site-nav"
    ai_block = _nav_ai_block(show_mobile_hint=(variant == "home"))
    return f"""<nav class="{nav_class}" data-nx-nav="v2">
  <div class="nav-aurora-track" aria-hidden="true"><span class="nav-aurora-beam"></span></div>
  <a href="/" class="nav-logo" aria-label="Nexperts Academy">
    <img src="{logo_prefix}/image/nexperts-logo.png" alt="Nexperts Academy logo" width="260" height="84">
  </a>
  <div class="nav-center">
  <ul class="nav-links" id="sitePrimaryNav">
{links}
  </ul>
  </div>
  <div class="nav-right nav-actions">
    {ai_block}
    <a href="{_esc(enroll_href)}" class="nav-enroll"{onclick}><span class="nav-enroll-text">Enquire Now</span><span class="nav-enroll-arrow" aria-hidden="true">→</span></a>
  </div>
  <button type="button" class="nav-menu-btn" id="siteNavMenuBtn" aria-controls="sitePrimaryNav" aria-expanded="false" aria-label="Open menu"><span class="nav-menu-bar" aria-hidden="true"></span><span class="nav-menu-bar" aria-hidden="true"></span><span class="nav-menu-bar" aria-hidden="true"></span></button>
</nav>
<div class="nav-drawer-backdrop" aria-hidden="true"></div>"""


_NAV_SCRIPTS = (
    '<script src="{prefix}/js/nav-highlight.js" defer></script>\n'
    '<script src="{prefix}/js/nav-addons.js" defer></script>\n'
    '<script src="{prefix}/js/courses-catalog.js" defer></script>'
)

NAV_ASSET_TAGS = (
    '<link rel="stylesheet" href="/css/site-nav.css">\n'
    '<link rel="stylesheet" href="/css/nav-addons.css">\n'
    + _NAV_SCRIPTS.format(prefix="")
)

NAV_ASSET_TAGS_REL = (
    '<link rel="stylesheet" href="css/site-nav.css">\n'
    '<link rel="stylesheet" href="css/nav-addons.css">\n'
    + _NAV_SCRIPTS.format(prefix="")
)

COURSE_NAV_ASSET_TAGS = (
    '<link rel="stylesheet" href="../css/site-nav.css">\n'
    '<link rel="stylesheet" href="../css/nav-addons.css">\n'
    '<link rel="stylesheet" href="../css/course-detail-addons.css">\n'
    + _NAV_SCRIPTS.format(prefix="..")
    + '\n<script src="../js/course-related.js" defer></script>'
)

COURSE_SIDEBAR_ENQUIRY_HEAD = {
    "course": (
        '<link rel="stylesheet" href="../css/enquiry-phone.css">\n'
        '<link rel="stylesheet" href="../css/enquiry-loading.css">\n'
        '<link rel="stylesheet" href="../css/course-sidebar-enquiry.css">'
    ),
    "root": (
        '<link rel="stylesheet" href="/css/enquiry-phone.css">\n'
        '<link rel="stylesheet" href="/css/enquiry-loading.css">\n'
        '<link rel="stylesheet" href="/css/course-sidebar-enquiry.css">'
    ),
}

COURSE_SIDEBAR_ENQUIRY_SCRIPTS = {
    "course": (
        '<script src="../js/enquiry-config.js"></script>\n'
        '<script src="../js/enquiry-phone.js" defer></script>\n'
        '<script src="../js/enquiry-submit.js"></script>\n'
        '<script src="../js/course-sidebar-enquiry.js" defer></script>'
    ),
    "root": (
        '<script src="/js/enquiry-config.js"></script>\n'
        '<script src="/js/enquiry-phone.js" defer></script>\n'
        '<script src="/js/enquiry-submit.js"></script>\n'
        '<script src="/js/course-sidebar-enquiry.js" defer></script>'
    ),
}

COURSE_DETAIL_ADDON_TAGS = {
    "course": (
        '<link rel="stylesheet" href="../css/course-detail-addons.css">\n'
        + COURSE_SIDEBAR_ENQUIRY_HEAD["course"]
        + '\n<script src="../js/course-related.js" defer></script>'
    ),
    "root": (
        '<link rel="stylesheet" href="/css/course-detail-addons.css">\n'
        + COURSE_SIDEBAR_ENQUIRY_HEAD["root"]
        + '\n<script src="/js/course-related.js" defer></script>'
    ),
}

WHATSAPP_URL = "https://wa.me/601112216870"

_WHATSAPP_SVG = (
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>'
    "</svg>"
)


def render_whatsapp_float() -> str:
    return (
        f'<a href="{WHATSAPP_URL}" class="nx-wa-float" target="_blank" '
        f'rel="noopener noreferrer" aria-label="Chat with Nexperts Academy on WhatsApp">\n'
        f"  {_WHATSAPP_SVG}\n"
        f"</a>"
    )


WHATSAPP_FLOAT_CSS = {
    "root": '<link rel="stylesheet" href="/css/whatsapp-float.css">',
    "rel": '<link rel="stylesheet" href="css/whatsapp-float.css">',
    "course": '<link rel="stylesheet" href="../css/whatsapp-float.css">',
}
