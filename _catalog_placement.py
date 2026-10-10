# -*- coding: utf-8 -*-
"""Catalog placement rules: multi-cat + Skill Vendor / Non-Vendor remap.

Card tuple formats supported:
  10-tuple: (brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled)
  11-tuple: same + extra_cats (tuple/list of additional cat keys)

After apply_placements(), every card is normalized to 11-tuple with:
  brand, primary_cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats
where cats is a sorted tuple of all category keys.
"""
from __future__ import annotations

# Name -> (brand_key, vendor_label, cats_tuple, badge_label|None)
# badge_label None keeps existing badge.
SKILL_REMAP: dict[str, tuple[str, str, tuple[str, ...], str | None]] = {
    # Non-AI vendor skills
    "Excel Advanced Analytics": ("microsoft", "Microsoft", ("skill",), "Skills"),
    "Microsoft Excel 2019 Basic": ("microsoft", "Microsoft", ("skill",), "Skills"),
    "Salesforce Admin & Automation": ("salesforce", "Salesforce", ("skill",), "Skills"),
    "ServiceNow Administration Fundamentals": ("servicenow", "ServiceNow", ("skill",), "Skills"),
    "ServiceNow Platform Implementation": ("servicenow", "ServiceNow", ("skill",), "Skills"),
    "Tableau for Beginners": ("tableau", "Tableau", ("skill",), "Skills"),
    "Data Analytics & Visualisation with Tableau": ("tableau", "Tableau", ("skill",), "Skills"),
    "Advanced Data Visualization Using Tableau": ("tableau", "Tableau", ("skill",), "Skills"),
    "Oracle PL/SQL Database Programming Course": ("oracle", "Oracle", ("skill",), "Skills"),
    # AI vendor / tool skills
    "Microsoft Copilot": ("microsoft", "Microsoft", ("skill", "ai"), "AI 2026"),
    "Microsoft Copilot Masterclass": ("microsoft", "Microsoft", ("skill", "ai"), "AI 2026"),
    # Claude Masterclass = practical tool skill, no Anthropic exam → Non-Vendor
    "Claude AI in 90 Minutes Productivity Course: Build Your AI Work Assistant": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Claude AI Masterclass": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "ChatGPT Masterclass": ("openai", "OpenAI", ("skill", "ai"), "AI 2026"),
    # Non-vendor non-AI
    "Docker & Containers": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "CI/CD with Jenkins & GitLab": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Python Bootcamp Certification Training": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Data Science with Python Certification": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Linux Administration": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "SQL for Data Professionals": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "SQL for Data Analytics": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Python for Data Analytics": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Certified Java Programming": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Full Stack Web Development": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Digital Marketing Certification": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Cyber Security Bootcamp": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Android Development": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Django Web Development": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "iOS Development": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Netflix Data Analysis Workshop": ("nonvendor", "Non-Vendor", ("skill",), "Workshop"),
    "Data Science Foundation": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    "Data Visualization with Seaborn Using Python": ("nonvendor", "Non-Vendor", ("skill",), "Skills"),
    # Non-vendor AI
    "AI & Machine Learning Bootcamp": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Machine Learning with Python": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Generative AI for Workplace Productivity & Business Automation": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Agentic AI": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Agentic AI Engineering": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Building a Chatbot Using Python": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Building AI Chatbots with Python": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Deep Learning Using PyTorch": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Generative AI Applications and Python Fundamentals": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Build Generative AI Applications with LLMs": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Prompt Engineering Certification Course with LLM": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Prompt Engineering Masterclass": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "AI Workflow Automation (No-Code)": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "AI-Powered Workflow Automation": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "AI Fundamentals": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "AI-Powered Data Analytics": ("nonvendor", "Non-Vendor", ("skill", "ai"), "AI 2026"),
    "Artificial Intelligence (AI) Course Malaysia": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
    "Artificial Intelligence & Machine Learning Course Malaysia": (
        "nonvendor",
        "Non-Vendor",
        ("skill", "ai"),
        "AI 2026",
    ),
}

# Existing vendor certs that are AI-related → also ai + skill (keep primary cat)
AI_VENDOR_CERT_EXTRA: dict[str, tuple[str, ...]] = {
    "AI-900: Azure AI Fundamentals": ("ai", "skill"),
    "DP-100: Azure Data Scientist": ("ai", "skill"),
    "AI-102: Azure AI Engineer": ("ai", "skill"),
    "AWS Machine Learning Specialty": ("ai", "skill"),
    "CompTIA SecAI+": ("ai", "skill"),
    "CPENT AI": ("ai", "skill"),
    "Cloud Digital Leader": ("ai", "skill"),
}


def unpack_card(c):
    brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled = c[:10]
    extras = ()
    if len(c) >= 11 and c[10]:
        extras = tuple(c[10]) if not isinstance(c[10], str) else (c[10],)
    cats = tuple(dict.fromkeys((cat,) + extras))
    return brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats


def apply_placements(cards: list) -> list:
    out = []
    for c in cards:
        brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats = unpack_card(c)

        if name in SKILL_REMAP:
            brand, vendor, cats, new_badge = SKILL_REMAP[name]
            if new_badge:
                badge = new_badge
            cat = cats[0]
        elif name in AI_VENDOR_CERT_EXTRA:
            extra = AI_VENDOR_CERT_EXTRA[name]
            cats = tuple(dict.fromkeys(cats + extra))
            cat = cats[0] if cat not in cats else cat
            # keep primary as first of original primary if still present
            if "cert" in cats:
                cat = "cert"
            elif "spec" in cats:
                cat = "spec"
            else:
                cat = cats[0]

        out.append(
            (brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats)
        )
    return out


def card_matches_cat(cats: tuple[str, ...], filter_cat: str) -> bool:
    if filter_cat == "all":
        return True
    return filter_cat in cats
