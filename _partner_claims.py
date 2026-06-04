# -*- coding: utf-8 -*-
"""Only CompTIA and EC-Council may be shown as official training partners."""
from __future__ import annotations

import re

PARTNER_VENDOR_BADGE_RE = re.compile(
    r"\n?\s*<span class=\"cbadge cb-vendor\">([^<]*)</span>",
    re.IGNORECASE,
)
PARTNER_CHECK_RE = re.compile(
    r"<div style=\"display:flex;align-items:flex-start;gap:10px[^\"]*\"[^>]*>\s*"
    r"<span style=\"color:var\(--green\)[^\"]*\"[^>]*>✓</span>\s*([^<]+)</div>",
    re.IGNORECASE,
)
INCLUDE_ITEM_RE = re.compile(r"<div class=\"include-item\">([^<]*)</div>", re.IGNORECASE)

INCLUDE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("PMI Authorized ATP courseware", "Official PMP exam courseware"),
    ("Digital badge from Nexperts ATP", "Digital credential badge from Nexperts Academy"),
    ("OffSec Authorized Training Partner", ""),
    ("OffSec Authorised Training Partner", ""),
    ("Microsoft Authorised training provider", ""),
    ("Microsoft Authorized training provider", ""),
)


def is_official_partner_text(text: str) -> bool:
    t = text.lower()
    return "comptia" in t or "ec-council" in t or "ec council" in t


def filter_badges(badges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for cls, txt in badges:
        if cls == "cb-vendor" and not is_official_partner_text(txt):
            continue
        out.append((cls, txt))
    return out


def sanitize_partner_text(text: str) -> str:
    if not text or is_official_partner_text(text):
        return text
    for old, new in INCLUDE_REPLACEMENTS:
        if old.lower() in text.lower():
            text = new
    lower = text.lower()
    partner_markers = (
        "authorised",
        "authorized",
        "authorisation",
        "authorization",
        " learning partner",
        " training partner",
        " atp ",
        " ato",
        " atc",
    )
    if any(m in lower for m in partner_markers):
        return ""
    return text


def sanitize_partner_html(html: str) -> str:
    def badge_repl(m: re.Match[str]) -> str:
        return m.group(0) if is_official_partner_text(m.group(1)) else ""

    html = PARTNER_VENDOR_BADGE_RE.sub(badge_repl, html)

    def check_repl(m: re.Match[str]) -> str:
        return m.group(0) if is_official_partner_text(m.group(1)) else ""

    html = PARTNER_CHECK_RE.sub(check_repl, html)

    def include_repl(m: re.Match[str]) -> str:
        cleaned = sanitize_partner_text(m.group(1))
        return f'<div class="include-item">{cleaned}</div>' if cleaned else ""

    html = INCLUDE_ITEM_RE.sub(include_repl, html)
    return html
