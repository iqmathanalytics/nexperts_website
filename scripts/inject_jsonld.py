# -*- coding: utf-8 -*-
"""
Inject schema.org JSON-LD into course pages (Course) and homepage (Organization).
Run from repo root: python scripts/inject_jsonld.py
Requires existing SEO meta block (meta name=description) on course pages.
"""
from __future__ import annotations

import html as html_module
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.nexpertsacademy.com"
LOGO_URL = f"{SITE}/image/nexperts-logo.png"

MARKER_COURSE_START = "<!-- nexperts-jsonld:course:v1 -->"
MARKER_COURSE_END = "<!-- /nexperts-jsonld:course:v1 -->"
MARKER_ORG_START = "<!-- nexperts-jsonld:organization:v1 -->"
MARKER_ORG_END = "<!-- /nexperts-jsonld:organization:v1 -->"


def decode_entities(s: str) -> str:
    return html_module.unescape(s)


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.I)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1).strip())


def extract_meta_description(html: str) -> str | None:
    m = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"',
        html,
        re.I,
    )
    if not m:
        return None
    return decode_entities(m.group(1))


def teaches_from_title(title: str) -> str:
    t = decode_entities(title)
    t = re.sub(r"\s*\|\s*Nexperts Academy\s*$", "", t, flags=re.I).strip()
    if len(t) > 200:
        t = t[:197] + "..."
    return t


def remove_marked(html: str, start: str, end: str) -> str:
    pat = re.compile(
        r"\n?\s*" + re.escape(start) + r".*?" + re.escape(end) + r"\s*",
        re.DOTALL,
    )
    return pat.sub("\n", html, count=1)


def inject_before_head_close(html: str, block: str) -> str:
    out = re.sub(r"(</head>)", block + r"\n\1", html, count=1, flags=re.I)
    if out == html:
        raise ValueError("No </head> found")
    return out


def build_course_json(filename: str, title: str, description: str) -> str:
    name = decode_entities(title.strip())
    teaches = teaches_from_title(title)
    url = f"{SITE}/course_pages/{filename}"
    data = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": name,
        "description": description,
        "provider": {
            "@type": "Organization",
            "name": "Nexperts Academy",
            "url": SITE,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Petaling Jaya",
                "addressRegion": "Selangor",
                "addressCountry": "MY",
            },
        },
        "url": url,
        "inLanguage": "en",
        "educationalLevel": "Professional Certification",
        "teaches": teaches,
    }
    inner = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        f"{MARKER_COURSE_START}\n"
        f'<script type="application/ld+json">\n{inner}\n</script>\n'
        f"{MARKER_COURSE_END}"
    )


def build_organization_json() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Nexperts Academy",
        "url": SITE,
        "logo": LOGO_URL,
        "description": (
            "IT certification training provider in Malaysia offering 120+ courses "
            "including CCNA, CEH, CISSP, AWS, Azure, Microsoft, CompTIA and more — "
            "delivered by certified practitioners in Kuala Lumpur (Petaling Jaya)."
        ),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Petaling Jaya",
            "addressRegion": "Selangor",
            "addressCountry": "MY",
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer service",
            "email": "enquiry@nexpertsacademy.com",
        },
        "sameAs": [
            "https://www.linkedin.com/company/nexperts-academy-sdn-bhd/",
        ],
    }
    inner = json.dumps(data, ensure_ascii=False, indent=2)
    return (
        f"{MARKER_ORG_START}\n"
        f'<script type="application/ld+json">\n{inner}\n</script>\n'
        f"{MARKER_ORG_END}"
    )


def process_course_pages():
    folder = ROOT / "course_pages"
    for path in sorted(folder.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        html = remove_marked(html, MARKER_COURSE_START, MARKER_COURSE_END)
        title = extract_title(html)
        desc = extract_meta_description(html)
        if not title:
            print(f"SKIP (no title): {path.name}")
            continue
        if not desc:
            desc = teaches_from_title(title) + (
                " Hands-on certification training at Nexperts Academy, Malaysia."
            )
            if len(desc) > 320:
                desc = desc[:317] + "..."
        block = build_course_json(path.name, title, desc)
        try:
            html = inject_before_head_close(html, block)
        except ValueError:
            print(f"SKIP (no head): {path.name}")
            continue
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"OK course_pages/{path.name}")


def process_index():
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    html = remove_marked(html, MARKER_ORG_START, MARKER_ORG_END)
    block = build_organization_json()
    try:
        html = inject_before_head_close(html, block)
    except ValueError:
        print("SKIP index.html")
        return
    path.write_text(html, encoding="utf-8", newline="\n")
    print("OK index.html")


def main():
    process_course_pages()
    process_index()


if __name__ == "__main__":
    main()
