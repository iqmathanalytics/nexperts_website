from __future__ import annotations

from pathlib import Path

ROOT_CANONICAL_FILES: dict[str, str] = {
    "ccna": "ccna.html",
    "python-bootcamp": "python-bootcamp.html",
    "data-science-with-python": "data-science-with-python.html",
    "ceh": "ceh.html",
}

SLUG_ALIASES: dict[str, str] = {
    "ceh-v13-ai": "ceh",
}


def canonical_slug(slug: str) -> str:
    return SLUG_ALIASES.get(slug, slug)


def canonical_path_for_slug(slug: str) -> str:
    slug = canonical_slug(slug)
    if slug in ROOT_CANONICAL_FILES:
        return f"/{slug}"
    return f"/courses/{slug}"


def detail_html_path(root: Path, slug: str) -> Path:
    slug = canonical_slug(slug)
    if slug in ROOT_CANONICAL_FILES:
        return root / ROOT_CANONICAL_FILES[slug]
    return root / "courses" / f"{slug}.html"
