# -*- coding: utf-8 -*-
"""Build Cisco Certification Path blog from docx and wire site-wide."""
from __future__ import annotations

import html as html_lib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from site_nav import NAV_ASSET_TAGS, render_site_nav  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"

SITE = "https://www.nexpertsacademy.com"
SLUG = "cisco-certification-path"
VANITY_PATH = "/cisco-certification-path"
IMG_SLUG = "cisco-certification-path"
META_TITLE = "Cisco Certification Path 2026: CCNA, CCNP & CCIE Roadmap"
META_DESC = (
    "Explore the complete Cisco Certification Path from CCNA to CCNP and CCIE. "
    "Learn certification levels, career opportunities, exam roadmap, and choose the right Cisco course for your goals."
)
DOCX = ROOT / "Cisco Certification Path_ CCNA, CCNP & CCIE Explained.docx"
IMG_DIR = ROOT / "image" / "blog" / IMG_SLUG

SKIP_LINES = {
    "h1",
    "meta title",
    "meta description",
    "url",
    META_TITLE.lower(),
    META_DESC.lower(),
    VANITY_PATH,
    f"{VANITY_PATH}/",
    "/blog/cisco-certification-path/",
    "cisco certification path: ccna, ccnp & ccie explained",
}


def _esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def _slugify(text: str) -> str:
    t = re.sub(r"<[^>]+>", "", text)
    t = re.sub(r"[^a-zA-Z0-9\s-]", "", t.lower())
    t = re.sub(r"\s+", "-", t.strip())
    return t[:80] or "section"


def _run_text(run: ET.Element) -> str:
    bold = run.find(f"{W}rPr/{W}b") is not None
    parts: list[str] = []
    for node in run:
        if node.tag == f"{W}t":
            t = node.text or ""
            parts.append(f"<strong>{_esc(t)}</strong>" if bold and t else _esc(t))
        elif node.tag == f"{W}tab":
            parts.append(" ")
        elif node.tag == f"{W}br":
            parts.append("<br>")
    return "".join(parts)


def _para_text(p: ET.Element) -> str:
    texts: list[str] = []
    for child in p:
        if child.tag == f"{W}r":
            texts.append(_run_text(child))
    return "".join(texts).strip()


def _table_html(tbl: ET.Element) -> str:
    rows: list[list[str]] = []
    for tr in tbl.findall(f"{W}tr"):
        cells = []
        for tc in tr.findall(f"{W}tc"):
            cell_parts = []
            for p in tc.findall(f"{W}p"):
                t = _para_text(p)
                if t:
                    cell_parts.append(t)
            cells.append("<br>".join(cell_parts) if cell_parts else "")
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    thead = ""
    tbody_rows = rows
    if len(rows) >= 2:
        head = rows[0]
        if all(head) and len(head) == ncols:
            thead = "<thead><tr>" + "".join(f'<th scope="col">{c}</th>' for c in head) + "</tr></thead>"
            tbody_rows = rows[1:]
    body = ""
    for row in tbody_rows:
        padded = row + [""] * (ncols - len(row))
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in padded[:ncols]) + "</tr>"
    compare = " blog-table--compare" if ncols == 3 else ""
    return (
        f'<div class="blog-table-wrap"><table class="blog-table{compare}">'
        f"{thead}<tbody>{body}</tbody></table></div>"
    )


def _should_skip(plain: str) -> bool:
    key = plain.strip().lower()
    if key in SKIP_LINES:
        return True
    if key.startswith("h1") and "cisco certification path" in key:
        return True
    return False


def docx_to_body(docx_path: Path) -> tuple[str, list[tuple[str, str]], str]:
    z = zipfile.ZipFile(docx_path)
    rels = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    rel_map = {rel.get("Id"): rel.get("Target") for rel in rels.findall(f"{REL_NS}Relationship")}
    root = ET.fromstring(z.read("word/document.xml"))
    body_el = root.find(f"{W}body")
    if body_el is None:
        raise SystemExit("No body in docx")

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    img_counter = [0]
    saved_media: dict[str, str] = {}
    blocks: list[str] = []
    toc: list[tuple[str, str]] = []
    list_buf: list[str] = []
    title = "Cisco Certification Path: CCNA, CCNP & CCIE Explained"
    h2_counter = 0
    in_faq = False
    faq_buf: list[tuple[str, str]] = []
    pending_q = ""
    saw_intro = False

    def flush_list() -> None:
        nonlocal list_buf
        if list_buf:
            blocks.append("<ul>" + "".join(list_buf) + "</ul>")
            list_buf = []

    def flush_faq() -> None:
        nonlocal faq_buf, in_faq, pending_q
        if pending_q:
            faq_buf.append((pending_q, ""))
            pending_q = ""
        if not faq_buf:
            in_faq = False
            return
        items = []
        for q, a in faq_buf:
            items.append(
                f'<div class="faq-item"><p class="faq-q"><strong>{q}</strong></p><p>{a}</p></div>'
            )
        blocks.append('<section class="blog-faq">' + "".join(items) + "</section>")
        faq_buf = []
        in_faq = False

    for child in body_el:
        tag = child.tag
        if tag == f"{W}tbl":
            flush_list()
            if in_faq:
                flush_faq()
            tbl = _table_html(child)
            if tbl:
                blocks.append(tbl)
            continue

        if tag != f"{W}p":
            continue

        p = child
        for drawing in p.iter(f"{W}drawing"):
            for blip in drawing.iter(f"{A}blip"):
                rid = blip.get(f"{R_NS}embed")
                if rid and rid in rel_map:
                    target = rel_map[rid]
                    media_name = target.split("/")[-1]
                    if rid not in saved_media:
                        img_counter[0] += 1
                        ext = Path(media_name).suffix.lower() or ".jpg"
                        fname = f"image{img_counter[0]}{ext}"
                        saved_media[rid] = fname
                        (IMG_DIR / fname).write_bytes(z.read(f"word/{target.lstrip('/')}"))
                    fname = saved_media[rid]
                    flush_list()
                    if in_faq:
                        flush_faq()
                    blocks.append(
                        f'<figure class="blog-figure"><img src="/image/blog/{IMG_SLUG}/{fname}" '
                        f'alt="Cisco certification path CCNA CCNP CCIE roadmap" loading="lazy" width="720" height="405"></figure>'
                    )
                    break

        p_pr = p.find(f"{W}pPr")
        style = ""
        is_list = False
        if p_pr is not None:
            ps = p_pr.find(f"{W}pStyle")
            if ps is not None:
                style = ps.get(f"{W}val") or ""
            if p_pr.find(f"{W}numPr") is not None:
                is_list = True

        text = _para_text(p)
        if not text:
            continue

        plain = html_lib.unescape(re.sub(r"<[^>]+>", "", text).strip())
        if _should_skip(plain):
            continue

        # Skip duplicate H1 appearing again as intro heading
        if plain.lower().startswith("cisco certification path: ccna") and not saw_intro:
            # First real body H1 duplicate after meta — treat as page title already set
            if style in ("Heading1", "") and len(blocks) == 0:
                continue

        if style == "Heading1":
            title = plain
            continue

        if plain.lower() in {"faq", "frequently asked questions"} or (
            style == "Heading2" and plain.lower() == "faq"
        ):
            flush_list()
            if in_faq:
                flush_faq()
            blocks.append('<h2 id="faq">Frequently Asked Questions</h2>')
            toc.append(("Frequently Asked Questions", "faq"))
            in_faq = True
            pending_q = ""
            continue

        if in_faq:
            if style in ("Heading3", "Heading4") or plain.endswith("?"):
                if pending_q:
                    faq_buf.append((pending_q, ""))
                pending_q = plain
            elif pending_q:
                faq_buf.append((pending_q, text))
                pending_q = ""
            continue

        if is_list:
            list_buf.append(f"<li>{text}</li>")
            continue

        flush_list()
        saw_intro = True

        if style == "Heading3" and plain == "Key Takeaways":
            style = "Heading2"
            text = "Key Takeaways"

        if style == "Heading2" or (not style and plain == "Key Takeaways"):
            h2_counter += 1
            sid = _slugify(text)
            if sid in [t[1] for t in toc]:
                sid = f"{sid}-{h2_counter}"
            toc.append((plain, sid))
            blocks.append(f'<h2 id="{sid}">{text}</h2>')
        elif style in ("Heading3", "Heading4"):
            blocks.append(f"<h3>{text}</h3>")
        else:
            blocks.append(f"<p>{text}</p>")

    flush_list()
    if in_faq:
        flush_faq()

    body = "\n        ".join(blocks)
    body = re.sub(
        r"(<h[23](?:\s[^>]*)?>)(.*?)(</h[23]>)",
        lambda m: m.group(1) + re.sub(r"</?strong>", "", m.group(2)) + m.group(3),
        body,
        flags=re.DOTALL,
    )
    body = body.replace("&amp;amp;", "&amp;")
    return title, toc, body


def _toc_html(toc: list[tuple[str, str]]) -> str:
    if not toc:
        return ""
    items = "".join(f'<li><a href="#{_esc(sid)}">{_esc(label)}</a></li>' for label, sid in toc)
    return f"""<nav class="blog-toc" aria-label="Table of contents">
      <h2 class="blog-toc-title">Table of Contents</h2>
      <ol class="blog-toc-list">{items}</ol>
    </nav>"""


def _apply_links(body: str) -> str:
    replacements = [
        (
            "Cisco Certified Network Associate (CCNA)",
            '<a href="/ccna">Cisco Certified Network Associate (CCNA)</a>',
        ),
        ("CCNA Certification", '<a href="/ccna">CCNA Certification</a>'),
        ("CCNP Enterprise", '<a href="/courses/ccnp-enterprise">CCNP Enterprise</a>'),
        ("CCNP Security", '<a href="/courses/ccnp-security">CCNP Security</a>'),
        (
            "cisco certification training",
            '<a href="/ccna">Cisco certification training</a>',
        ),
        (
            "cisco training",
            '<a href="/ccna">Cisco training</a>',
        ),
    ]
    for src, dst in replacements:
        if src in body and f">{src}</a>" not in body and f">{src}<" not in body:
            body = body.replace(src, dst, 1)

    # Never leave anchors inside headings
    body = re.sub(
        r"(<h[23][^>]*>)(.*?)(</h[23]>)",
        lambda m: m.group(1) + re.sub(r"</?a[^>]*>", "", m.group(2)) + m.group(3),
        body,
        flags=re.DOTALL,
    )

    body = body.replace("United States job market", "global and Malaysian job market")
    body = body.replace("United States technology sector", "global technology sector")
    body = body.replace("US job market", "Malaysian and global job market")
    body = body.replace("in the U.S. IT sector", "in the IT sector")
    body = body.replace("across the United States", "across Malaysia and globally")
    body = body.replace("in the United States", "in Malaysia and globally")
    body = body.replace("Employers across the country", "Employers across the region")
    body = re.sub(
        r'<p>"([^"]+)"</p>\s*<p>([^<]{2,80})</p>',
        r'<blockquote class="blog-quote"><p>"\1"</p><cite>\2</cite></blockquote>',
        body,
    )
    return body


def patch_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    entry = (
        f"  <url><loc>{SITE}/blog/{SLUG}</loc>"
        f"<changefreq>monthly</changefreq><priority>0.7</priority></url>"
    )
    if SLUG not in text:
        anchor = f"  <url><loc>{SITE}/blog/aws-certification-roadmap</loc>"
        if anchor in text:
            text = text.replace(anchor, entry + "\n" + anchor, 1)
        else:
            text = text.replace("</urlset>", entry + "\n</urlset>", 1)
        path.write_text(text, encoding="utf-8", newline="\n")
        print("  patched sitemap.xml")


def patch_redirects() -> None:
    path = ROOT / "_redirects"
    text = path.read_text(encoding="utf-8")
    rules = [
        f"{VANITY_PATH} /blog/{SLUG} 301",
        f"{VANITY_PATH}/ /blog/{SLUG} 301",
        f"/blog/cisco-certification-path/ /blog/{SLUG} 301",
    ]
    changed = False
    existing = {line.split()[0] for line in text.splitlines() if line.strip() and not line.startswith("#")}
    for rule in rules:
        src = rule.split()[0]
        if src not in existing:
            text = text.rstrip() + f"\n{rule}"
            changed = True
    if changed:
        path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
        print("  patched _redirects")


def patch_blog_index() -> None:
    path = ROOT / "blog.html"
    text = path.read_text(encoding="utf-8")
    link = (
        f'      <a href="/blog/{SLUG}">Cisco Certification Path 2026: CCNA, CCNP &amp; CCIE Roadmap '
        f"<span>Networking · Jul 2026</span></a>\n"
    )
    if f'href="/blog/{SLUG}"' not in text.split("Latest posts", 1)[-1].split("Featured", 1)[0]:
        # Insert at top of latest posts after AWS or first post
        for marker in (
            '      <a href="/blog/aws-certification-roadmap">',
            '      <a href="/blog/top-data-science-training-institutes-malaysia">',
        ):
            if marker in text:
                text = text.replace(marker, link + marker, 1)
                break
    card = f"""      <a class="card" href="/blog/{SLUG}">
        <h3>Cisco Certification Path</h3>
        <p>Complete CCNA, CCNP and CCIE roadmap — levels, exams and career paths for 2026.</p>
        <span class="card-link">Read article →</span>
      </a>
"""
    card_marker = f'<a class="card" href="/blog/{SLUG}">'
    if card_marker not in text:
        for marker in (
            '      <a class="card" href="/blog/aws-certification-roadmap">',
            '      <a class="card" href="/blog/top-data-science-training-institutes-malaysia">',
        ):
            if marker in text:
                text = text.replace(marker, card + marker, 1)
                break
    path.write_text(text, encoding="utf-8", newline="\n")
    print("  patched blog.html")


def build_page() -> None:
    if not DOCX.is_file():
        raise SystemExit(f"Missing: {DOCX}")
    title, toc, body = docx_to_body(DOCX)
    body = _apply_links(body)
    toc_html = _toc_html(toc)
    body_html = "        " + body
    path = f"/blog/{SLUG}"
    nav = render_site_nav(variant="inner", current_path=path)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(META_TITLE)}</title>
<meta name="description" content="{_esc(META_DESC)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:title" content="{_esc(META_TITLE)}">
<meta property="og:description" content="{_esc(META_DESC)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/image/nexperts-logo.png">
<meta property="og:site_name" content="Nexperts Academy">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{_esc(META_TITLE)}">
<meta name="twitter:description" content="{_esc(META_DESC)}">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300;1,9..144,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site-nav-mobile.css">
{NAV_ASSET_TAGS}
<link rel="stylesheet" href="/css/blog.css">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f8fbff;--ink:#0f1b2d;--ink2:#2a3f5f;--ink3:#4b6284;--ink4:#7e97b8;--blue:#1d4ed8;--line:#d7e6fb;--line2:#bfd5f2}}
html{{scroll-behavior:smooth;background:var(--bg)}}
body{{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--ink);line-height:1.65;font-size:15px;padding-top:62px}}
.hero{{padding:48px 40px 48px;text-align:center;background:linear-gradient(180deg,#eef6ff,#f8fbff);border-bottom:1px solid var(--line)}}
.hero h1{{font-family:'Fraunces',serif;font-weight:300;font-size:clamp(2rem,4vw,2.8rem);margin-bottom:12px}}
.hero h1 em{{font-style:italic;color:var(--blue)}}
.hero p{{color:var(--ink2);max-width:720px;margin:0 auto}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:32px}}
.card{{display:block;padding:20px;background:#fff;border:1px solid var(--line);border-radius:12px;text-decoration:none;color:inherit;transition:transform .2s,box-shadow .2s}}
.card:hover{{transform:translateY(-3px);box-shadow:0 12px 32px rgba(29,78,216,.12)}}
.card h3{{font-size:.95rem;margin-bottom:8px;color:var(--ink)}}
.card p{{font-size:.82rem;color:var(--ink3);margin:0}}
.card-link{{display:inline-block;margin-top:12px;font-size:.78rem;font-weight:700;color:var(--blue)}}
.blog-faq{{margin-top:1.5rem}}
.faq-item{{margin-bottom:1.25rem;padding-bottom:1.25rem;border-bottom:1px solid var(--line)}}
.faq-q{{margin-bottom:.5rem;color:var(--ink)}}
footer{{background:#0d1117;color:rgba(255,255,255,.5);text-align:center;padding:32px 24px;font-size:.75rem}}
footer a{{color:rgba(255,255,255,.65);text-decoration:none}}
</style>
<link rel="stylesheet" href="/css/whatsapp-float.css">
</head>
<body class="blog-page">
{nav}
<section class="hero">
  <p style="font-size:.72rem;color:var(--ink3);margin-bottom:14px"><a href="/" style="color:inherit;text-decoration:none">Home</a> / <a href="/blog" style="color:inherit;text-decoration:none">Blog</a> / Cisco Certification Path</p>
  <h1>Cisco Certification Path<br><em>CCNA, CCNP &amp; CCIE explained</em></h1>
  <p>July 2026 · Nexperts Networking Practice</p>
</section>
<section class="content legal-prose">
  <a class="blog-back" href="/blog">← Back to Blog</a>
{toc_html}
{body_html}
    <div class="card-grid">
      <a class="card" href="/ccna">
        <h3>CCNA Training</h3>
        <p>Associate-level Cisco networking foundation with hands-on labs.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/courses/ccnp-enterprise">
        <h3>CCNP Enterprise</h3>
        <p>Professional-level enterprise networking after CCNA.</p>
        <span class="card-link">Learn more →</span>
      </a>
      <a class="card" href="/contact-us">
        <h3>Contact</h3>
        <p>Corporate training enquiry.</p>
        <span class="card-link">Learn more →</span>
      </a>
    </div>
  <p style="margin-top:2rem"><a href="/contact-us#enquire" style="color:var(--blue);font-weight:700">Enquire about Cisco certification training →</a></p>
</section>
<footer>
  <p>© Nexperts Academy Sdn Bhd · <a href="/">Home</a> · <a href="/blog">Blog</a> · <a href="/privacy-policy">Privacy</a></p>
</footer>
<script src="/js/site-nav-mobile.js" defer></script>
<a href="https://wa.me/601112216870" class="nx-wa-float" target="_blank" rel="noopener noreferrer" aria-label="Chat with Nexperts Academy on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.435 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
</a>
</body>
</html>
"""
    out = ROOT / "blog" / f"{SLUG}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {out} ({len(body)} chars) title={title!r}")


def main() -> None:
    build_page()
    patch_sitemap()
    patch_redirects()
    patch_blog_index()
    print("Done. Next: update site_nav + inject_addons_nav.py")


if __name__ == "__main__":
    main()
