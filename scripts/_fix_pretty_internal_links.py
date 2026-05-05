# -*- coding: utf-8 -*-
"""One-shot: root + courses hrefs → pretty paths (/ /about /contact-us /privacy-policy)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fix_href_text(t: str, *, in_course_dir: bool) -> str:
    if in_course_dir:
        pairs = [
            ('href="../index.html#', 'href="/#'),
            ("href='../index.html#", "href='/#"),
            ('href="../index.html"', 'href="/"'),
            ("href='../index.html'", "href='/'"),
            ('href="../contact.html?', 'href="/contact-us?'),
            ("href='../contact.html?", "href='/contact-us?"),
            ('href="../contact.html#', 'href="/contact-us#'),
            ("href='../contact.html#", "href='/contact-us#"),
            ('href="../contact.html"', 'href="/contact-us"'),
            ("href='../contact.html'", "href='/contact-us'"),
            ('href="../about.html#', 'href="/about#'),
            ("href='../about.html#", "href='/about#"),
            ('href="../about.html"', 'href="/about"'),
            ("href='../about.html'", "href='/about'"),
            ('href="../privacy-policy.html"', 'href="/privacy-policy"'),
            ("href='../privacy-policy.html'", "href='/privacy-policy'"),
        ]
    else:
        pairs = [
            ('href="index.html#', 'href="/#'),
            ("href='index.html#", "href='/#"),
            ('href="index.html"', 'href="/"'),
            ("href='index.html'", "href='/'"),
            ('href="contact.html?', 'href="/contact-us?'),
            ("href='contact.html?", "href='/contact-us?"),
            ('href="contact.html#', 'href="/contact-us#'),
            ("href='contact.html#", "href='/contact-us#"),
            ('href="contact.html"', 'href="/contact-us"'),
            ("href='contact.html'", "href='/contact-us'"),
            ('href="about.html#', 'href="/about#'),
            ("href='about.html#", "href='/about#"),
            ('href="about.html"', 'href="/about"'),
            ("href='about.html'", "href='/about'"),
            ('href="privacy-policy.html"', 'href="/privacy-policy"'),
            ("href='privacy-policy.html'", "href='/privacy-policy'"),
        ]
    for a, b in pairs:
        t = t.replace(a, b)
    return t


def fix_index_js(t: str) -> str:
    return (
        t.replace(
            "setActive(links.find(a=>a.getAttribute('href')==='index.html')||links[0],false);",
            "setActive(links.find(a=>a.getAttribute('href')==='/')||links[0],false);",
        )
        .replace(
            "return href==='index.html'||href==='/'||href===''||a.textContent.trim().toLowerCase()==='home';",
            "return href==='/'||href===''||a.textContent.trim().toLowerCase()==='home';",
        )
    )


def fix_about_js(t: str) -> str:
    return t.replace(
        "setActive(links.find(a=>(a.getAttribute('href')||'').includes('about.html'))||links[0],false);",
        "setActive(links.find(a=>(a.getAttribute('href')||'')==='/about')||links[0],false);",
    )


def main() -> None:
    changed = 0
    for p in sorted((ROOT / "courses").glob("*.html")):
        old = p.read_text(encoding="utf-8")
        new = fix_href_text(old, in_course_dir=True)
        if new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    for name in (
        "index.html",
        "about.html",
        "contact.html",
        "privacy-policy.html",
        "Nexperts beyond.html",
    ):
        p = ROOT / name
        if not p.exists():
            continue
        old = p.read_text(encoding="utf-8")
        new = fix_href_text(old, in_course_dir=False)
        if name == "index.html":
            new = fix_index_js(new)
        if name == "about.html":
            new = fix_about_js(new)
        if new != old:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    adm = ROOT / "admin" / "index.html"
    if adm.exists():
        old = adm.read_text(encoding="utf-8")
        new = old.replace('href="../index.html"', 'href="/"')
        if new != old:
            adm.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    sm = ROOT / "sitemap.xml"
    if sm.exists():
        text = sm.read_text(encoding="utf-8")
        text2 = text.replace(
            "https://www.nexpertsacademy.com/about.html",
            "https://www.nexpertsacademy.com/about",
        )
        text2 = text2.replace(
            "https://www.nexpertsacademy.com/contact.html",
            "https://www.nexpertsacademy.com/contact-us",
        )
        text2 = text2.replace(
            "https://www.nexpertsacademy.com/privacy-policy.html",
            "https://www.nexpertsacademy.com/privacy-policy",
        )
        text2 = re.sub(
            r"https://www\.nexpertsacademy\.com/courses/([\w.-]+)\.html",
            r"https://www.nexpertsacademy.com/courses/\1",
            text2,
        )
        if text2 != text:
            sm.write_text(text2, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Pretty link pass: {changed} files updated (incl. sitemap if changed)")


if __name__ == "__main__":
    main()
