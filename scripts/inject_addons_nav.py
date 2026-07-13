# -*- coding: utf-8 -*-
"""Inject Add-ons nav dropdown and shared header on public HTML pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_nav import (  # noqa: E402
    COURSE_DETAIL_ADDON_TAGS,
    COURSE_NAV_ASSET_TAGS,
    NAV_ASSET_TAGS,
    NAV_ASSET_TAGS_REL,
    WHATSAPP_FLOAT_CSS,
    addons_dropdown_li,
    render_site_nav,
    render_whatsapp_float,
)

NAV_RE = re.compile(
    r'<nav class="site-nav[^"]*"(?:\s+data-nx-nav="v2")?>.*?</nav>\s*'
    r'<div class="nav-drawer-backdrop"[^>]*>\s*</div>',
    re.DOTALL | re.IGNORECASE,
)

CONTACT_LI_RE = re.compile(
    r"(\s*<li><a href=\"(?:\.\./)?contact-us\"[^>]*>Contact</a></li>)",
    re.IGNORECASE,
)

WHATSAPP_SOCIAL_RE = re.compile(
    r'\s*<a href="https://wa\.me/601112216870" class="nx-social-btn nx-social-wa"[^>]*>.*?</a>',
    re.DOTALL | re.IGNORECASE,
)

STATIC_PAGES = [
    "workshops.html",
    "upcoming-events.html",
    "past-events.html",
    "blog.html",
    "catalyst-for-change.html",
    "empowering-community-throught-technology.html",
    "chinese-new-year.html",
    "tan-boon-heong-event.html",
    "nexpert-x-universiti-teknologi-mara.html",
    "blog/unlocking-the-power-of-data-science-applications-and-challenges.html",
    "blog/ccna-certification-guide.html",
    "blog/comptia-network-plus-certification-guide.html",
    "blog/top-data-science-training-institutes-malaysia.html",
    "blog/aws-certification-roadmap.html",
]

ROOT_PAGES_HOME = ["index.html"]
ROOT_PAGES_INNER = [
    "about.html",
    "contact.html",
    "privacy-policy.html",
    "ceh.html",
    "ccna.html",
    "python-bootcamp.html",
    "data-science-with-python.html",
    "404.html",
    "Nexperts beyond.html",
]


def path_from_file(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel == "contact.html":
        return "/contact-us"
    if rel == "Nexperts beyond.html":
        return "/Nexperts beyond.html"
    if rel.startswith("blog/"):
        return "/" + rel.replace(".html", "")
    if rel.startswith("post/"):
        return "/" + rel.replace(".html", "")
    return "/" + rel.replace(".html", "")


def _ensure_site_base_css(html: str, *, course: bool = False) -> str:
    if "site-base.css" in html:
        return html
    pairs: list[tuple[str, str]] = []
    if course:
        pairs = [
            (
                '<link rel="stylesheet" href="../css/site-nav.css">',
                '<link rel="stylesheet" href="../css/site-base.css">\n',
            ),
            (
                '<link rel="stylesheet" href="/css/site-nav.css">',
                '<link rel="stylesheet" href="/css/site-base.css">\n',
            ),
        ]
    elif 'href="/css/site-nav.css"' in html:
        pairs = [
            (
                '<link rel="stylesheet" href="/css/site-nav.css">',
                '<link rel="stylesheet" href="/css/site-base.css">\n',
            ),
        ]
    elif 'href="css/site-nav.css"' in html:
        pairs = [
            (
                '<link rel="stylesheet" href="css/site-nav.css">',
                '<link rel="stylesheet" href="css/site-base.css">\n',
            ),
        ]
    for needle, ins in pairs:
        if needle in html:
            return html.replace(needle, ins + needle, 1)
    return html


def ensure_nav_assets(html: str, *, course: bool = False) -> str:
    tags = COURSE_NAV_ASSET_TAGS if course else NAV_ASSET_TAGS
    if course:
        html = html.replace('href="/css/nav-addons.css"', 'href="../css/nav-addons.css"')
        html = html.replace('src="/js/nav-highlight.js"', 'src="../js/nav-highlight.js"')
        html = html.replace('src="/js/nav-addons.js"', 'src="../js/nav-addons.js"')
    if "nav-addons.css" in html:
        if "site-nav.css" not in html:
            if course:
                ins = '<link rel="stylesheet" href="../css/site-nav.css">\n'
                html = html.replace(
                    '<link rel="stylesheet" href="../css/nav-addons.css">',
                    ins + '<link rel="stylesheet" href="../css/nav-addons.css">',
                    1,
                )
            elif 'href="/css/nav-addons.css"' in html:
                ins = '<link rel="stylesheet" href="/css/site-nav.css">\n'
                html = html.replace(
                    '<link rel="stylesheet" href="/css/nav-addons.css">',
                    ins + '<link rel="stylesheet" href="/css/nav-addons.css">',
                    1,
                )
            elif 'href="css/nav-addons.css"' in html:
                ins = '<link rel="stylesheet" href="css/site-nav.css">\n'
                html = html.replace(
                    '<link rel="stylesheet" href="css/nav-addons.css">',
                    ins + '<link rel="stylesheet" href="css/nav-addons.css">',
                    1,
                )
        if "nav-highlight.js" not in html:
            if course:
                ins = '<script src="../js/nav-highlight.js" defer></script>\n'
                html = html.replace(
                    '<script src="../js/nav-addons.js" defer></script>',
                    ins + '<script src="../js/nav-addons.js" defer></script>',
                    1,
                )
            elif 'src="/js/nav-addons.js"' in html:
                ins = '<script src="/js/nav-highlight.js" defer></script>\n'
                html = html.replace(
                    '<script src="/js/nav-addons.js" defer></script>',
                    ins + '<script src="/js/nav-addons.js" defer></script>',
                    1,
                )
            elif 'src="js/nav-addons.js"' in html:
                ins = '<script src="js/nav-highlight.js" defer></script>\n'
                html = html.replace(
                    '<script src="js/nav-addons.js" defer></script>',
                    ins + '<script src="js/nav-addons.js" defer></script>',
                    1,
                )
        if "courses-catalog.js" not in html:
            if course and 'src="../js/nav-addons.js"' in html:
                html = html.replace(
                    '<script src="../js/nav-addons.js" defer></script>',
                    '<script src="../js/nav-addons.js" defer></script>\n'
                    '<script src="../js/courses-catalog.js" defer></script>',
                    1,
                )
            elif 'src="/js/nav-addons.js"' in html:
                html = html.replace(
                    '<script src="/js/nav-addons.js" defer></script>',
                    '<script src="/js/nav-addons.js" defer></script>\n'
                    '<script src="/js/courses-catalog.js" defer></script>',
                    1,
                )
            elif 'src="js/nav-addons.js"' in html:
                html = html.replace(
                    '<script src="js/nav-addons.js" defer></script>',
                    '<script src="js/nav-addons.js" defer></script>\n'
                    '<script src="js/courses-catalog.js" defer></script>',
                    1,
                )
        html = _ensure_site_base_css(html, course=course)
        return html
    if course:
        anchor = '<link rel="stylesheet" href="../css/site-nav-mobile.css">'
        rep = anchor + "\n" + tags
    else:
        anchor = '<link rel="stylesheet" href="/css/site-nav-mobile.css">'
        if anchor not in html:
            anchor = '<link rel="stylesheet" href="css/site-nav-mobile.css">'
            rep = anchor + "\n" + NAV_ASSET_TAGS_REL
        else:
            rep = anchor + "\n" + tags
    if anchor in html:
        html = html.replace(anchor, rep, 1)
    else:
        html = html.replace("</head>", tags + "\n</head>", 1)
    return _ensure_site_base_css(html, course=course)


def ensure_course_detail_addons(html: str, *, course: bool = False) -> str:
    if "enroll-card" not in html or "course-detail-addons.css" in html:
        return html
    tags = COURSE_DETAIL_ADDON_TAGS["course" if course else "root"]
    if 'src="../js/courses-catalog.js"' in html:
        return html.replace(
            '<script src="../js/courses-catalog.js" defer></script>',
            '<script src="../js/courses-catalog.js" defer></script>\n' + tags,
            1,
        )
    if 'src="/js/courses-catalog.js"' in html:
        return html.replace(
            '<script src="/js/courses-catalog.js" defer></script>',
            '<script src="/js/courses-catalog.js" defer></script>\n' + tags,
            1,
        )
    if 'src="js/courses-catalog.js"' in html:
        return html.replace(
            '<script src="js/courses-catalog.js" defer></script>',
            '<script src="js/courses-catalog.js" defer></script>\n' + tags,
            1,
        )
    return html.replace("</head>", tags + "\n</head>", 1)


def strip_whatsapp_social(html: str) -> str:
    return WHATSAPP_SOCIAL_RE.sub("", html)


def ensure_whatsapp_float(html: str, *, course: bool = False) -> str:
    html = strip_whatsapp_social(html)
    if "nx-wa-float" in html:
        if "whatsapp-float.css" not in html:
            css = WHATSAPP_FLOAT_CSS["course" if course else "root"]
            if course:
                pass
            elif 'href="/css/site-nav.css"' in html or 'href="/css/nav-addons.css"' in html:
                css = WHATSAPP_FLOAT_CSS["root"]
            elif 'href="css/site-nav.css"' in html or 'href="css/nav-addons.css"' in html:
                css = WHATSAPP_FLOAT_CSS["rel"]
            else:
                css = WHATSAPP_FLOAT_CSS["course" if course else "root"]
            if css in html:
                return html
            if "</head>" in html:
                html = html.replace("</head>", css + "\n</head>", 1)
        return html

    if course:
        css = WHATSAPP_FLOAT_CSS["course"]
    elif 'href="/css/site-nav.css"' in html or 'href="/css/nav-addons.css"' in html:
        css = WHATSAPP_FLOAT_CSS["root"]
    elif 'href="css/site-nav.css"' in html or 'href="css/nav-addons.css"' in html:
        css = WHATSAPP_FLOAT_CSS["rel"]
    else:
        css = WHATSAPP_FLOAT_CSS["root"]

    if "whatsapp-float.css" not in html and "</head>" in html:
        html = html.replace("</head>", css + "\n</head>", 1)

    block = render_whatsapp_float()
    if re.search(r"</body>", html, re.IGNORECASE):
        html = re.sub(r"</body>", block + "\n</body>", html, count=1, flags=re.IGNORECASE)
    return html


def inject_addons_before_contact(html: str, current_path: str) -> str:
    block = addons_dropdown_li(variant="inner", current_path=current_path)
    if "nav-addons-wrap" in html:
        return html
    m = CONTACT_LI_RE.search(html)
    if not m:
        return html
    return html[: m.start(1)] + "\n" + block + m.group(1) + html[m.end(1) :]


def replace_full_nav(
    html: str,
    *,
    variant: str,
    current_path: str,
    enroll_href: str,
    enroll_onclick: str = "",
    logo_prefix: str = "",
) -> str:
    nav = render_site_nav(
        variant=variant,
        current_path=current_path,
        enroll_href=enroll_href,
        enroll_onclick=enroll_onclick,
        logo_prefix=logo_prefix,
    )
    if NAV_RE.search(html):
        return NAV_RE.sub(nav, html, count=1)
    return html


def patch_file(path: Path, mode: str, current_path: str) -> bool:
    html = path.read_text(encoding="utf-8")
    orig = html
    course = path.parts[-2] == "courses" if "courses" in path.parts else False

    if mode == "home":
        html = replace_full_nav(
            html,
            variant="home",
            current_path=current_path,
            enroll_href="#enquire-modal",
            enroll_onclick="openEnquireModal(event)",
        )
    elif mode == "inner":
        html = replace_full_nav(
            html,
            variant="inner",
            current_path=current_path,
            enroll_href="/contact-us#enquire",
        )
    elif mode == "course":
        enroll_href = "/contact-us#enquire"
        eh = re.search(r'href="([^"]+)" class="nav-enroll"', html)
        if eh:
            enroll_href = eh.group(1)
        html = replace_full_nav(
            html,
            variant="inner",
            current_path=current_path,
            enroll_href=enroll_href,
        )
    elif mode == "static":
        html = replace_full_nav(
            html,
            variant="inner",
            current_path=current_path,
            enroll_href="/contact-us#enquire",
        )

    html = ensure_nav_assets(html, course=course)
    html = ensure_whatsapp_float(html, course=course)
    if "enroll-card" in html:
        html = ensure_course_detail_addons(html, course=course)
    if html != orig:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    for name in ROOT_PAGES_HOME:
        p = ROOT / name
        if p.is_file() and patch_file(p, "home", path_from_file(name)):
            print(f"  nav home: {name}")
            changed += 1

    for name in ROOT_PAGES_INNER:
        p = ROOT / name
        if p.is_file() and patch_file(p, "inner", path_from_file(name)):
            print(f"  nav inner: {name}")
            changed += 1

    for p in sorted((ROOT / "courses").glob("*.html")):
        if patch_file(p, "course", f"/courses/{p.stem}"):
            print(f"  nav course: courses/{p.name}")
            changed += 1

    for rel in STATIC_PAGES:
        p = ROOT / rel
        if p.is_file() and patch_file(p, "static", path_from_file(rel)):
            print(f"  nav static: {rel}")
            changed += 1

    print(f"Done. Updated {changed} files.")


if __name__ == "__main__":
    main()
