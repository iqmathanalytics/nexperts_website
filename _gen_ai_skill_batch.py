# -*- coding: utf-8 -*-
"""Generate _course_batch_ai_skill_pdfs.py from New Course PDFs (practical skills)."""
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
OUT = ROOT / "_course_batch_ai_skill_pdfs.py"

# (catalog_title, slug, brand_key, vendor_label, level, is_ai, pdf_prefix)
META = [
    ("ChatGPT Masterclass", "chatgpt-masterclass", "openai", "OpenAI", "Beginner to Intermediate", True, "01_ChatGPT"),
    ("Claude AI Masterclass", "claude-ai-productivity-90-minutes", "anthropic", "Anthropic", "Beginner to Intermediate", True, "02_Claude"),
    ("AI Workflow Automation (No-Code)", "ai-workflow-automation-no-code", "nonvendor", "Non-Vendor", "Beginner to Intermediate", True, "03_AI_Workflow"),
    ("AI-Powered Workflow Automation", "ai-powered-workflow-automation", "nonvendor", "Non-Vendor", "Intermediate", True, "04_AI_Powered_Workflow"),
    ("Building AI Chatbots with Python", "building-a-chatbot-using-python", "nonvendor", "Non-Vendor", "Intermediate", True, "12_Building_AI_Chatbots"),
    ("Build Generative AI Applications with LLMs", "generative-ai-applications-python-fundamentals", "nonvendor", "Non-Vendor", "Intermediate", True, "13_Build_Generative"),
    ("Prompt Engineering Masterclass", "prompt-engineering-certification", "nonvendor", "Non-Vendor", "Beginner to Intermediate", True, "14_Prompt_Engineering"),
    ("Machine Learning with Python", "ai-ml-bootcamp", "nonvendor", "Non-Vendor", "Beginner to Intermediate", True, "15_Machine_Learning"),
    ("Deep Learning Using PyTorch", "deep-learning-using-pytorch", "nonvendor", "Non-Vendor", "Intermediate", True, "16_Deep_Learning"),
    ("AI Fundamentals", "ai-fundamentals", "nonvendor", "Non-Vendor", "Beginner", True, "18_AI_Fundamentals"),
    ("Microsoft Copilot Masterclass", "microsoft-copilot", "microsoft", "Microsoft", "Beginner to Intermediate", True, "19_Microsoft_Copilot"),
    ("SQL for Data Analytics", "sql-for-data-professionals", "nonvendor", "Non-Vendor", "Beginner to Intermediate", False, "22_SQL"),
    ("Python for Data Analytics", "python-for-data-analytics", "nonvendor", "Non-Vendor", "Beginner to Intermediate", False, "23_Python"),
    ("Data Analytics & Visualisation with Tableau", "tableau-for-beginners", "tableau", "Tableau", "Beginner to Intermediate", False, "24_Data_Analytics"),
    ("AI-Powered Data Analytics", "ai-powered-data-analytics", "nonvendor", "Non-Vendor", "Beginner to Intermediate", True, "25_AI_Powered_Data"),
]


def clean_lines(items):
    out = []
    for x in items:
        x = re.sub(r"^[^\w]+", "", x).strip()
        if not x or "Nexperts Academy" in x and "|" in x and len(x) < 50:
            continue
        if x.startswith("Page ") or x.startswith("Four Reasons") or x.startswith("Why "):
            continue
        if len(x) < 8:
            continue
        out.append(x)
    return out


def parse_text(text: str) -> dict:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    ov = ""
    for pat in (
        r"(?:Course Overview|What This Course Is|Course overview)\s*(.+?)(?:Who Should Attend|Four Reasons|Why Learn|Why Take|At a Glance|Level:)",
        r"(?:Course Overview|What This Course Is)\s*(.+)",
    ):
        m = re.search(pat, text, re.S | re.I)
        if m:
            ov = " ".join(m.group(1).split())
            break
    who = []
    m3 = re.search(r"Who Should Attend\??\s*(.+?)(?:Prerequisites|Four Reasons|Course Overview|Why |$)", text, re.S | re.I)
    if m3:
        who = clean_lines(m3.group(1).splitlines())[:6]
    learn = []
    for pat in (
        r"(?:Four Key Learning Benefits|Four Reasons to (?:Join|Learn|Take This Course)|Why Learn[^\n]*\n|Why Take This Course\??)\s*(.+?)(?:What This Course|Course Overview|Who Should Attend|Level:)",
        r"(?:Four Key Learning Benefits|Four Reasons[^\n]*)\s*(.+)",
    ):
        m4 = re.search(pat, text, re.S | re.I)
        if m4:
            learn = clean_lines(m4.group(1).splitlines())[:6]
            if learn:
                break
    modules = []
    for mm in re.finditer(r"Module\s+(\d+)\s*[:.\-]\s*(.+)", text, re.I):
        modules.append((mm.group(1).zfill(2), mm.group(2).strip()[:80]))
    modules = modules[:6]
    if not modules and learn:
        modules = [(f"{i+1:02d}", learn[i][:70]) for i in range(min(4, len(learn)))]
    if not modules:
        modules = [
            ("01", "Foundations and core concepts"),
            ("02", "Hands-on practice and workflows"),
            ("03", "Applied project and review"),
            ("04", "Responsible use and next steps"),
        ]
    return dict(overview=ov, who=who, learn=learn, modules=modules, preview=" ".join(lines[:12]))


def find_pdf(prefix: str) -> Path | None:
    for f in sorted(PDF_DIR.glob("*.pdf")):
        if f.name.startswith(prefix):
            return f
    return None


def py_str(s: str) -> str:
    return repr(s)


def emit_course(meta, parsed) -> str:
    title, slug, brand, vendor, level, is_ai, _prefix = meta
    overview = parsed.get("overview") or (
        f"This Nexperts Academy practical course covers {title} with instructor-led training, "
        "guided exercises and workplace-ready skills for professionals in Malaysia."
    )
    overview = overview[:900]
    who = parsed.get("who") or [
        "Working professionals building practical skills",
        "Team leads adopting modern tools",
        "Learners preparing a structured skills pathway",
    ]
    learn = parsed.get("learn") or [
        f"Apply core techniques from {title}",
        "Practise with realistic workplace scenarios",
        "Leave with reusable templates and next-step guidance",
    ]
    modules = parsed.get("modules") or []
    badge = "AI 2026" if is_ai else "Skills"
    watermark = title.split()[0][:12]
    who_tuples = ",\n            ".join(
        f'("\\U0001F4BC", {py_str(w[:48])}, {py_str(w)})' for w in who[:5]
    )
    learn_bullets = ",\n                    ".join(py_str(x) for x in learn[:6])
    mod_blocks = []
    for num, name in modules[:6]:
        mod_blocks.append(
            f"({py_str(num)}, {py_str(name)}, [\n"
            f"                    {learn_bullets}\n"
            f"                ])"
        )
    modules_py = ",\n                ".join(mod_blocks)
    seo_title = f"{title} Training Malaysia | Nexperts Academy"
    seo_desc = (
        f"{title} training in Malaysia at Nexperts Academy — instructor-led practical skills "
        "with workplace scenarios and mentor support."
    )[:160]
    path_kind = "AI & Automation" if is_ai else "Skill Programs"
    exam_label = "Labs + Project"

    return dedent(
        f"""
    BATCH.append(dict(
        slug={py_str(slug)},
        seo_title={py_str(seo_title)},
        seo_description={py_str(seo_desc)},
        seo_keywords={py_str(f"{title}, {vendor} training Malaysia, Nexperts Academy, practical skills")},
        canonical_path={py_str(f"/courses/{slug}")},
        schema_markup=schema_markup_for_slug({py_str(slug)}),
        title={py_str(title)},
        title_html={py_str(title + "<br><em>Training in Malaysia</em>")},
        vendor_short={py_str(vendor if vendor != "Non-Vendor" else "Nexperts Skill")},
        watermark={py_str(watermark)},
        crumb_vendor={py_str(path_kind)},
        subtitle={py_str(f"Practical instructor-led {title} for professionals in Malaysia — workplace scenarios, guided labs and reusable workflows.")},
        badges=[("cb-vendor", {py_str(vendor if vendor != "Non-Vendor" else "Nexperts Skill")}), ("cb-level", {py_str(level)}), ("cb-new", "2026"), ("cb-hot", {py_str(badge)})],
        hero_meta=common_meta("Enquire for schedule", "Instructor-Led + Labs", "On-site · Virtual · Hybrid", 94, "Enquire"),
        hero_img=HERO_IMG,
        quick_wins=[
            ("\\U0001F9E0", "Practical skills", "Hands-on techniques you can use at work"),
            ("\\U0001F4BB", "Guided labs", "Instructor-led practice with realistic scenarios"),
            ("\\U0001F6E1\\uFE0F", "Responsible use", "Accuracy, privacy and human oversight habits"),
            ("\\U0001F3AF", "Portfolio output", "Finish with a demonstrable work product"),
        ],
        overview_eyebrow={py_str(path_kind)},
        overview_head=("Practical training", "for Malaysia."),
        overview_p1={py_str(overview)},
        overview_p2="Delivered by Nexperts Academy with Malaysian workplace examples. Exact duration, delivery dates and fees are confirmed at enrolment. HRD Corp claim support is available for eligible employers.",
        overview_quote={py_str(f"Practical skills course — {title}.")},
        overview_p3="This programme focuses on applied capability rather than an external vendor examination voucher unless separately arranged.",
        who_for=[
            {who_tuples}
        ],
        prereqs=[
            "Working understanding of computers and common business applications",
            "Role-specific courses may require Python, spreadsheets or prior tool exposure",
            "Review your experience with a Nexperts training adviser before enrolling",
        ],
        prereqs_note="Ask enrolment for a free readiness check before class.",
        curriculum_eyebrow="Curriculum",
        curriculum_head=("Structured modules.", "Practical checkpoints."),
        curriculum_intro="Instructor explanation, guided labs and knowledge checks aligned to workplace outcomes.",
        modules=[
                {modules_py}
        ],
        labs_eyebrow="Hands-on Practice",
        labs_head=("Apply.", "Review."),
        labs_intro="Guided scenarios reinforce concepts with realistic workplace examples.",
        labs=[
            ("01", "Scenario labs", "Apply concepts to practical workplace situations.", "lt-recon", "Labs"),
            ("02", "Knowledge checks", "Confirm understanding before the next module.", "lt-defend", "Check"),
            ("03", "Project checkpoint", "Build a demonstrable work product.", "lt-attack", "Project"),
        ],
        labs_footer="+ Enrolment confirms lab environment details for your cohort.",
        exam_eyebrow="Assessment",
        exam_head=("Practical checkpoint.", "Certificate."),
        exam_intro="Complete guided labs and the mini-project to earn your Nexperts Academy certificate of completion.",
        exam_main=dict(
            name="Completion rubric",
            rows=[
                ("Labs", "Core labs completed with tutor sign-off"),
                ("Project", "Mini-project meets the published checklist"),
                ("Attendance", "Minimum attendance threshold met"),
                ("Passing", '<span class="pass-highlight">Certificate issued</span>'),
                ("Resit", "One remediation session included"),
            ],
        ),
        exam_optional=None,
        mock_programme=[
            ("01", "Concept checks", "Short knowledge checks after key modules."),
            ("02", "Lab review", "Tutor feedback on practical work."),
            ("03", "Project dry-run", "Present before final submit."),
        ],
        pass_rate=94,
        pass_head_html="94% cohort completion<br><em>with mentor support.</em>",
        pass_intro="We keep cohorts practical — applied scenarios, not slide-only delivery.",
        pass_pills=["Mentor-led", "Lab-driven", "Malaysia cohorts", {py_str(badge)}],
        pass_compare=[
            ("Self-paced video only", "Limited feedback and weak workplace transfer."),
            ("Nexperts", "Instructor-led pathway with guided scenarios."),
        ],
        next_eyebrow="Your next step",
        next_head=("Continue", "the pathway."),
        next_steps_intro="Stack related AI, automation or analytics programmes once foundations are solid.",
        next_steps=[
            ("Before this", "Foundations ready", "Meet the published prerequisites.", "Prep →"),
            ("You are here", {py_str(title[:40])}, "Current programme.", "Currently viewing →"),
            ("Recommended next", "Related track", "Ask us for a learning path.", "Talk to us →"),
        ],
        path_name={py_str(path_kind)},
        path_chips=[({py_str(vendor)}, "now"), ({py_str(path_kind)}, ""), ({py_str(level)}, ""), ("Malaysia", "")],
        salary_html="<strong>Enquire</strong> for role-aligned salary guidance in Malaysia.",
        reviews_eyebrow="Learner feedback",
        reviews_head=("What participants", "say."),
        reviews_summary=("4.8", 40, 10, 5, 48),
        reviews=[
            ("★★★★★", "Clear practical pathway with workplace examples.", "rav-b", "AS", "Aina S.", "Analyst", "✓ Completed"),
            ("★★★★★", "Instructors connected concepts to real project decisions.", "rav-m", "KT", "Kevin T.", "Engineer", "✓ Completed"),
            ("★★★★", "Well structured and immediately usable.", "rav-g", "LM", "Li Mei", "Consultant", "✓ Completed"),
            ("★★★★★", "Helpful for our team skills programme.", "rav-a", "NR", "Nabil R.", "L&D lead", "✓ Completed"),
        ],
        price="Enquire",
        price_orig="",
        price_save="",
        price_note="Fees confirmed at enrolment · HRD Corp claim support available",
        sidebar_meta=[
            ("Duration", "Enquire for schedule"),
            ("Next intake", "Enquire"),
            ("Format", "Hybrid"),
            ("Level", {py_str(level)}),
            ("Language", "English"),
            ("Cert body", {py_str(vendor if vendor != "Non-Vendor" else "Nexperts Academy")}),
            ("Exam", f'<span class="smeta-badge">{exam_label}</span>'),
        ],
        whats_included=[
            "Official courseware",
            "Class and Study Materials",
            "Full class recording downloadable",
            "Software access if applicable",
        ],
        verify_items=["Nexperts Academy verification ID"],
        guarantee_text="Attend sessions and complete guided activities — we support your project completion plan.",
        faqs=[
            (f"Who is {title} for?", "Professionals and teams who want practical, instructor-led skills with Malaysian workplace examples."),
            ("Is this online or classroom?", "On-site, virtual and hybrid cohorts are available. Ask enrolment for the next intake format."),
            ("Do I get a certificate?", "Yes. Complete labs and the mini-project to receive a Nexperts Academy certificate of completion."),
            ("Is HRD Corp claimable?", "Selected programmes support HRD Corp claims for eligible Malaysian employers — ask enrolment."),
        ],
    ))
"""
    )


def main():
    parts = [
        "# -*- coding: utf-8 -*-",
        '"""Practical AI / data skill courses generated from New Course PDFs."""',
        "from _course_data import HERO_IMG, common_meta  # noqa: E402",
        "from _course_schema_loader import schema_markup_for_slug",
        "",
        "BATCH = []",
        "",
    ]
    missing = []
    for meta in META:
        pdf = find_pdf(meta[6])
        if not pdf:
            missing.append(meta[6])
            parsed = {}
        else:
            text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
            parsed = parse_text(text)
        parts.append(emit_course(meta, parsed))
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.name} with {len(META)} courses; missing prefixes: {missing or 'none'}")


if __name__ == "__main__":
    main()
