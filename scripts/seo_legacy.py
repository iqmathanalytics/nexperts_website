# -*- coding: utf-8 -*-
"""Parse seo_tags_output.txt (legacy Wix export) and map legacy paths → course slug via _redirects."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class LegacySeo:
    title: str = ""
    description: str = ""
    keywords: str = ""
    og_title: str = ""
    og_description: str = ""
    twitter_title: str = ""
    twitter_description: str = ""
    google_site_verification: list[str] = field(default_factory=list)
    facebook_domain_verification: str = ""
    fb_admins: str = ""

    @classmethod
    def from_block(cls, body: str) -> LegacySeo:
        out = cls()
        tm = re.search(r"<title[^>]*>(.*?)</title>", body, re.DOTALL | re.I)
        if tm:
            out.title = re.sub(r"\s+", " ", tm.group(1).strip())

        for name, content in re.findall(
            r'<meta\s+name="([^"]+)"\s+content="([^"]*)"', body, re.I
        ):
            n = name.lower()
            if n == "description":
                out.description = content
            elif n == "keywords":
                out.keywords = content
            elif n == "google-site-verification":
                out.google_site_verification.append(content)
            elif n == "facebook-domain-verification":
                out.facebook_domain_verification = content
            elif n == "fb_admins_meta_tag":
                pass  # duplicate of fb:admins
            elif n == "twitter:title":
                out.twitter_title = content
            elif n == "twitter:description":
                out.twitter_description = content

        for prop, content in re.findall(
            r'<meta\s+property="([^"]+)"\s+content="([^"]*)"', body, re.I
        ):
            p = prop.lower()
            if p == "og:title":
                out.og_title = content
            elif p == "og:description":
                out.og_description = content

        for prop, content in re.findall(
            r'<meta\s+property="([^"]+)"\s+content="([^"]*)"', body, re.I
        ):
            if prop.lower() == "fb:admins":
                out.fb_admins = content

        return out


def parse_seo_tags_file(text: str) -> dict[str, LegacySeo]:
    """Keys are URL paths like '/' or '/ccna'."""
    pages: dict[str, LegacySeo] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("https://"):
            raw_url = line
            i += 1
            body_chunks: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("https://"):
                body_chunks.append(lines[i])
                i += 1
            body = "\n".join(body_chunks)
            path = urlparse(raw_url).path or "/"
            if not path.startswith("/"):
                path = "/" + path
            pages[path.rstrip("/") or "/"] = LegacySeo.from_block(body)
        else:
            i += 1
    # Normalize '' to '/'
    if "/" not in pages and "" in pages:
        pages["/"] = pages[""]
    return pages


def redirect_slug_map(redirects_text: str) -> dict[str, str]:
    """Map legacy path (e.g. '/ccna') → slug stem (e.g. 'ccna')."""
    m: dict[str, str] = {}
    for line in redirects_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        mo = re.match(
            r"^(/[^\s]+)\s+(?:/course_pages/([\w.-]+)\.html|/courses/([\w.-]+))\s+301\s*$",
            line,
        )
        if mo:
            slug = mo.group(2) or mo.group(3)
            if slug:
                m[mo.group(1)] = slug
    return m


def parse_seo_export(root: Path) -> dict[str, LegacySeo]:
    """Load seo_tags_output.txt; empty dict if missing."""
    seo_path = root / "seo_tags_output.txt"
    if not seo_path.exists():
        return {}
    return parse_seo_tags_file(seo_path.read_text(encoding="utf-8"))


def legacy_by_slug(
    root: Path,
) -> tuple[dict[str, LegacySeo], LegacySeo | None]:
    """
    Returns:
      slug -> LegacySeo for course detail URLs present in both seo_tags_output and _redirects
      home_legacy: LegacySeo for '/' from export (or None)
    """
    seo_path = root / "seo_tags_output.txt"
    red_path = root / "_redirects"
    if not seo_path.exists():
        return {}, None
    pages = parse_seo_tags_file(seo_path.read_text(encoding="utf-8"))
    home = pages.get("/")
    path_map = redirect_slug_map(red_path.read_text(encoding="utf-8"))
    by_slug: dict[str, LegacySeo] = {}
    for legacy_path, slug in path_map.items():
        key = legacy_path.rstrip("/") or "/"
        pg = pages.get(key)
        if pg:
            by_slug[slug] = pg
    return by_slug, home
