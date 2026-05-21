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
                "/post/unlocking-the-power-of-data-science-applications-and-challenges",
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


def _esc(s: str) -> str:
    return html_lib.escape(s, quote=True)


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
    return f"""    <li class="nav-addons-wrap nav-courses-wrap">
      <button type="button" class="nav-addons-trigger nav-courses-trigger" aria-expanded="false" aria-haspopup="true" aria-controls="navCoursesPanel">
        Courses <span class="nav-addons-caret" aria-hidden="true">▾</span>
      </button>
      <div class="nav-addons-panel nav-courses-panel" id="navCoursesPanel" role="menu" hidden>
        <div class="nav-courses-stack">
{stack}
        </div>
      </div>
    </li>"""


def addons_dropdown_li(current_path: str = "") -> str:
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
      <button type="button" class="nav-addons-trigger" aria-expanded="false" aria-haspopup="true" aria-controls="navAddonsPanel">
        {html_lib.escape(NAV_EXPLORE_LABEL)} <span class="nav-addons-caret" aria-hidden="true">▾</span>
      </button>
      <div class="nav-addons-panel" id="navAddonsPanel" role="menu" hidden>
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
            continue
        if label == "Contact":
            parts.append(addons_dropdown_li(path))
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
    return f"""<nav class="{nav_class}">
  <a href="/" class="nav-logo" aria-label="Nexperts Academy">
    <img src="{logo_prefix}/image/nexperts-logo.png" alt="Nexperts Academy logo" width="260" height="84">
  </a>
  <ul class="nav-links" id="sitePrimaryNav">
{links}
  </ul>
  <div class="nav-right">
    {ai_block}
    <a href="{_esc(enroll_href)}" class="nav-enroll"{onclick}>Enquire Now</a>
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
    + _NAV_SCRIPTS.format(prefix="..")
)
