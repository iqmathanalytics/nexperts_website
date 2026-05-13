# -*- coding: utf-8 -*-
"""
Inject canonical, meta description, Open Graph, Twitter, and legacy verification tags.
Uses seo_tags_output.txt + _redirects for course URLs that existed on the old site.
Canonical course URLs are /courses/{slug}, except selected legacy pages that stay at root.

Run from repo root: python scripts/inject_seo_meta.py
"""
from __future__ import annotations

import html as html_module
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from seo_legacy import (  # noqa: E402
    LegacySeo,
    legacy_by_slug,
    parse_seo_export,
)
from site_paths import ROOT_CANONICAL_FILES, canonical_path_for_slug

SITE = "https://www.nexpertsacademy.com"
OG_IMAGE = f"{SITE}/image/nexperts-logo.png"
OG_IMG_W = "260"
OG_IMG_H = "84"
FAVICON_PATH = "/favicon.png"

MARKER_START = "<!-- nexperts-seo-meta:v1 -->"
MARKER_END = "<!-- /nexperts-seo-meta:v1 -->"


def favicon_tags() -> list[str]:
    return [
        f'<link rel="icon" sizes="192x192" href="{FAVICON_PATH}" type="image/png">',
        f'<link rel="shortcut icon" href="{FAVICON_PATH}" type="image/png">',
        f'<link rel="apple-touch-icon" href="{FAVICON_PATH}" type="image/png">',
    ]


def esc_attr(s: str) -> str:
    return html_module.escape(s, quote=True)


def decode_entities(s: str) -> str:
    return html_module.unescape(s)


def strip_title(raw: str) -> str:
    t = re.sub(r"\s+", " ", raw.strip())
    t = re.sub(r"\s*\|\s*Nexperts Academy\s*$", "", t, flags=re.I)
    return t.strip()


def course_description(title_inner: str) -> str:
    base = strip_title(decode_entities(title_inner))
    if not base:
        base = "IT certification course"
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


def fallback_keywords(title_inner: str, slug: str) -> str:
    base = strip_title(decode_entities(title_inner))
    core = base.replace("—", " ").split("|")[0].strip()
    return (
        f"{core}, {slug.replace('-', ' ')}, IT certification Malaysia, "
        "training Kuala Lumpur, Nexperts Academy"
    )


def remove_existing_block(html: str) -> str:
    pat = re.compile(
        r"\n?\s*" + re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\s*",
        re.DOTALL,
    )
    return pat.sub("\n", html, count=1)


def remove_contact_legacy_meta(html: str) -> str:
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


def replace_title_tag(html: str, new_title: str) -> str:
    inner = html_module.escape(decode_entities(new_title), quote=False)
    out = re.sub(
        r"<title[^>]*>.*?</title>",
        f"<title>{inner}</title>",
        html,
        count=1,
        flags=re.DOTALL | re.I,
    )
    return out


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


def pick_verifications(
    legacy: LegacySeo | None, home: LegacySeo | None
) -> tuple[list[str], str, str, str]:
    """google tokens, facebook domain, fb meta tag content, fb:admins."""
    gsv: list[str] = []
    fd = ""
    fb_meta = ""
    fb_admins = ""
    src = legacy or home
    if src:
        gsv = list(src.google_site_verification)
        fd = src.facebook_domain_verification or ""
        fb_admins = src.fb_admins or ""
        fb_meta = fb_admins
    return gsv, fd, fb_meta, fb_admins


def build_course_seo_block(
    slug: str,
    title_inner: str,
    legacy: LegacySeo | None,
    home: LegacySeo | None,
) -> str:
    canon = f"{SITE}{canonical_path_for_slug(slug)}"
    gsv, fd, fb_meta, fb_admins = pick_verifications(legacy, home)

    if legacy:
        desc = legacy.description or course_description(title_inner)
        kw = legacy.keywords or fallback_keywords(title_inner, slug)
        og_t = legacy.og_title or legacy.title or title_inner
        og_d = legacy.og_description or desc
        tw_t = legacy.twitter_title or og_t
        tw_d = legacy.twitter_description or og_d
    else:
        desc = course_description(title_inner)
        kw = fallback_keywords(title_inner, slug)
        og_t = decode_entities(title_inner.strip())
        og_d = desc
        tw_t = og_t
        tw_d = desc

    pre_g = gsv[:2]
    post_g = gsv[2:] if len(gsv) > 2 else []
    lines: list[str] = []
    lines.extend(favicon_tags())
    for tok in pre_g:
        lines.append(
            f'<meta name="google-site-verification" content="{esc_attr(tok)}">'
        )
    lines.append(f'<meta name="description" content="{esc_attr(desc)}">')
    lines.extend(
        [
            f'<meta property="og:title" content="{esc_attr(og_t)}">',
            f'<meta property="og:description" content="{esc_attr(og_d)}">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
            f'<meta property="og:image:width" content="{OG_IMG_W}">',
            f'<meta property="og:image:height" content="{OG_IMG_H}">',
            f'<meta property="og:url" content="{canon}">',
            '<meta property="og:site_name" content="Nexperts Academy">',
            '<meta property="og:type" content="website">',
            f'<meta name="keywords" content="{esc_attr(kw)}">',
        ]
    )
    for tok in post_g:
        lines.append(
            f'<meta name="google-site-verification" content="{esc_attr(tok)}">'
        )
    if fd:
        lines.append(
            f'<meta name="facebook-domain-verification" content="{esc_attr(fd)}">'
        )
    if fb_meta:
        lines.append(f'<meta name="fb_admins_meta_tag" content="{esc_attr(fb_meta)}">')
    if fb_admins:
        lines.append(f'<meta property="fb:admins" content="{esc_attr(fb_admins)}">')
    lines.extend(
        [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc_attr(tw_t)}">',
            f'<meta name="twitter:description" content="{esc_attr(tw_d)}">',
            f'<meta name="twitter:image" content="{OG_IMAGE}">',
            f'<link rel="canonical" href="{canon}">',
        ]
    )
    return "\n".join(lines)


def build_legacy_static_page_block(
    legacy: LegacySeo | None,
    canon: str,
    title_inner: str,
    home_fb: LegacySeo | None,
    *,
    include_keywords_fallback: str = "",
    extra_before_description: tuple[str, ...] = (),
) -> str:
    """
    Full legacy-style meta block. `canon` is full URL (e.g. SITE or SITE + '/about').
    Omits <meta name="keywords"> if legacy has no keywords and include_keywords_fallback is empty.
    """
    if legacy:
        desc = (legacy.description or "").strip() or decode_entities(title_inner.strip())
        og_t = legacy.og_title or legacy.title or decode_entities(title_inner.strip())
        og_d = (legacy.og_description or desc).strip() or desc
        tw_t = legacy.twitter_title or og_t
        tw_d = legacy.twitter_description or og_d
        gsv, fd, fb_meta, fb_admins = pick_verifications(legacy, home_fb)
        kw = (legacy.keywords or "").strip()
    else:
        desc = decode_entities(title_inner.strip())
        og_t = desc
        og_d = desc
        tw_t = og_t
        tw_d = og_d
        gsv, fd, fb_meta, fb_admins = pick_verifications(None, home_fb)
        kw = ""
    if not kw and include_keywords_fallback.strip():
        kw = include_keywords_fallback.strip()

    pre_g = gsv[:2]
    post_g = gsv[2:] if len(gsv) > 2 else []
    lines: list[str] = []
    lines.extend(favicon_tags())
    lines.extend(extra_before_description)
    for tok in pre_g:
        lines.append(
            f'<meta name="google-site-verification" content="{esc_attr(tok)}">'
        )
    lines.append(f'<meta name="description" content="{esc_attr(desc)}">')
    lines.extend(
        [
            f'<meta property="og:title" content="{esc_attr(og_t)}">',
            f'<meta property="og:description" content="{esc_attr(og_d)}">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
            f'<meta property="og:image:width" content="{OG_IMG_W}">',
            f'<meta property="og:image:height" content="{OG_IMG_H}">',
            f'<meta property="og:url" content="{canon}">',
            '<meta property="og:site_name" content="Nexperts Academy">',
            '<meta property="og:type" content="website">',
        ]
    )
    if kw:
        lines.append(f'<meta name="keywords" content="{esc_attr(kw)}">')
    for tok in post_g:
        lines.append(
            f'<meta name="google-site-verification" content="{esc_attr(tok)}">'
        )
    if fd:
        lines.append(
            f'<meta name="facebook-domain-verification" content="{esc_attr(fd)}">'
        )
    if fb_meta:
        lines.append(f'<meta name="fb_admins_meta_tag" content="{esc_attr(fb_meta)}">')
    if fb_admins:
        lines.append(f'<meta property="fb:admins" content="{esc_attr(fb_admins)}">')
    lines.extend(
        [
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc_attr(tw_t)}">',
            f'<meta name="twitter:description" content="{esc_attr(tw_d)}">',
            f'<meta name="twitter:image" content="{OG_IMAGE}">',
            f'<link rel="canonical" href="{canon}">',
        ]
    )
    return "\n".join(lines)


def build_home_seo_block(home: LegacySeo | None, title_inner: str) -> str:
    canon = f"{SITE}/"
    home_extra = (
        '<meta name="robots" content="index, follow">',
        '<meta name="language" content="English">',
        '<meta name="author" content="Nexperts Academy">',
        '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
    )
    fb_kw = (
        "ccna, cisco, azure, python, data science, networking,web development,frontend,"
        "ccnp,sql,Networking Course Malaysia,Computer Networking Course,It Training"
    )
    if not home:
        return build_legacy_static_page_block(
            None,
            canon,
            title_inner,
            None,
            include_keywords_fallback=fb_kw,
            extra_before_description=home_extra,
        )
    return build_legacy_static_page_block(
        home,
        canon,
        title_inner,
        home,
        include_keywords_fallback=fb_kw if not (home.keywords or "").strip() else "",
        extra_before_description=home_extra,
    )


def build_simple_root_block(canonical_url: str, description: str, og_title: str) -> str:
    e_desc = esc_attr(description)
    e_title = esc_attr(og_title)
    return "\n".join(
        [
            *favicon_tags(),
            f'<meta name="description" content="{e_desc}">',
            f'<link rel="canonical" href="{canonical_url}">',
            f'<meta property="og:title" content="{e_title}">',
            f'<meta property="og:description" content="{e_desc}">',
            f'<meta property="og:url" content="{canonical_url}">',
            '<meta property="og:type" content="website">',
            f'<meta property="og:image" content="{OG_IMAGE}">',
            f'<meta property="og:image:width" content="{OG_IMG_W}">',
            f'<meta property="og:image:height" content="{OG_IMG_H}">',
        ]
    )


def process_courses(
    by_slug: dict[str, LegacySeo],
    home: LegacySeo | None,
    seo_pages: dict[str, LegacySeo],
):
    course_paths: list[tuple[Path, str]] = []
    for slug, fname in ROOT_CANONICAL_FILES.items():
        path = ROOT / fname
        if path.exists():
            course_paths.append((path, slug))
    folder = ROOT / "courses"
    for path in sorted(folder.glob("*.html")):
        slug = path.stem
        if slug in ROOT_CANONICAL_FILES or path.name == "ceh-v13-ai.html":
            continue
        course_paths.append((path, slug))

    for path, slug in course_paths:
        html = path.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        legacy = by_slug.get(slug) or seo_pages.get(canonical_path_for_slug(slug))
        if legacy and legacy.title:
            html = replace_title_tag(html, legacy.title)
        title_inner = extract_title(html)
        if not title_inner:
            print(f"SKIP (no title): {path.name}")
            continue
        block = build_course_seo_block(slug, title_inner, legacy, home)
        try:
            html = inject_block_after_title(html, block)
        except ValueError:
            print(f"SKIP (inject failed): {path.name}")
            continue
        path.write_text(html, encoding="utf-8", newline="\n")
        tag = "legacy" if legacy else "generated"
        rel = path.relative_to(ROOT).as_posix()
        print(f"OK {rel} ({tag})")


def process_root_pages(home: LegacySeo | None, seo_pages: dict[str, LegacySeo]):
    index_block = None
    if home:
        idx = ROOT / "index.html"
        if idx.exists():
            html_i = idx.read_text(encoding="utf-8")
            html_i = remove_existing_block(html_i)
            ti = extract_title(html_i)
            if ti and home.title:
                html_i = replace_title_tag(html_i, home.title)
            ti = extract_title(html_i) or ti
            block = build_home_seo_block(home, ti or "")
            try:
                html_i = inject_block_after_title(html_i, block)
                idx.write_text(html_i, encoding="utf-8", newline="\n")
                print("OK index.html (legacy homepage SEO)")
            except ValueError as e:
                print(f"SKIP index.html: {e}")
        index_block = True

    if not index_block and home is None:
        pages = [
            (
                "index.html",
                SITE,
                "Nexperts Academy offers IT certification training in Malaysia. CCNA, CEH, CISSP, AWS, Azure and 120+ courses delivered by certified practitioners in Kuala Lumpur.",
            ),
        ]
        for fname, canon, desc in pages:
            path = ROOT / fname
            if not path.exists():
                continue
            html = path.read_text(encoding="utf-8")
            html = remove_existing_block(html)
            ti = extract_title(html)
            if not ti:
                continue
            block = build_simple_root_block(canon, desc, decode_entities(ti))
            try:
                html = inject_block_after_title(html, block)
                path.write_text(html, encoding="utf-8", newline="\n")
                print(f"OK {fname}")
            except ValueError:
                print("SKIP index.html (inject failed)")

    static_specs: list[tuple[str, str, str, str]] = [
        (
            "about.html",
            "/about",
            "About Nexperts Academy — IT certification training in Malaysia & the US. Meet our instructors, Kuala Lumpur HQ & Albany NY offices, and hands-on exam-ready programmes.",
        ),
        (
            "contact.html",
            "/contact",
            "Contact Nexperts Academy for course enquiries, corporate training & HRD Corp in Kuala Lumpur (HQ) and Albany NY. Fast replies within 4 business hours.",
        ),
        (
            "privacy-policy.html",
            "/privacy-policy",
            "Privacy Policy for Nexperts Academy Sdn Bhd — how we collect, use and protect personal data under the Malaysian PDPA.",
        ),
    ]
    for fname, export_key, desc_fallback in static_specs:
        path = ROOT / fname
        if not path.exists():
            print(f"MISSING {fname}")
            continue
        html = path.read_text(encoding="utf-8")
        html = remove_existing_block(html)
        if fname == "contact.html":
            html = remove_contact_legacy_meta(html)
        leg = seo_pages.get(export_key) if seo_pages else None
        if leg and leg.title:
            html = replace_title_tag(html, leg.title)
        ti = extract_title(html)
        if not ti:
            print(f"SKIP (no title): {fname}")
            continue
        canon = f"{SITE}{export_key}"
        if leg:
            block = build_legacy_static_page_block(leg, canon, ti, home)
        else:
            block = build_simple_root_block(canon, desc_fallback, decode_entities(ti))
        try:
            html = inject_block_after_title(html, block)
        except ValueError as e:
            print(f"SKIP {fname}: {e}")
            continue
        path.write_text(html, encoding="utf-8", newline="\n")
        tag = "legacy" if leg else "fallback"
        print(f"OK {fname} ({tag} SEO, canonical {export_key})")


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
            + build_simple_root_block(canon, desc, title_inner)
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
        block = build_simple_root_block(canon, desc, title_inner)
        try:
            html = inject_block_after_title(html, block)
            beyond.write_text(html, encoding="utf-8", newline="\n")
            print("OK Nexperts beyond.html")
        except ValueError:
            print("SKIP Nexperts beyond.html")


def main():
    seo_pages = parse_seo_export(ROOT)
    by_slug, home_fb = legacy_by_slug(ROOT)
    home = seo_pages.get("/") or home_fb
    print(f"Legacy SEO entries mapped to slugs: {len(by_slug)}")
    process_courses(by_slug, home, seo_pages)
    process_root_pages(home, seo_pages)
    process_admin_and_beyond()


if __name__ == "__main__":
    main()
