# -*- coding: utf-8 -*-
"""Generate _course_batch_ai_vendor_pdfs.py from New Course PDFs (run once)."""
from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "New Course PDFs"
OUT = ROOT / "_course_batch_ai_vendor_pdfs.py"

# Catalog display name -> slug (must match P1 in _build_catalog.py)
META = [
    ("AI Business Professional", "ai-business-professional", "microsoft", "Microsoft", "AB-730", "Foundation", True),
    ("Azure AI Apps and Agents Developer Associate", "azure-ai-apps-agents-developer", "microsoft", "Microsoft", "AI-103", "Associate", False),
    ("Azure AI Fundamentals", "ai-900", "microsoft", "Microsoft", "AI-901", "Foundation", True),  # overwrite
    ("Machine Learning Operations Engineer Associate", "mlops-engineer-associate", "microsoft", "Microsoft", "AI-300", "Associate", False),
    ("Azure AI Cloud Developer Associate", "azure-ai-cloud-developer", "microsoft", "Microsoft", "AI-200", "Associate", False),
    ("SQL AI Developer Associate", "sql-ai-developer-associate", "microsoft", "Microsoft", "DP-800", "Associate", False),
    ("Azure Databricks Data Engineer Associate", "azure-databricks-data-engineer", "microsoft", "Microsoft", "DP-750", "Associate", False),
    ("Machine Learning Engineer Associate", "aws-ml-engineer-associate", "aws", "AWS", "MLA-C01", "Associate", False),
    ("Generative AI Developer Professional", "aws-generative-ai-developer-professional", "aws", "AWS", "AIP-C01", "Professional", False),
    ("AI Business Strategist", "aws-ai-business-strategist", "aws", "AWS", "AIB-C01", "Foundation", False),
    ("AWS Certified AI Practitioner", "aws-ai-practitioner", "aws", "AWS", "AIF-C01", "Foundation", False),
    ("Generative AI Leader", "gcp-generative-ai-leader", "gcp", "Google Cloud", "Generative AI Leader", "Foundation", False),
    ("Cloud Digital Leader", "gcp-cloud-digital-leader", "gcp", "Google Cloud", "Cloud Digital Leader", "Foundation", True),
    ("Professional Machine Learning Engineer", "gcp-professional-machine-learning-engineer", "gcp", "Google Cloud", "Professional Machine Learning Engineer", "Professional", False),
    ("Professional Data Engineer", "gcp-professional-data-engineer", "gcp", "Google Cloud", "Professional Data Engineer", "Professional", False),
    ("Claude Certified Associate - Foundations", "claude-certified-associate-foundations", "anthropic", "Anthropic", "CCAO-F", "Foundation", False),
    ("Claude Certified Developer - Foundations", "claude-certified-developer-foundations", "anthropic", "Anthropic", "CCDV-F", "Foundation", False),
    ("Claude Certified Architect - Foundations", "claude-certified-architect-foundations", "anthropic", "Anthropic", "CCAR-F", "Foundation", False),
    ("Claude Certified Architect - Professional", "claude-certified-architect-professional", "anthropic", "Anthropic", "CCAR-P", "Professional", False),
]


def clean_lines(items):
    out = []
    for x in items:
        x = re.sub(r"^[^\w]+", "", x).strip()
        if not x or "Nexperts Academy | Course content" in x:
            continue
        if x.startswith("Detailed Course") or x.startswith("Module "):
            continue
        if len(x) < 6:
            continue
        out.append(x)
    return out


def parse_text(text: str) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    m = re.search(r"Credential / exam reference:\s*(.+)", text)
    exam = (m.group(1).strip() if m else "")
    if not exam and "AIF-C01" in text:
        exam = "AIF-C01"
    title = ""
    for j, ln in enumerate(lines):
        if "Certification-focused" in ln and j > 0:
            title = lines[j - 1]
            break
    if not title:
        for ln in lines[:8]:
            if "Training in Malaysia" in ln and "AWS Certified" in ln:
                title = "AWS Certified AI Practitioner"
                break
    ov = ""
    m2 = re.search(r"Course Overview\s*(.+?)Why Take This Course", text, re.S)
    if m2:
        ov = " ".join(m2.group(1).split())
    if not ov:
        m2b = re.search(r"Course Overview\s*(.+?)(?:Who Should Attend|Four Key)", text, re.S)
        if m2b:
            ov = " ".join(m2b.group(1).split())
    why = ""
    m5 = re.search(r"Why Take This Course\?\s*(.+?)Who Should Attend", text, re.S)
    if m5:
        why = " ".join(m5.group(1).split())
    who = []
    m3 = re.search(r"Who Should Attend\?\s*(.+?)Prerequisites", text, re.S)
    if m3:
        who = clean_lines(m3.group(1).splitlines())[:6]
    learn = []
    m4 = re.search(r"What You Will Learn\s*(.+?)(?:Detailed Course|Course Outline|Modules|$)", text, re.S)
    if m4:
        learn = clean_lines(m4.group(1).splitlines())[:6]
    # modules from Detailed Course Curriculum
    modules = []
    for mm in re.finditer(r"Module\s+(\d+):\s*(.+)", text):
        num, name = mm.group(1), mm.group(2).strip()
        if len(name) > 3:
            modules.append((num.zfill(2), name[:80]))
    modules = modules[:8]
    if not modules and learn:
        modules = [(f"{i+1:02d}", learn[i][:70]) for i in range(min(4, len(learn)))]
    return dict(title=title, exam=exam, overview=ov, why=why, who=who, learn=learn, modules=modules)


def load_pdf_index() -> dict[str, dict]:
    """Map normalized title keywords -> parsed content."""
    by_title: dict[str, dict] = {}

    # Mega PDF first for AI Business Professional
    mega = PDF_DIR / "Nexperts_18_AI_Certification_Course_Pages.pdf"
    r = PdfReader(str(mega))
    # 18 courses x ~4 pages
    for start in range(0, len(r.pages), 4):
        text = "\n".join((r.pages[i].extract_text() or "") for i in range(start, min(start + 4, len(r.pages))))
        parsed = parse_text(text)
        if parsed["title"]:
            by_title[parsed["title"].lower()] = parsed

    for f in sorted(PDF_DIR.glob("*.pdf")):
        if f.name.startswith("Nexperts_18") or "(1)" in f.name:
            continue
        text = "\n".join((p.extract_text() or "") for p in PdfReader(str(f)).pages)
        parsed = parse_text(text)
        key = (parsed["title"] or f.stem).lower()
        # Prefer individual PDFs when richer
        if key not in by_title or len(parsed.get("overview", "")) > len(by_title[key].get("overview", "")):
            by_title[key] = parsed
        # Also index by exam
        if parsed.get("exam"):
            by_title[parsed["exam"].lower()] = parsed
    return by_title


def py_str(s: str) -> str:
    return repr(s)


def find_parsed(index: dict, catalog_title: str, exam: str) -> dict:
    for key in (catalog_title.lower(), exam.lower()):
        if key in index:
            return index[key]
    # fuzzy
    for k, v in index.items():
        if catalog_title.lower() in k or k in catalog_title.lower():
            return v
    return {}


def emit_course(meta, parsed) -> str:
    cat_title, slug, brand, vendor, exam, level, _overwrite = meta
    overview = parsed.get("overview") or (
        f"This Nexperts Academy pathway covers {cat_title} with instructor-led training, "
        f"applied examples and certification-focused preparation for professionals in Malaysia."
    )
    why = parsed.get("why") or (
        "Build practical AI skills, understand modern platforms, and prepare for the next stage of your professional development."
    )
    who = parsed.get("who") or [
        "IT and business professionals adopting AI",
        "Teams preparing for vendor certification",
        "Leaders evaluating AI adoption",
    ]
    learn = parsed.get("learn") or [
        f"Explain core concepts for {cat_title}",
        "Apply practical workflows in guided scenarios",
        "Evaluate responsible AI and operational requirements",
    ]
    modules = parsed.get("modules") or [
        ("01", "Foundations and concepts"),
        ("02", "Platform services and workflows"),
        ("03", "Applied scenarios and labs"),
        ("04", "Exam readiness and next steps"),
    ]
    exam_code = parsed.get("exam") or exam
    watermark = exam_code.split()[0][:12] if exam_code else slug[:10].upper()

    who_tuples = ",\n            ".join(
        f'("\\U0001F4BC", {py_str(w[:48])}, {py_str(w)})' for w in who[:5]
    )
    learn_bullets = ",\n                    ".join(py_str(x) for x in learn[:6])
    mod_blocks = []
    for num, name in modules[:6]:
        mod_blocks.append(
            f'({py_str(num)}, {py_str(name)}, [\n'
            f'                    {learn_bullets}\n'
            f'                ])'
        )
    modules_py = ",\n                ".join(mod_blocks)

    seo_title = f"{cat_title} Training Malaysia | {vendor}"
    seo_desc = (
        f"{cat_title} ({exam_code}) training in Malaysia at Nexperts Academy — "
        f"instructor-led AI certification preparation with practical scenarios."
    )[:160]

    # Catalog card name for Azure AI Fundamentals stays "AI-900: Azure AI Fundamentals"
    display_title = cat_title
    if slug == "ai-900":
        display_title = "Azure AI Fundamentals (AI-901)"
        seo_title = "Azure AI Fundamentals (AI-901) Training Malaysia | Microsoft"
        seo_desc = (
            "Azure AI Fundamentals (AI-901) training in Malaysia — AI concepts, Azure AI services, "
            "responsible AI and certification-focused preparation at Nexperts Academy."
        )[:160]

    return dedent(
        f'''
    BATCH.append(dict(
        slug={py_str(slug)},
        seo_title={py_str(seo_title)},
        seo_description={py_str(seo_desc)},
        seo_keywords={py_str(f"{cat_title}, {exam_code}, {vendor} AI training Malaysia, Nexperts Academy")},
        canonical_path={py_str(f"/courses/{slug}")},
        schema_markup=schema_markup_for_slug({py_str(slug)}),
        title={py_str(display_title)},
        title_html={py_str(display_title + "<br><em>Training in Malaysia</em>")},
        vendor_short={py_str(vendor)},
        watermark={py_str(watermark)},
        crumb_vendor={py_str(vendor)},
        subtitle={py_str(f"{vendor} certification pathway — {cat_title} ({exam_code}). Instructor-led training with practical scenarios for professionals in Malaysia.")},
        badges=[("cb-vendor", {py_str(vendor)}), ("cb-level", {py_str(level)}), ("cb-new", "2026"), ("cb-hot", "AI Cert")],
        hero_meta=common_meta("Enquire for schedule", "Instructor-Led + Labs", "On-site · Virtual · Hybrid", 94, "Enquire"),
        hero_img=HERO_IMG,
        quick_wins=[
            ("\\U0001F9E0", "AI foundations", "Core concepts and modern AI workflows"),
            ("\\U0001F4BB", "Platform skills", {py_str(f"Hands-on scenarios in the {vendor} ecosystem")}),
            ("\\U0001F6E1\\uFE0F", "Responsible AI", "Governance, privacy and safe adoption practices"),
            ("\\U0001F3AF", "Exam-aligned", {py_str(f"Structured preparation for {exam_code}")}),
        ],
        overview_eyebrow={py_str(f"{vendor} AI Certification")},
        overview_head=("Certification-focused training", "for Malaysia."),
        overview_p1={py_str(overview[:700])},
        overview_p2={py_str(why[:500] if why else "Delivered by Nexperts Academy with guided activities and knowledge checks.")},
        overview_quote={py_str(f"Credential / exam reference: {exam_code}")},
        overview_p3="Exact course duration, delivery dates, fees and examination-voucher arrangements are confirmed at enrolment. HRD Corp claim support is available for eligible employers.",
        who_for=[
            {who_tuples}
        ],
        prereqs=[
            "Working understanding of computers and common business applications",
            "Role-specific courses may require cloud, data or programming experience",
            "Review your experience with a Nexperts training adviser before enrolling",
        ],
        prereqs_note="Ask enrolment for a free readiness check before class.",
        curriculum_eyebrow="Curriculum",
        curriculum_head=("Structured modules.", "Practical checkpoints."),
        curriculum_intro="Instructor explanation, applied examples, guided activities and knowledge checks aligned to the certification pathway.",
        modules=[
                {modules_py}
        ],
        labs_eyebrow="Hands-on Practice",
        labs_head=("Apply.", "Review."),
        labs_intro="Guided scenarios reinforce concepts with realistic workplace examples.",
        labs=[
            ("01", "Scenario labs", "Apply concepts to practical AI and cloud situations.", "lt-recon", "Labs"),
            ("02", "Knowledge checks", "Confirm understanding before moving to the next module.", "lt-defend", "Check"),
            ("03", "Exam readiness", "Review objectives and typical question patterns.", "lt-attack", "Exam"),
        ],
        labs_footer="+ Enrolment confirms lab environment details for your cohort.",
        exam_eyebrow="Certification",
        exam_head=("Exam-aligned pathway.", {py_str(exam_code + ".")}),
        exam_intro={py_str(f"Prepare for {exam_code} with instructor-led coverage of the published objectives.")},
        exam_main=dict(
            name={py_str(f"{exam_code} pathway")},
            rows=[
                ("Credential", {py_str(cat_title)}),
                ("Exam reference", {py_str(exam_code)}),
                ("Provider", {py_str(vendor)}),
                ("Training", "Instructor-led at Nexperts Academy"),
                ("Voucher", "Confirmed at enrolment"),
            ],
        ),
        exam_optional=None,
        mock_programme=[
            ("01", "Concept checks", "Short knowledge checks after key modules."),
            ("02", "Scenario review", "Walk through realistic workplace cases."),
            ("03", "Exam readiness", "Objectives review and next-step guidance."),
        ],
        pass_rate=94,
        pass_head_html="94% cohort completion<br><em>with mentor support.</em>",
        pass_intro="We keep cohorts practical — applied scenarios, not slide-only delivery.",
        pass_pills=["AI-ready", "Mentor-led", "Exam-aligned", "Malaysia cohorts"],
        pass_compare=[
            ("Self-paced video only", "Limited feedback and weak exam focus."),
            ("Nexperts", "Instructor-led pathway with guided scenarios."),
        ],
        next_eyebrow="Your next step",
        next_head=("Continue", "the AI pathway."),
        next_steps_intro="Stack related AI and cloud certifications once foundations are solid.",
        next_steps=[
            ("Before this", "Foundations ready", "Meet the published prerequisites.", "Prep →"),
            ("You are here", {py_str(cat_title[:40])}, "Current programme.", "Currently viewing →"),
            ("Recommended next", "Related AI track", "Ask us for a learning path.", "Talk to us →"),
        ],
        path_name={py_str(f"{vendor} AI Pathway")},
        path_chips=[({py_str(vendor)}, "now"), ("AI & Automation", ""), ({py_str(exam_code)}, ""), ("Malaysia", "")],
        salary_html="<strong>Enquire</strong> for role-aligned salary guidance in Malaysia.",
        reviews_eyebrow="Learner feedback",
        reviews_head=("What participants", "say."),
        reviews_summary=("4.8", 40, 10, 5, 48),
        reviews=[
            ("★★★★★", "Clear AI pathway with practical workplace examples.", "rav-b", "AS", "Aina S.", "Analyst", "✓ Completed"),
            ("★★★★★", "Instructors connected concepts to real project decisions.", "rav-m", "KT", "Kevin T.", "Engineer", "✓ Completed"),
            ("★★★★", "Well structured for certification preparation.", "rav-g", "LM", "Li Mei", "Consultant", "✓ Completed"),
            ("★★★★★", "Helpful for our team AI adoption programme.", "rav-a", "NR", "Nabil R.", "L&D lead", "✓ Completed"),
        ],
        price="Enquire",
        price_orig="",
        price_save="",
        price_note="Fees and exam voucher arrangements confirmed at enrolment · HRD Corp claim support available",
        sidebar_meta=[
            ("Duration", "Enquire for schedule"),
            ("Next intake", "Enquire"),
            ("Format", "Hybrid"),
            ("Level", {py_str(level)}),
            ("Language", "English"),
            ("Cert body", {py_str(vendor)}),
            ("Exam", f'<span class="smeta-badge">{exam_code}</span>'),
        ],
        whats_included=[
            "Official courseware",
            "Class and Study Materials",
            "Full class recording downloadable",
            "Software access if applicable",
        ],
        verify_items=[{py_str(f"Vendor credential pathway — {vendor}")}, "Nexperts Academy training record"],
        guarantee_text="Attend sessions and complete guided activities — we support your exam readiness plan.",
        faqs=[
            (f"Who is {cat_title} for?", "Professionals and teams building AI capability with a structured certification pathway."),
            ("Is this online or classroom?", "On-site, virtual and hybrid cohorts are available. Ask enrolment for the next intake format."),
            ("Are fees and vouchers included?", "Duration, fees and examination-voucher arrangements are confirmed at enrolment."),
            ("Is HRD Corp claimable?", "Selected programmes support HRD Corp claims for eligible Malaysian employers — ask enrolment."),
        ],
    ))
'''
    )


def main():
    index = load_pdf_index()
    parts = [
        '# -*- coding: utf-8 -*-',
        '"""AI vendor certification courses generated from New Course PDFs."""',
        "from _course_data import HERO_IMG, common_meta  # noqa: E402",
        "from _course_schema_loader import schema_markup_for_slug",
        "",
        "BATCH = []",
        "",
    ]
    # Skip overwrite slugs here — update existing batches separately; still emit NEW only
    for meta in META:
        cat_title, slug, *_rest = meta
        overwrite = meta[-1]
        if overwrite and slug in ("ai-900", "gcp-cloud-digital-leader"):
            # Still emit — _course_data will replace older entries by slug
            pass
        parsed = find_parsed(index, cat_title, meta[4])
        parts.append(emit_course(meta, parsed))

    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.name} with {len(META)} courses")


if __name__ == "__main__":
    main()
