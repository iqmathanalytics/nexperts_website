# -*- coding: utf-8 -*-
"""
Regenerate root _redirects for Cloudflare Pages / Netlify.

Uses EXPLICIT lines for every /courses/{slug} rewrite and legacy 301 (no :slug
placeholders) so local tooling that only partially implements _redirects still
works. For local preview, prefer `netlify dev` or Wrangler; plain `python -m
http.server` ignores _redirects entirely.

SEO: single-hop 301s (flattened), trailing-slash variants, /courses/*.html → /courses/{slug}.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REDIRECTS = ROOT / "_redirects"

_COURSE_200 = re.compile(r"^/courses/([\w.-]+)\s+/courses/([\w.-]+)\.html\s+200\s*$")
# Bogus trailing slash after a course detail filename (never link these on purpose).
_NOISE_COURSE_HTML_SLASH = re.compile(
    r"^/(?:course_pages|courses)/[\w.-]+\.html/$"
)

_REDIRECTS_PREAMBLE = """# =============================================================================
# _redirects — SEO routing (Cloudflare Pages / Netlify)
# =============================================================================
#
# HTTPS + www: configure at the edge (Cloudflare Redirect Rules / Netlify domains).
#
# LOCAL: Use Netlify CLI (`npm run dev`) or `python scripts/local_dev_server.py`.
# Plain `python -m http.server` ignores this file. Open courses/*.html only
# for a quick file check.
#
# ORDER: First match wins. Put 200 rewrites BEFORE trailing-slash 301s: Netlify
# matches /path and /path/ as the same for redirect rules, so /path/→/path 301
# would otherwise beat /path → file 200 and break pretty course URLs.
#
# All rules below are EXPLICIT (no :slug placeholders) for maximum compatibility.
# =============================================================================
"""

_SKIP_SECTION_COMMENTS = frozenset(
    {
        "# Public course URLs (pretty path); serve courses/{slug}.html (200)",
        "# --- Trailing slash removal (301; non-trailing slash is canonical) ---",
        "# Static site pages (pretty path); serve root *.html (200)",
        "# Legacy & vanity → canonical /courses/{slug} (301; flattened, single hop)",
        "# Direct /courses/{slug}.html bookmarks → pretty /courses/{slug} (301)",
        "# Filename & legacy paths → pretty canonical URLs (301)",
        "# --- REVIEW: legacy semantics may not match current course positioning ---",
        "# Optional explicit 404:",
    }
)

LEGACY_REQUESTED_MAP: dict[str, str] = {
    "/ccna": "/courses/ccna",
    "/ceh": "/courses/ceh-v13-ai",
    "/cissp": "/courses/cissp",
    "/ecih": "/courses/ecih",
    "/aws-certified-solutions-architect": "/courses/aws-solutions-architect-associate",
    "/aws-cloud-practitioner": "/courses/aws-cloud-practitioner",
    "/aws-dataengineer-associate": "/courses/aws-data-engineer-associate",
    "/aws-advanced": "/courses/aws-solutions-architect-professional",
    "/azure-fundamentals": "/courses/az-900",
    "/microsoft-certified-azure-administrator": "/courses/az-104",
    "/azure-sc900": "/courses/sc-900",
    "/azure-dp900": "/courses/dp-900",
    "/azure-ai900": "/courses/ai-900",
    "/microsoft-power-bi": "/courses/pl-300",
    "/artificial-intelligence-machine-learning": "/courses/ai-102",
    "/data-science-with-python": "/courses/data-science-with-python",
    "/data-analytics-associate-with-python": "/courses/sql-for-data-professionals",
    "/python-bootcamp": "/courses/python-bootcamp",
    "/ccnp-encor": "/courses/ccnp-enterprise",
    "/cisco-scor": "/courses/ccnp-security",
    "/cisco-spcor": "/courses/cisco-spcor",
    "/cisco-dccor": "/courses/cisco-dccor",
    "/sdwan": "/courses/sdwan",
    "/cisco-certified-devnet-associate": "/courses/devnet-associate",
    "/itil5-foundation-certification": "/courses/itil-4-foundation",
    "/prince2-certification": "/courses/prince2-foundation-practitioner",
    "/devops-fundamentals": "/courses/az-400",
    "/microsoft-power-apps": "/courses/pl-100",
    "/java-programming": "/courses/java-programming",
    "/full-stack-web-development": "/courses/full-stack-web-development",
    "/digitalmarketing": "/courses/digital-marketing",
    "/excel-basic": "/courses/excel-basic",
    "/copy-of-microsoft-excel-basic": "/courses/excel-advanced-analytics",
    "/microsoft-excel-advanced": "/courses/excel-advanced-analytics",
    "/redhat-rhcsa-and-rhce-cert": "/courses/linux-administration",
    "/network-security": "/courses/ccnp-security",
    "/salesforce-admin-and-automation": "/courses/salesforce-admin",
    "/servicenow-administration": "/courses/servicenow-admin",
    "/servicenow-platform": "/courses/servicenow-platform",
}


def transform_dest_course_html(dest: str) -> str:
    for pat in (
        r"^/courses/([\w.-]+)\.html$",
        r"^/course_pages/([\w.-]+)\.html$",
    ):
        mo = re.match(pat, dest)
        if mo:
            return f"/courses/{mo.group(1)}"
    return dest


def skip_regenerated_rule_line(norm: str) -> bool:
    if norm in _SKIP_SECTION_COMMENTS:
        return True
    m = _COURSE_200.match(norm)
    if m and m.group(1) == m.group(2):
        return True
    static_200 = {
        "/about /about.html 200",
        "/contact-us /contact.html 200",
        "/privacy-policy /privacy-policy.html 200",
    }
    if norm in static_200:
        return True
    pretty_301 = {
        "/index.html / 301",
        "/about.html /about 301",
        "/contact.html /contact-us 301",
        "/privacy-policy.html /privacy-policy 301",
        "/contact /contact-us 301",
    }
    if norm in pretty_301:
        return True
    return False


def parse_301_rules_from_body(body: list[str]) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    seen_src: set[str] = set()
    for line in body:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        norm = stripped.split("#")[0].strip()
        if skip_regenerated_rule_line(norm):
            continue
        m301 = re.match(r"^(\S+)\s+(\S+)\s+301(?:\s|$)", norm)
        if not m301:
            continue
        src, dst = m301.group(1), m301.group(2)
        if ":" in src or ":" in dst:
            continue
        if "/course_pages/" in src:
            continue
        if _NOISE_COURSE_HTML_SLASH.match(src):
            continue
        dst = transform_dest_course_html(dst)
        if src in seen_src:
            continue
        seen_src.add(src)
        rules.append((src, dst))
    return rules


def flatten_chains(rules: list[tuple[str, str]]) -> list[tuple[str, str]]:
    rmap = dict(rules)
    out: list[tuple[str, str]] = []
    for src, _ in rules:
        dest = rmap[src]
        visited: set[str] = {src}
        while dest in rmap:
            if dest in visited:
                break
            visited.add(dest)
            dest = rmap[dest]
        out.append((src, dest))
    return out


def sort_rules_longest_src_first(rules: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return sorted(rules, key=lambda t: (-len(t[0]), t[0]))


def trailing_slash_rules(
    all_301: list[tuple[str, str]], slugs: list[str]
) -> list[tuple[str, str]]:
    # On Cloudflare Pages, slash normalization can vary by route and may cause
    # loops if we emit slash-removal 301s. Keep this empty and serve both forms
    # with explicit 200 rewrites instead.
    return []


def review_suffix(path: str) -> str:
    return ""


_SLUG_FROM_CP = re.compile(r"/courses/([\w.-]+)\.html")
_CP_BOOKMARK = re.compile(r"^/courses/([\w.-]+)\.html$")


def is_canonical_courses_html_bookmark(src: str, dest: str) -> bool:
    """True for /courses/{slug}.html → /courses/{slug} (emitted in final section)."""
    m = _CP_BOOKMARK.match(src)
    return bool(m and dest == f"/courses/{m.group(1)}")


def discover_slugs() -> list[str]:
    """Prefer on-disk courses/*.html; else recover slugs from existing _redirects."""
    cp = ROOT / "courses"
    if cp.is_dir():
        slugs = sorted({p.stem for p in cp.glob("*.html")})
        if slugs:
            return slugs
    if not REDIRECTS.is_file():
        return []
    text = REDIRECTS.read_text(encoding="utf-8")
    found: set[str] = set()
    for line in text.splitlines():
        for m in _SLUG_FROM_CP.finditer(line):
            found.add(m.group(1))
    return sorted(found)


def main() -> None:
    slugs = discover_slugs()
    slug_set = set(slugs)
    legacy_rules: list[tuple[str, str]] = []
    for src, dst in LEGACY_REQUESTED_MAP.items():
        if not src.startswith("/"):
            continue
        m = re.match(r"^/courses/([\w.-]+)$", dst)
        if m and m.group(1) in slug_set:
            legacy_rules.append((src, dst))

    flat_sorted = sort_rules_longest_src_first(legacy_rules)
    trail_sorted = sort_rules_longest_src_first(
        trailing_slash_rules(flat_sorted, slugs)
    )
    trail_srcs = {s for s, _ in trail_sorted}
    flat_sorted = [(s, d) for s, d in flat_sorted if s not in trail_srcs]

    lines: list[str] = [
        _REDIRECTS_PREAMBLE.rstrip("\n"),
        "",
        "# Public course URLs (pretty path); serve courses/{slug}.html (200)",
    ]
    for slug in slugs:
        lines.append(f"/courses/{slug} /courses/{slug}.html 200")
        lines.append(f"/courses/{slug}/ /courses/{slug}.html 200")

    lines.extend(
        [
            "/about/ /about.html 200",
            "/contact-us/ /contact.html 200",
            "/privacy-policy/ /privacy-policy.html 200",
        ]
    )

    lines.extend(
        [
            "",
            "# Static site pages (pretty path); serve root *.html (200)",
            "/about /about.html 200",
            "/contact-us /contact.html 200",
            "/privacy-policy /privacy-policy.html 200",
            "",
            "# --- Trailing slash removal (301; non-trailing slash is canonical) ---",
        ]
    )
    for s, d in trail_sorted:
        lines.append(f"{s} {d} 301")

    lines.extend(
        [
            "",
            "# Legacy & vanity → canonical /courses/{slug} (301; flattened, single hop)",
        ]
    )
    for s, d in flat_sorted:
        lines.append(f"{s} {d} 301")

    lines.extend(
        [
            "",
            "# Filename & legacy paths → pretty canonical URLs (301)",
            "/index.html / 301",
            "/about.html /about 301",
            "/contact.html /contact-us 301",
            "/privacy-policy.html /privacy-policy 301",
            "",
            "# Optional explicit 404:",
            "# /* /404.html 404",
        ]
    )

    REDIRECTS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(
        f"Wrote {REDIRECTS.name}: {len(slugs)} courses; "
        f"{len(trail_sorted)} trailing 301s; {len(flat_sorted)} flat 301s"
    )


if __name__ == "__main__":
    main()
