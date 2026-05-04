# -*- coding: utf-8 -*-
"""
Inject canonical, meta description, and Open Graph tags after <title>.
Run from repo root: python scripts/inject_seo_meta.py
"""
from __future__ import annotations

import re
import html as html_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Canonical production host (www)
SITE = "https://www.nexpertsacademy.com"
OG_IMAGE = f"{SITE}/image/nexperts-logo.png"

MARKER_START = "<!-- nexperts-seo-meta:v1 -->"
MARKER_END = "<!-- /nexperts-seo-meta:v1 -->"


def esc_attr(s: str) -> str:
    return html_module.escape(s, quote=True)


def decode_entities(s: str) -> str:
    """Decode &amp; etc. from <title> text before re-escaping for attributes."""
    return html_module.unescape(s)


def strip_title(raw: str) -> str:
    t = re.sub(r"\s+", " ", raw.strip())
    t = re.sub(r"\s*\|\s*Nexperts Academy\s*$", "", t, flags=re.I)
    return t.strip()


def course_description(title_inner: str) -> str:
    """Meta description ~150–160 chars derived from <title> text."""
    base = strip_title(decode_entities(title_inner))
    if not base:
        base = "IT certification course"
    # Prefer short lead before "—" (e.g. "CCNA" from "CCNA — Cisco | ...")
    if "—" in base:
        first = base.split("—", 1)[0].strip()
        if 3 <= len(first) <= 55:
            base = first
    tail = (
        " Hands-on certification training in Malaysia — expert instructors, "
        "exam-focused labs & HRD Corp options at Nexperts Academy."
    )
    max_base = 160 - len(tail)
    if max_base < 24:
        max_base = 24
    if len(base) > max_base:
        base = base[: max_base - 1].rstrip(" ,.;—") + "…"
    out = base + tail
    if len(out) > 160:
        out = out[:157] + "..."
    return out


def remove_existing_block(html: str) -> str:
    pat = re.compile(
        r"\n?\s*" + re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\s*",
        re.DOTALL,
    )
    return pat.sub("\n", html, count=1)


def remove_contact_legacy_meta(html: str) -> str:
    """Strip standalone SEO tags from contact.html before unified block (avoid duplicates)."""
    lines = html.splitlines()
    out = []
    skip_patterns = (
        '<meta name="description"',
        '<meta name="robots"',
        '<link rel="canonical"',
        '<meta property="og:title"',
        '<meta property="og:description"',
        '<meta property="og:type"',
    )
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if any(stripped.startswith(p) for p in skip_patterns):
            i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL | re.I)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(1).strip())


def inject_block_after_title(html: str, block: str) -> str:
    block_full = f"\n{MARKER_START}\n{block}\n{MARKER_END}\n"
    out = re.sub(
        r"(<title[^>]*>.*?</title>)",
        r"\1" + block_full,
        html,
        count=1,
        flags=re.DOTALL | re.I,
    )
    if out == html:
        raise ValueError("Could not find <title> to inject after")
    return out


def build_course_block(filename: str, title_inner: str) -> str:
    desc = course_description(title_inner)
    canonical = f"{SITE}/course_pages/{filename}"
    og_title = decode_entities(title_inner.strip())
    e_desc = esc_attr(desc)
    e_title = esc_attr(og_title)
    return "\n".join(
        [
            f'<meta name="description" content="{e_desc}">',
            f'<link rel="canonical" href="{canonical}">',
            f'<meta property="og:title" content="{e_title}">',
            f'<meta property="og:description" content="{e_desc}">',
            f'<meta property="og:url" content="{canonical}">',
            '<meta property="og:type" content="website">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
        ]
    )


def build_root_block(canonical_url: str, description: str, og_title: str) -> str:
    e_desc = esc_attr(description)
    e_title = esc_attr(og_title)
    return "\n".join(
        [
            f'<meta name="description" content="{e_desc}">',
            f'<link rel="canonical" href="{canonical_url}">',
            f'<meta property="og:title" content="{e_title}">',
            f'<meta property="og:description" content="{e_desc}">',
            f'<meta property="og:url" content="{canonical_url}">',
            '<meta property="og:type" content="website">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
        ]
    )


def process_course_pages():
    folder = ROOT / "course_pages"
    for path in sorted(folder.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        title_inner = extract_title(html)
        if not title_inner:
            print(f"SKIP (no title): {path.name}")
            continue
        block = build_course_block(path.name, title_inner)
        try:
            html = inject_block_after_title(html, block)
        except ValueError:
            print(f"SKIP (inject failed): {path.name}")
            continue
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"OK course_pages/{path.name}")


def process_root_pages():
    pages: list[tuple[str, str, str]] = [
        (
            "index.html",
            f"{SITE}/",
            "Nexperts Academy offers IT certification training in Malaysia. CCNA, CEH, CISSP, AWS, Azure and 120+ courses delivered by certified practitioners in Kuala Lumpur.",
        ),
        (
            "about.html",
            f"{SITE}/about.html",
            "About Nexperts Academy — IT certification training in Malaysia & the US. Meet our instructors, Kuala Lumpur HQ & Albany NY offices, and hands-on exam-ready programmes.",
        ),
        (
            "contact.html",
            f"{SITE}/contact.html",
            "Contact Nexperts Academy for course enquiries, corporate training & HRD Corp in Kuala Lumpur (HQ) and Albany NY. Fast replies within 4 business hours.",
        ),
        (
            "privacy-policy.html",
            f"{SITE}/privacy-policy.html",
            "Privacy Policy for Nexperts Academy Sdn Bhd — how we collect, use and protect personal data under the Malaysian PDPA.",
        ),
    ]
    for fname, canon, desc in pages:
        path = ROOT / fname
        if not path.exists():
            print(f"MISSING {fname}")
            continue
        html = path.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        if fname == "contact.html":
            html = remove_contact_legacy_meta(html)
        title_inner = extract_title(html)
        if not title_inner:
            print(f"SKIP (no title): {fname}")
            continue
        block = build_root_block(canon, desc, decode_entities(title_inner))
        try:
            html = inject_block_after_title(html, block)
        except ValueError as e:
            print(f"SKIP {fname}: {e}")
            continue
        path.write_text(html, encoding="utf-8", newline="\n")
        print(f"OK {fname}")


def process_admin_and_beyond():
    admin_path = ROOT / "admin" / "index.html"
    if admin_path.exists():
        html = admin_path.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        title_inner = extract_title(html) or "Admin — Nexperts Academy"
        title_inner = decode_entities(title_inner)
        desc = (
            "Internal catalogue tools for Nexperts Academy — not intended for public search results."
        )
        canon = f"{SITE}/admin/"
        block = (
            '<meta name="robots" content="noindex, nofollow">\n'
            + build_root_block(canon, desc, title_inner)
        )
        try:
            html = inject_block_after_title(html, block)
            admin_path.write_text(html, encoding="utf-8", newline="\n")
            print("OK admin/index.html")
        except ValueError:
            print("SKIP admin/index.html")

    beyond = ROOT / "Nexperts beyond.html"
    if beyond.exists():
        html = beyond.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        title_inner = decode_entities(extract_title(html) or "Nexperts Beyond")
        desc = (
            "Extended learning paths from Nexperts Academy Malaysia — programmes and resources beyond the core certification catalogue."
        )
        if len(desc) > 160:
            desc = desc[:157] + "..."
        canon = f"{SITE}/Nexperts%20beyond.html"
        block = build_root_block(canon, desc, title_inner)
        try:
            html = inject_block_after_title(html, block)
            beyond.write_text(html, encoding="utf-8", newline="\n")
            print("OK Nexperts beyond.html")
        except ValueError:
            print("SKIP Nexperts beyond.html")


def main():
    process_course_pages()
    process_root_pages()
    process_admin_and_beyond()


if __name__ == "__main__":
    main()
