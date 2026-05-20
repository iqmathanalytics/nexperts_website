# -*- coding: utf-8 -*-
"""Add site-nav.css, remove stray click-here markup, fix backdrop closing tags."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLICK_HERE = (
    '<span class="nav-ai-mobile-hint"><span class="nav-ai-mobile-up">&uarr;</span>'
    '<span class="nav-ai-mobile-text">Click here</span></span>'
)

_DIV = "</div>"
BACKDROP_FIX = re.compile(
    r"(<div class=\"nav-drawer-backdrop\" aria-hidden=\"true\">"
    + re.escape(_DIV)
    + r")(?:"
    + re.escape(_DIV)
    + r")+",
    re.IGNORECASE,
)


def patch_html(html: str, *, is_home: bool) -> str:
    if not is_home:
        html = html.replace(CLICK_HERE, "")
    html = BACKDROP_FIX.sub(r"\1", html)
    if "site-nav.css" not in html and "nav-addons.css" in html:
        html = html.replace(
            'href="/css/nav-addons.css"',
            'href="/css/site-nav.css">\n<link rel="stylesheet" href="/css/nav-addons.css"',
            1,
        )
        html = html.replace(
            'href="css/nav-addons.css"',
            'href="css/site-nav.css">\n<link rel="stylesheet" href="css/nav-addons.css"',
            1,
        )
        html = html.replace(
            'href="../css/nav-addons.css"',
            'href="../css/site-nav.css">\n<link rel="stylesheet" href="../css/nav-addons.css"',
            1,
        )
    if is_home and 'class="site-nav site-nav--home"' not in html:
        html = html.replace('class="site-nav"', 'class="site-nav site-nav--home"', 1)
    return html


def strip_contact_nav_css(html: str) -> str:
    """Remove contact page inline nav overrides (conflict with site-nav.css)."""
    start = html.find("/* ── NAV (matches site) ── */")
    if start < 0:
        return html
    end = html.find("/* ── HERO ── */", start)
    if end < 0:
        return html
    return html[:start] + html[end:]


def strip_beyond_nav_css(html: str) -> str:
    """Remove beyond page duplicate nav rules (now in site-nav.css)."""
    patterns = [
        (
            r"nav\{position:fixed;top:0;left:0;right:0;z-index:200;height:62px;.*?\n",
            "",
        ),
        (
            r"\.nav-logo\{display:flex;align-items:center;text-decoration:none\}\n"
            r"\.nav-logo img\{height:36px;width:auto;display:block\}\n",
            "",
        ),
        (
            r"\.nav-links\{display:flex;align-items:center;gap:14px;.*?\n"
            r"\.nav-links li\{position:relative;z-index:2\}\n"
            r"\.nav-links a\{font-size:\.8rem;.*?\n"
            r"\.nav-links a::after\{.*?\n"
            r"\.nav-links a:hover\{.*?\n"
            r"\.nav-links a:hover::after,\.nav-links a\.active::after\{.*?\n"
            r"\.nav-links a\.active\{.*?\n",
            "",
        ),
        (
            r"\.nav-highlight\{position:absolute;top:50%;.*?\n",
            "",
        ),
        (
            r"\.nav-right\{display:flex;align-items:center;gap:14px\}\n",
            "",
        ),
    ]
    for pat, repl in patterns:
        html = re.sub(pat, repl, html, count=1)
    # nav-ai block through nav-enroll (minified in beyond)
    html = re.sub(
        r"\.nav-ai-wrap\{position:relative;display:flex;flex-direction:column;align-items:center;gap:5px\}.*?"
        r"\.nav-enroll:hover\{background:linear-gradient\(135deg,#1e40af.*?\n\n",
        "",
        html,
        count=1,
        flags=re.DOTALL,
    )
    return html


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if "admin" in path.parts:
            continue
        html = path.read_text(encoding="utf-8")
        orig = html
        is_home = path.name == "index.html"
        html = patch_html(html, is_home=is_home)
        if path.name == "contact.html":
            html = strip_contact_nav_css(html)
        if path.name == "Nexperts beyond.html":
            html = strip_beyond_nav_css(html)
        if html != orig:
            path.write_text(html, encoding="utf-8", newline="\n")
            print(f"  synced: {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. Updated {changed} files.")


if __name__ == "__main__":
    main()
