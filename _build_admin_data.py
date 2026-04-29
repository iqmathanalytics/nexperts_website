# -*- coding: utf-8 -*-
"""Generate admin/admin-data.json with the baseline catalog data.

This is the immutable seed shipped with the repo. The actual admin
edits live entirely in localStorage (key: nexperts_admin_v1) so the
admin can reset back to this baseline at any time.
"""
from __future__ import annotations

from pathlib import Path
import json
import re

# Pull catalog metadata from the existing build script.
import importlib.util
import sys

ROOT = Path(__file__).parent
CATALOG = ROOT / "_build_catalog.py"

spec = importlib.util.spec_from_file_location("_build_catalog", CATALOG)
catalog = importlib.util.module_from_spec(spec)
sys.modules["_build_catalog"] = catalog
spec.loader.exec_module(catalog)

P1 = catalog.P1
BRANDS = catalog.BRANDS
CARDS = catalog.CARDS
name_to_slug = catalog.name_to_slug

OUT = ROOT / "admin" / "admin-data.json"
OUT.parent.mkdir(exist_ok=True)

PAGES = ROOT / "course_pages"

# --------------------------------------------------------------------------
# Detail-page parsers
# --------------------------------------------------------------------------
PRICE_RX = re.compile(r'<span class="price">\s*([^<]+?)\s*</span>')
PRICE_ORIG_RX = re.compile(r'<span class="price-orig">\s*([^<]+?)\s*</span>')
PRICE_SAVE_RX = re.compile(r'<span class="price-save">\s*([^<]+?)\s*</span>')
DURATION_RX = re.compile(
    r'<div class="smeta-row"><span>Duration</span><strong>\s*([^<]+?)\s*</strong></div>',
    re.IGNORECASE,
)
INTAKE_RX = re.compile(
    r'<div class="smeta-row"><span>Next intake</span><strong>\s*([^<]+?)\s*</strong></div>',
    re.IGNORECASE,
)


def detail_for(slug: str) -> dict:
    """Return {duration, next_intake, price, price_original, price_save} or {}."""
    path = PAGES / f"{slug}.html"
    if not path.exists():
        return {}
    h = path.read_text(encoding="utf-8")
    out = {}
    if (m := PRICE_RX.search(h)):          out["price"] = m.group(1)
    if (m := PRICE_ORIG_RX.search(h)):     out["price_original"] = m.group(1)
    if (m := PRICE_SAVE_RX.search(h)):     out["price_save"] = m.group(1)
    if (m := DURATION_RX.search(h)):       out["duration"] = m.group(1)
    if (m := INTAKE_RX.search(h)):         out["next_intake"] = m.group(1)
    return out


# --------------------------------------------------------------------------
# Build payload
# --------------------------------------------------------------------------
brand_meta = {
    bm[0]: {
        "key": bm[0],
        "label": bm[1],
        "tagline": bm[3],
        "color": bm[4],
        "color_tint": bm[5],
    }
    for bm in BRANDS
}

courses = []
order_by_brand: dict[str, list[str]] = {}

for c in CARDS:
    (brand, cat, vendor, badge_label, name, desc, level,
     rating, reviews, enrolled) = c
    slug = P1.get(name) or name_to_slug(name)
    has_detail = slug in P1.values()
    detail = detail_for(slug) if has_detail else {}

    courses.append({
        "slug": slug,
        "brand": brand,
        "category": cat,
        "vendor": vendor,
        "badge": badge_label,
        "name": name,
        "description": desc,
        "level": level,
        "rating": rating,
        "reviews": reviews,
        "enrolled": enrolled,
        "has_detail_page": has_detail,
        "duration": detail.get("duration", ""),
        "next_intake": detail.get("next_intake", ""),
        "price": detail.get("price", ""),
        "price_original": detail.get("price_original", ""),
        "price_save": detail.get("price_save", ""),
    })
    order_by_brand.setdefault(brand, []).append(slug)

brand_order = [b[0] for b in BRANDS if b[0] in order_by_brand]

payload = {
    "version": 1,
    "generated_at": "build-time",
    "brand_meta": brand_meta,
    "brand_order": brand_order,
    "card_order": order_by_brand,
    "courses": courses,
}

OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT.relative_to(ROOT)}")
print(f"  brands  : {len(brand_order)}")
print(f"  courses : {len(courses)}")
print(f"  with detail page: {sum(1 for c in courses if c['has_detail_page'])}")
