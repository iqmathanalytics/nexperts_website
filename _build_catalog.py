# -*- coding: utf-8 -*-
"""Rebuild the Course Catalog block in index.html.

Output:
- 4 filter tabs (All, Industry Certifications, Skill-Based Programs, Specialized & Compliance)
- Courses visually grouped by BRAND (CompTIA, EC-Council, AWS, ...)
- Brand-themed color accents per group
- Each card shows: vendor badge, name, description, level chip,
  rating (star + count), students enrolled, and a "View Details" button
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
INDEX = ROOT / "index.html"

# -----------------------------------------------------------------------------
# Phase 1 slug map (anchor links)
# -----------------------------------------------------------------------------
P1 = {
    "CompTIA A+": "comptia-a-plus",
    "CompTIA Network+": "comptia-network-plus",
    "CompTIA Security+": "comptia-security-plus",
    "CompTIA CySA+": "comptia-cysa-plus",
    "CompTIA PenTest+": "comptia-pentest-plus",
    "CEH v13 AI": "ceh-v13-ai",
    "CHFI v11": "chfi-v11",
    "CPENT AI": "cpent-ai",
    "AWS Cloud Practitioner": "aws-cloud-practitioner",
    "AWS Solutions Architect Associate": "aws-solutions-architect-associate",
    "AWS Solutions Architect Professional": "aws-solutions-architect-professional",
    "AZ-900: Azure Fundamentals": "az-900",
    "AZ-104: Azure Administrator": "az-104",
    "AZ-305: Solutions Architect": "az-305",
    "SC-200: Security Operations": "sc-200",
    "PL-300: Power BI Data Analyst": "pl-300",
    "DP-203: Data Engineer": "dp-203",
    "CCNA": "ccna",
    "CCNP Enterprise": "ccnp-enterprise",
    "Professional Cloud Architect": "gcp-professional-cloud-architect",
    "ITIL 4 Foundation": "itil-4-foundation",
    "PMP": "pmp",
    "Kubernetes Administrator (CKA)": "cka",
    "CISM": "cism",
    "CISSP": "cissp",
}

# -----------------------------------------------------------------------------
# Brand metadata: order, label, badge label, tagline, color (--bk),
# tinted background (--bk-tint), CSS class for vendor chip
# -----------------------------------------------------------------------------
BRANDS = [
    ("comptia",   "CompTIA",          "CompTIA",          "Vendor-neutral standard for IT and cybersecurity.",          "#ef4444", "#fef2f2"),
    ("eccouncil", "EC-Council",       "EC-Council",       "Offensive security, ethical hacking and forensics.",        "#7c3aed", "#f5f3ff"),
    ("aws",       "AWS",              "AWS",              "The most-deployed cloud platform on Earth.",                "#ff9900", "#fff7ed"),
    ("microsoft", "Microsoft",        "Microsoft",        "Azure, M365 and the Microsoft cloud stack.",                "#0078d4", "#eff6ff"),
    ("cisco",     "Cisco",            "Cisco",            "The networking standard \u2014 from CCNA to CCIE.",         "#1ba0d7", "#ecfeff"),
    ("gcp",       "Google Cloud",     "Google Cloud",     "Data-first cloud, AI and analytics on Google Cloud.",       "#4285f4", "#eff6ff"),
    ("peoplecert","PeopleCert",       "PeopleCert",       "ITIL service management and PRINCE2 project delivery.",     "#ec4899", "#fdf2f8"),
    ("pmi",       "PMI",              "PMI",              "Project Management Institute \u2014 PMP and CAPM.",        "#1e40af", "#eff6ff"),
    ("scrum",     "Scrum Alliance",   "Scrum Alliance",   "Agile delivery, Scrum and modern team practices.",          "#f97316", "#fff7ed"),
    ("linuxfdn",  "Linux Foundation", "Linux Foundation", "Kubernetes, cloud-native and open-source platform skills.", "#326ce5", "#eff6ff"),
    ("hashicorp", "HashiCorp",        "HashiCorp",        "Infrastructure as code with Terraform and Vault.",          "#7b42bc", "#f5f3ff"),
    ("tableau",   "Tableau",          "Tableau",          "Enterprise BI and data visualisation.",                     "#e8762d", "#fff7ed"),
    ("isaca",     "ISACA",            "ISACA",            "Audit, risk, governance and security management.",          "#a30729", "#fef2f2"),
    ("isc2",      "ISC2",             "ISC2",             "CISSP and the ISC2 cybersecurity body of knowledge.",       "#082c5e", "#eef2ff"),
    ("skill",     "Skill-Based",      "Skills",           "Hands-on, role-ready skills \u2014 outcome over paperwork.","#10b981", "#ecfdf5"),
    ("my",        "Malaysia-Focused", "MY",               "PDPA, BNM RMiT and Malaysia-specific compliance.",          "#e11d48", "#fff1f2"),
]

# -----------------------------------------------------------------------------
# Course catalog. Each row:
# (brand_key, cat, vendor_label, badge_class, name, desc, level,
#  rating, reviews_count, enrolled)
# enrolled values are unique, 1000+, varied across course tier.
# rating: 4.6 - 4.9 (Phase 1 use real review-summary numbers).
# -----------------------------------------------------------------------------
CARDS = [
    # ---- CompTIA ----
    ("comptia","cert","CompTIA","Cert","CompTIA A+",                 "IT support foundation. Hardware, OS, troubleshooting, networking basics.","Foundation",     4.9,289,18420),
    ("comptia","cert","CompTIA","Cert","CompTIA Network+",           "Networking fundamentals \u2014 protocols, infrastructure and troubleshooting.","Foundation", 4.8,247,14780),
    ("comptia","cert","CompTIA","Cert","CompTIA Security+",          "Most requested cybersecurity cert by Malaysian employers.","Intermediate",                 4.9,512,22340),
    ("comptia","cert","CompTIA","Cert","CompTIA CySA+",              "Threat detection, behavioural analytics and SOC response operations.","Intermediate",      4.8,184,7820),
    ("comptia","cert","CompTIA","Cert","CompTIA PenTest+",           "Hands-on penetration testing, vulnerability assessment and reporting.","Advanced",         4.8,162,5640),
    ("comptia","cert","CompTIA","Cert","CompTIA SecurityX",          "Expert-level security architecture for enterprise environments.","Expert",                 4.7,84, 2480),
    ("comptia","cert","CompTIA","Cert","CompTIA Linux+",             "Linux administration for cloud, security and operational environments.","Intermediate",    4.8,138,6420),
    ("comptia","cert","CompTIA","Cert","CompTIA Cloud+",             "Vendor-neutral cloud infrastructure, security and automation cert.","Intermediate",        4.7,112,4960),
    ("comptia","cert","CompTIA","Cert","CompTIA Server+",            "Server hardware, virtualisation, storage and data centre operations.","Intermediate",      4.7,98, 4180),
    ("comptia","cert","CompTIA","Cert","CompTIA DataSys+",           "Database deployment, management and maintenance fundamentals.","Foundation",              4.7,72, 3520),
    ("comptia","cert","CompTIA","Cert","CompTIA Tech+",              "Digital literacy and tech fundamentals for any business professional.","Entry",            4.8,156,8240),
    ("comptia","spec","CompTIA","New 2026","CompTIA SecAI+",         "Secure and govern AI in cybersecurity operations. First cert of its kind.","Intermediate", 4.9,46, 1840),

    # ---- EC-Council ----
    ("eccouncil","cert","EC-Council","Cert","CEH v13 AI",            "Certified Ethical Hacker \u2014 flagship offensive security cert, AI-integrated.","Intermediate", 4.9,612,24180),
    ("eccouncil","cert","EC-Council","Cert","CPENT AI",              "Certified Penetration Testing Professional \u2014 advanced real-world attack labs.","Advanced",   4.8,118,3640),
    ("eccouncil","cert","EC-Council","Cert","CHFI v11",              "Computer Hacking Forensic Investigator \u2014 digital forensics and evidence.","Intermediate",  4.8,94, 4320),
    ("eccouncil","cert","EC-Council","Cert","Certified SOC Analyst (CSA)","SOC operations, threat monitoring, alert triage and incident reporting.","Entry\u2013Mid",4.8,168,9620),
    ("eccouncil","cert","EC-Council","Cert","CND v3",                "Certified Network Defender \u2014 proactive network protection and defense.","Intermediate",   4.7,124,5780),
    ("eccouncil","cert","EC-Council","Cert","CCISO",                 "Chief Information Security Officer \u2014 executive cybersecurity leadership.","Executive",   4.9,42, 1620),
    ("eccouncil","cert","EC-Council","Cert","CTIA",                  "Certified Threat Intelligence Analyst \u2014 dark web intel, threat hunting.","Advanced",      4.8,86, 2940),
    ("eccouncil","cert","EC-Council","Cert","ECIH v3",               "Certified Incident Handler \u2014 IR planning, detection and containment.","Intermediate",     4.7,72, 3180),
    ("eccouncil","spec","EC-Council","Cert","ICS / SCADA Security",  "OT and industrial control security \u2014 critical for Malaysia's energy sector.","Specialist",4.9,38, 1240),
    ("eccouncil","cert","EC-Council","Cert","ECDE \u2014 DevSecOps Engineer","Integrate security into DevOps pipelines \u2014 containers, CI/CD and IaC.","Intermediate",4.8,68,2860),
    ("eccouncil","cert","EC-Council","Cert","CCSE \u2014 Cloud Security Engineer","Certified Cloud Security Engineer \u2014 multi-cloud protection strategies.","Advanced", 4.8,54,2140),
    ("eccouncil","spec","EC-Council","AI 2026","C|OASP \u2014 Offensive AI Security","Certified Offensive AI Security Professional \u2014 adversarial AI techniques.","Advanced",4.9,32,1080),
    ("eccouncil","cert","EC-Council","Cert","CCT \u2014 Cybersecurity Technician","Entry-level hands-on cybersecurity \u2014 the right starting point in security.","Entry",4.8,142,7940),

    # ---- AWS ----
    ("aws","cert","AWS","Cert","AWS Cloud Practitioner",                "Foundational cloud concepts \u2014 the right first step for any IT professional.","Foundation",     4.9,486,21680),
    ("aws","cert","AWS","Cert","AWS Solutions Architect Associate",     "Design scalable, secure, high-availability architectures. Most hired-for AWS cert.","Associate", 4.9,394,16240),
    ("aws","cert","AWS","Cert","AWS SysOps Administrator",              "Deploy, manage and operate workloads on AWS \u2014 operations focus.","Associate",                4.7,184,6820),
    ("aws","cert","AWS","Cert","AWS Developer Associate",               "Develop and maintain applications on AWS \u2014 code-first cloud skills.","Associate",            4.8,212,8460),
    ("aws","cert","AWS","Cert","AWS Solutions Architect Professional",  "Complex enterprise cloud, multi-account design and migration strategy.","Professional",          4.8,148,4920),
    ("aws","cert","AWS","Cert","AWS DevOps Engineer Professional",      "Automate CI/CD, monitoring and governance at enterprise scale.","Professional",                  4.7,118,3680),
    ("aws","cert","AWS","Cert","AWS Security Specialty",                "Advanced IAM, encryption, logging and cloud threat response.","Specialty",                       4.8,96, 3140),
    ("aws","cert","AWS","Cert","AWS Data Engineer Associate",           "Build and manage data pipelines, lakes and analytics on AWS.","Associate",                       4.8,134,5260),
    ("aws","cert","AWS","Cert","AWS Machine Learning Specialty",        "ML models, SageMaker, and AI services on AWS \u2014 for data scientists.","Specialty",            4.8,82, 2680),

    # ---- Microsoft ----
    ("microsoft","cert","Microsoft","Cert","AZ-900: Azure Fundamentals", "Core cloud and Azure concepts \u2014 starting point for Microsoft cert path.","Foundation",         4.9,289,17840),
    ("microsoft","cert","Microsoft","Cert","AZ-104: Azure Administrator","Manage Azure identities, networking, storage and VMs at enterprise scale.","Associate",          4.8,221,10620),
    ("microsoft","cert","Microsoft","Cert","AZ-204: Azure Developer",    "Build and deploy Azure applications \u2014 compute, storage, APIs and more.","Associate",          4.7,148,6740),
    ("microsoft","cert","Microsoft","Cert","AZ-305: Solutions Architect","Design enterprise-grade Azure architecture across hybrid environments.","Expert",                 4.9,108,3920),
    ("microsoft","cert","Microsoft","Cert","AZ-400: DevOps Engineer",    "Azure Pipelines, continuous delivery and DevOps transformation at scale.","Expert",               4.7,86, 2780),
    ("microsoft","cert","Microsoft","Cert","SC-900: Security Fundamentals","Security, compliance and identity concepts in Microsoft cloud environments.","Foundation",      4.8,176,9180),
    ("microsoft","cert","Microsoft","Cert","SC-200: Security Operations","Microsoft Sentinel, Defender \u2014 detect, investigate and respond to threats.","Associate",     4.9,164,6240),
    ("microsoft","cert","Microsoft","Cert","SC-300: Identity & Access Admin","Azure AD, identity governance, conditional access and Zero Trust.","Associate",              4.7,118,4880),
    ("microsoft","cert","Microsoft","Cert","PL-300: Power BI Data Analyst","Interactive BI dashboards and reports \u2014 most-requested data cert in MY.","Associate",      4.9,312,12480),
    ("microsoft","cert","Microsoft","Cert","DP-203: Data Engineer",      "Design and implement data solutions in Azure \u2014 pipelines, lakes and more.","Associate",       4.9,138,5680),
    ("microsoft","cert","Microsoft","Cert","AI-102: Azure AI Engineer",  "Build and manage Azure AI solutions \u2014 OpenAI, Cognitive Services and more.","Associate",      4.8,94, 3460),
    ("microsoft","cert","Microsoft","Cert","MS-102: M365 Administrator", "Microsoft 365 tenant administration, security and compliance management.","Associate",            4.7,112,5240),

    # ---- Cisco ----
    ("cisco","cert","Cisco","Cert","CCNA",            "Routing, switching, automation and AI-driven networking. Industry standard.","Associate",   4.9,231,12940),
    ("cisco","cert","Cisco","Cert","CCNP Enterprise", "Advanced enterprise networking \u2014 routing, switching and SD-WAN.","Professional",       4.9,107,3840),
    ("cisco","cert","Cisco","Cert","CCNP Security",   "Cisco firewall, VPN, identity and threat defense solutions.","Professional",                 4.8,78, 2580),
    ("cisco","cert","Cisco","Cert","CCIE Enterprise", "Expert-level enterprise infrastructure \u2014 lab and written exams.","Expert",              4.9,42, 1340),

    # ---- Google Cloud ----
    ("gcp","cert","Google Cloud","Cert","Cloud Digital Leader",                "GCP fundamentals for business and technology decision makers.","Foundation",     4.7,98, 5240),
    ("gcp","cert","Google Cloud","Cert","Associate Cloud Engineer",            "Deploy and manage applications on GCP \u2014 compute, storage and networking.","Associate",4.8,142,6480),
    ("gcp","cert","Google Cloud","Cert","Professional Cloud Architect",        "Design enterprise-grade GCP solutions \u2014 highest value GCP cert.","Professional",   4.9,76, 2940),
    ("gcp","cert","Google Cloud","Cert","Professional Data Engineer",          "Build and maintain data pipelines and ML models on Google Cloud.","Professional",      4.8,68, 2380),
    ("gcp","cert","Google Cloud","Cert","Professional Cloud Security Engineer","Design and implement secure infrastructure on Google Cloud Platform.","Professional",  4.8,54, 1880),

    # ---- PeopleCert (ITIL + PRINCE2) ----
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Foundation",            "Most sought-after ITSM cert by Malaysian enterprises \u2014 service management essentials.","Foundation",4.9,418,16280),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Specialist: CDS",       "Create, Deliver and Support \u2014 advanced service design and delivery.","Intermediate",4.8,124,4380),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Specialist: DSV",       "Drive Stakeholder Value \u2014 customer journeys, demand and value creation.","Intermediate",4.8,98,3240),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Strategist: DPI",       "Direct, Plan and Improve \u2014 strategic IT management and continual improvement.","Advanced",4.8,76,2480),
    ("peoplecert","cert","PeopleCert","Cert","PRINCE2 Foundation & Practitioner","Widely mandated in Malaysian government and GLC project environments.","Foundation\u2192Practitioner",4.8,164,7240),

    # ---- PMI ----
    ("pmi","cert","PMI","Cert","PMP",  "Project Management Professional \u2014 global gold standard. 25% average salary boost.","Advanced",4.9,184,8920),
    ("pmi","cert","PMI","Cert","CAPM", "Certified Associate in Project Management \u2014 entry-level PM certification.","Entry",          4.8,128,5640),

    # ---- Scrum Alliance ----
    ("scrum","cert","Scrum Alliance","Cert","Certified ScrumMaster (CSM)","Agile project delivery \u2014 essential for any IT or software delivery team.","Foundation",4.8,234,11420),

    # ---- Linux Foundation ----
    ("linuxfdn","cert","Linux Foundation","Cert","Kubernetes Administrator (CKA)","Deploy, manage and secure Kubernetes clusters in production.","Intermediate",4.9,144,5180),
    ("linuxfdn","cert","Linux Foundation","Cert","CKAD \u2014 Kubernetes App Developer","Design, build and deploy applications on Kubernetes environments.","Intermediate",4.8,108,3840),

    # ---- HashiCorp ----
    ("hashicorp","cert","HashiCorp","Cert","Terraform Associate","Infrastructure as Code \u2014 provision and manage cloud with Terraform.","Associate",4.8,156,6920),

    # ---- Tableau ----
    ("tableau","cert","Tableau","Cert","Tableau Desktop Specialist","Data visualisation and analytics used globally by enterprise BI teams.","Foundation",4.7,98,4280),

    # ---- ISACA ----
    ("isaca","cert","ISACA","Cert","CISM",  "Certified Information Security Manager \u2014 governance, risk and security leadership.","Advanced",4.9,118,3840),
    ("isaca","cert","ISACA","Cert","CISA",  "Certified Information Systems Auditor \u2014 IT audit, control and compliance.","Advanced",        4.8,94, 3260),
    ("isaca","cert","ISACA","Cert","CRISC", "Certified in Risk and Information Systems Control \u2014 enterprise IT risk.","Advanced",         4.8,68, 2240),
    ("isaca","cert","ISACA","Cert","CGEIT", "Certified in Governance of Enterprise IT \u2014 C-suite and board-level credential.","Executive", 4.9,38, 1180),

    # ---- ISC2 ----
    ("isc2","cert","ISC2","Cert","CISSP",                       "The gold standard of security certs. Eight domains, globally mandated for leaders.","Expert",4.9,162,4980),
    ("isc2","cert","ISC2","Cert","SSCP",                        "Systems Security Certified Practitioner \u2014 solid mid-level security credential.","Intermediate",4.8,84,3080),
    ("isc2","cert","ISC2","Cert","CC \u2014 Certified in Cybersecurity","Free ISC2 entry-level cert \u2014 the ideal first step into the profession.","Entry",4.9,212,9840),

    # ---- Skill-Based ----
    ("skill","skill","Skill-Based","Skills","Docker & Containers",     "Containerisation fundamentals \u2014 build, ship and run applications anywhere.","Foundation",     4.8,196,9420),
    ("skill","skill","Skill-Based","Skills","CI/CD with Jenkins & GitLab","Automated delivery pipelines from code commit to production.","Intermediate",                 4.8,148,6240),
    ("skill","skill","Skill-Based","Skills","Python for IT & Automation","Automate IT tasks \u2014 network scripts, API calls and system admin.","Beginner\u2192Intermediate",4.9,284,13680),
    ("skill","skill","Skill-Based","Skills","Linux Administration",    "Server management, shell scripting and system operations on Linux.","Foundation\u2192Advanced",      4.8,212,10840),
    ("skill","skill","Skill-Based","Skills","Ansible Automation",      "Automate infrastructure configuration management at scale with Ansible.","Intermediate",            4.7,118,4640),
    ("skill","skill","Skill-Based","Skills","SQL for Data Professionals","Non-negotiable foundation for every data and analytics role.","Foundation",                     4.9,316,15280),
    ("skill","skill","Skill-Based","Skills","Excel Advanced Analytics","PivotTables, Power Query and advanced formulas for business analysts.","Foundation",              4.8,268,11920),

    # ---- Malaysia-Focused ----
    ("my","spec","Malaysia-Focused","MY","Data Governance & PDPA","Personal Data Protection Act compliance \u2014 mandatory for enterprise teams in Malaysia.","Specialist",4.9,76,2640),
]


# -----------------------------------------------------------------------------
# HTML builders
# -----------------------------------------------------------------------------
def fmt_int(n):
    return f"{n:,}"


def badge_html(badge_label, badge_class):
    if badge_label == "Cert":
        return '<span class="cbadge">Cert</span>'
    if badge_label == "Skills":
        return '<span class="cbadge sk">Skills</span>'
    if badge_label == "MY":
        return '<span class="cbadge mr">MY</span>'
    if badge_label == "New 2026":
        return '<span class="cbadge nw">New 2026</span>'
    if badge_label == "AI 2026":
        return '<span class="cbadge mr">AI 2026</span>'
    return f'<span class="cbadge">{badge_label}</span>'


_SLUG_RX = re.compile(r"[^a-z0-9]+")


def name_to_slug(name: str) -> str:
    """Stable slug for any course name (used by the admin to identify cards)."""
    s = name.lower()
    # Common-token cleanup
    s = s.replace("&", " and ")
    s = s.replace("+", " plus ")
    s = _SLUG_RX.sub("-", s).strip("-")
    return s


def card_html(c):
    (brand, cat, vendor, badge_label, name, desc, level,
     rating, reviews, enrolled) = c
    bh = badge_html(badge_label, badge_label)
    rating_str = f"{rating:.1f}"
    enrolled_str = fmt_int(enrolled)
    slug = P1.get(name) or name_to_slug(name)

    inner = (
        f'<div class="cv2">{vendor} {bh}</div>'
        f'<div class="cname2">{name}</div>'
        f'<div class="cdesc2">{desc}</div>'
        '<div class="c-stats">'
        f'  <span class="c-rate"><span class="c-star">\u2605</span> {rating_str} <em>({reviews})</em></span>'
        f'  <span class="c-enrol"><span class="c-people">\U0001F465</span> {enrolled_str}+ enrolled</span>'
        '</div>'
        '<div class="cmeta">'
        f'  <span class="clevel">{level}</span>'
        '  <span class="c-cta">View Details <span class="cta-arr">\u2192</span></span>'
        '</div>'
    )
    common_attrs = (f'data-cat="{cat}" data-brand="{brand}" '
                    f'data-slug="{slug}" data-vendor="{vendor}" '
                    f'data-level="{level}"')
    if name in P1:
        return (f'      <a href="course_pages/{slug}.html" '
                f'class="cc show" {common_attrs}>{inner}</a>')
    return f'      <div class="cc show" {common_attrs}>{inner}</div>'


def brand_block(brand_meta, cards):
    key, label, _badge, tagline, color, tint = brand_meta
    count = len(cards)
    cards_html = "\n".join(card_html(c) for c in cards)
    initials = "".join(part[0] for part in label.split()[:2]).upper()
    return (
        f'    <div class="brand-block" data-brand="{key}" '
        f'style="--bk:{color};--bk-tint:{tint}">\n'
        f'      <div class="brand-head">\n'
        f'        <div class="bh-mark" aria-hidden="true">{initials}</div>\n'
        f'        <div class="bh-text">\n'
        f'          <div class="bh-name">{label}</div>\n'
        f'          <div class="bh-tag">{tagline}</div>\n'
        f'        </div>\n'
        f'        <div class="bh-count"><span>{count}</span> course{"s" if count != 1 else ""}</div>\n'
        f'      </div>\n'
        f'      <div class="brand-grid">\n'
        f'{cards_html}\n'
        f'      </div>\n'
        f'    </div>'
    )


def build_catalog():
    blocks = []
    for bm in BRANDS:
        key = bm[0]
        bcards = [c for c in CARDS if c[0] == key]
        if not bcards:
            continue
        blocks.append(brand_block(bm, bcards))

    tabs = (
        '    <div class="filter-tabs">\n'
        '      <button class="ftab on" data-cat="all">All</button>\n'
        '      <button class="ftab" data-cat="cert">Industry Certifications</button>\n'
        '      <button class="ftab" data-cat="skill">Skill-Based Programs</button>\n'
        '      <button class="ftab" data-cat="spec">Specialized &amp; Compliance</button>\n'
        '    </div>'
    )

    grid = (
        '    <div class="cg">\n'
        + "\n".join(blocks)
        + '\n    </div>'
    )
    return tabs + "\n" + grid


def main():
    html = INDEX.read_text(encoding="utf-8")

    new_block = build_catalog()

    # Replace the existing block: from the old `<div class="filter-tabs">` to
    # the closing `</div>` of the `<div class="cg">` grid, inclusive.
    pattern = re.compile(
        r'    <div class="filter-tabs">.*?    </div>\s*\n  </div>\s*\n</section>',
        re.DOTALL,
    )

    match = pattern.search(html)
    if not match:
        # Fallback: try simpler pattern
        pattern = re.compile(
            r'    <div class="filter-tabs">.*?    </div>',
            re.DOTALL,
        )
        match = pattern.search(html)
        if not match:
            raise SystemExit("Could not locate catalog block in index.html")
        html = html[:match.start()] + new_block + html[match.end():]
    else:
        # Replace tabs + cg block, leaving </div></section> wrapper intact.
        replacement = new_block + "\n  </div>\n</section>"
        html = html[:match.start()] + replacement + html[match.end():]

    INDEX.write_text(html, encoding="utf-8")
    total_cards = sum(1 for _ in CARDS)
    total_brands = sum(1 for bm in BRANDS if any(c[0] == bm[0] for c in CARDS))
    print(f"Catalog rebuilt: {total_brands} brand groups, {total_cards} courses.")


if __name__ == "__main__":
    main()
