#!/usr/bin/env python3
"""Replace Enroll Now links with inline enquiry forms on all course detail pages."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.course_sidebar_enquiry import (  # noqa: E402
    ENROLL_BTN_RE,
    parse_enroll_href,
    render_sidebar_enquiry_form,
)
from scripts.site_nav import (  # noqa: E402
    COURSE_SIDEBAR_ENQUIRY_HEAD,
    COURSE_SIDEBAR_ENQUIRY_SCRIPTS,
)

SKIP = {
    "contact.html",
    "index.html",
}


def is_course_detail(path: Path) -> bool:
    if path.name in SKIP:
        return False
    if path.parent.name == "courses" and path.suffix == ".html":
        return True
    if "enroll-card" not in path.read_text(encoding="utf-8"):
        return False
    return path.suffix == ".html" and path.parent == ROOT


def asset_variant(path: Path) -> str:
    return "course" if path.parent.name == "courses" else "root"


def ensure_head_assets(html: str, variant: str) -> str:
    block = COURSE_SIDEBAR_ENQUIRY_HEAD[variant]
    if "course-sidebar-enquiry.css" in html:
        return html
    needle = "course-detail-addons.css"
    if needle in html:
        if f'href="../css/{needle}"' in html or f'href="/css/{needle}"' in html:
            return html.replace(
                f'<link rel="stylesheet" href="{"../" if variant == "course" else "/"}css/{needle}">',
                f'<link rel="stylesheet" href="{"../" if variant == "course" else "/"}css/{needle}">\n'
                + block,
                1,
            )
    return html.replace("</head>", block + "\n</head>", 1)


def ensure_body_scripts(html: str, variant: str) -> str:
    block = COURSE_SIDEBAR_ENQUIRY_SCRIPTS[variant]
    if "course-sidebar-enquiry.js" in html:
        return html
    for anchor in (
        '<script src="../js/course-page-ui.js" defer></script>',
        '<script src="/js/course-page-ui.js" defer></script>',
        '<script src="js/course-page-ui.js" defer></script>',
        '<script src="../admin/overlay.js" defer></script>',
    ):
        if anchor in html:
            return html.replace(anchor, block + "\n" + anchor, 1)
    return html.replace("</body>", block + "\n</body>", 1)


def patch_enroll_button(html: str) -> tuple[str, bool]:
    m = ENROLL_BTN_RE.search(html)
    if not m:
        return html, False
    slug, title = parse_enroll_href(m.group("href"))
    form = render_sidebar_enquiry_form(course_title=title, course_slug=slug)
    return ENROLL_BTN_RE.sub(form + "\n", html, count=1), True


def patch_share_enquire(html: str) -> str:
    """Point sidebar share Enquire to the inline form when still linking to contact."""
    return re.sub(
        r'(<div class="share-strip">[\s\S]*?<a href=")(/contact[^"]*#enquire)(" class="share-btn">✉️ Enquire</a>)',
        r'\1#courseEnquiry\3',
        html,
        count=1,
    )


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    orig = html
    variant = asset_variant(path)

    html, replaced = patch_enroll_button(html)
    if not replaced and "course-sidebar-enquiry" in html:
        pass
    elif not replaced:
        return False

    html = patch_share_enquire(html)
    html = ensure_head_assets(html, variant)
    html = ensure_body_scripts(html, variant)

    if html != orig:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    targets: list[Path] = list((ROOT / "courses").glob("*.html"))
    for p in sorted(ROOT.glob("*.html")):
        if p.name not in SKIP and "enroll-card" in p.read_text(encoding="utf-8"):
            targets.append(p)

    seen: set[Path] = set()
    for path in sorted(targets):
        if path in seen:
            continue
        seen.add(path)
        if patch_file(path):
            print(f"  course enquiry: {path.relative_to(ROOT).as_posix()}")
            changed += 1

    print(f"Done. Updated {changed} file(s).")


if __name__ == "__main__":
    main()
