# -*- coding: utf-8 -*-
"""Rebuild the Course Catalog block in index.html.

Output:
- Filter tabs (All, Industry Certifications, AI & Automation, Skill-Based, Specialized)
- Courses visually grouped by BRAND (CompTIA, EC-Council, AWS, ...)
- Multi-cat placement via data-cats / data-ai (one card per course)
- Brand-themed color accents per group
"""
from pathlib import Path
import re

try:
    from scripts.site_paths import canonical_path_for_slug
except ModuleNotFoundError:
    from site_paths import canonical_path_for_slug

from _catalog_placement import apply_placements

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
    "CEH v13 AI": "ceh",
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
    # Phase 2A
    "AZ-204: Azure Developer": "az-204",
    "AZ-400: DevOps Engineer": "az-400",
    "SC-900: Security Fundamentals": "sc-900",
    "SC-300: Identity & Access Admin": "sc-300",
    "AI-102: Azure AI Engineer": "artificial-intelligence",
    "MS-102: M365 Administrator": "ms-102",
    "AWS Developer Associate": "aws-developer-associate",
    "AWS SysOps Administrator": "aws-sysops-administrator",
    # Phase 2B
    "CompTIA SecAI+": "comptia-secai-plus",
    "CompTIA SecurityX": "comptia-securityx",
    "CompTIA Linux+": "comptia-linux-plus",
    "Certified SOC Analyst (CSA)": "certified-soc-analyst-csa",
    "CCISO": "cciso",
    "CTIA": "ctia",
    "CC \u2014 Certified in Cybersecurity": "cc-certified-in-cybersecurity",
    "SSCP": "sscp",
    # Phase 2C
    "AWS DevOps Engineer Professional": "aws-devops-engineer-professional",
    "AWS Security Specialty": "aws-security-specialty",
    "AWS Data Engineer Associate": "aws-data-engineer-associate",
    "AWS Machine Learning Specialty": "aws-machine-learning-specialty",
    "CKAD \u2014 Kubernetes App Developer": "ckad-kubernetes-app-developer",
    "Terraform Associate": "terraform-associate",
    "Cloud Digital Leader": "gcp-cloud-digital-leader",
    "Associate Cloud Engineer": "gcp-associate-cloud-engineer",
    # Phase 2D
    "AZ-500: Azure Security Engineer": "az-500",
    "AZ-700: Azure Network Engineer": "az-700",
    "AZ-140: Azure Virtual Desktop": "az-140",
    "MD-102: M365 Endpoint Administrator": "md-102",
    "MS-700: Managing Microsoft Teams": "ms-700",
    "CCNP Security": "ccnp-security",
    "CCNP Collaboration": "ccnp-collaboration",
    "DevNet Associate": "devnet-associate",
    # Phase 2E
    "AI-900: Azure AI Fundamentals": "ai-900",
    "DP-100: Azure Data Scientist": "dp-100",
    "DP-300: Azure Database Admin": "dp-300",
    "PL-100: Power Platform App Maker": "pl-100",
    "PL-200: Power Platform Functional": "pl-200",
    "PL-400: Power Platform Developer": "pl-400",
    "PL-600: Power Platform Architect": "pl-600",
    "Tableau Desktop Specialist": "tableau-desktop-specialist",
    # Phase 2F
    "PRINCE2 Foundation & Practitioner": "prince2-foundation-practitioner",
    "CAPM": "capm",
    "Certified ScrumMaster (CSM)": "certified-scrum-master-csm",
    "ITIL 4 Specialist: CDS": "itil-4-specialist-cds",
    "ITIL 4 Specialist: DSV": "itil-4-specialist-dsv",
    "ITIL 4 Strategist: DPI": "itil-4-strategist-dpi",
    "AgilePM Foundation & Practitioner": "agilepm-foundation-practitioner",
    "ISO 27001 Lead Implementer": "iso-27001-lead-implementer",
    # Phase 2G
    "CRISC": "crisc",
    "CGEIT": "cgeit",
    "CDPSE": "cdpse",
    "CCSP": "ccsp",
    "HCISPP": "hcispp",
    "CSSLP": "csslp",
    "OSCP": "oscp",
    "OSWE": "oswe",
    # Phase 3: popular missing-page courses
    "CISA": "cisa",
    "SQL for Data Professionals": "sql-for-data-professionals",
    "Python Bootcamp Certification Training": "python-bootcamp",
    "Data Science with Python Certification": "data-science-with-python",
    "Excel Advanced Analytics": "excel-advanced-analytics",
    "Linux Administration": "linux-administration",
    "Docker & Containers": "docker-containers",
    "CompTIA Tech+": "comptia-tech-plus",
    "CCT \u2014 Cybersecurity Technician": "cct-cybersecurity-technician",
    "CI/CD with Jenkins & GitLab": "cicd-jenkins-gitlab",
    "CND v3": "cnd-v3",
    "CompTIA Cloud+": "comptia-cloud-plus",
    # Phase 4A & 4B
    "E|CIH": "ecih",
    "DP-900: Azure Data Fundamentals": "dp-900",
    "CCNP SPCOR": "cisco-spcor",
    "CCNP DCCOR": "cisco-dccor",
    "Cisco SD-WAN ENSDWI": "sdwan",
    "Certified Java Programming": "java-programming",
    "Full Stack Web Development": "full-stack-web-development",
    "Digital Marketing Certification": "digital-marketing",
    "Microsoft Excel 2019 Basic": "excel-basic",
    "Salesforce Admin & Automation": "salesforce-admin",
    "ServiceNow Administration Fundamentals": "servicenow-admin",
    "ServiceNow Platform Implementation": "servicenow-platform",
    # Legacy Wix bootcamps & skills (detail under /courses/{slug})
    "AI & Machine Learning Bootcamp": "ai-ml-bootcamp",
    "Generative AI for Workplace Productivity & Business Automation": "generative-ai-workplace-productivity",
    "Agentic AI": "agentic-ai",
    "Cyber Security Bootcamp": "cyber-security-bootcamp",
    "Android Development": "android-development",
    "Django Web Development": "django",
    "iOS Development": "ios-development",
    "Netflix Data Analysis Workshop": "netflix-data-analysis",
    "Fortinet FCP Network Security": "fortinet-certified-professional-network-security",
    # AI Field + Data Science short programmes (2026)
    "Building a Chatbot Using Python": "building-a-chatbot-using-python",
    "Building AI Chatbots with Python": "building-a-chatbot-using-python",
    "Deep Learning Using PyTorch": "deep-learning-using-pytorch",
    "Generative AI Applications and Python Fundamentals": "generative-ai-applications-python-fundamentals",
    "Build Generative AI Applications with LLMs": "generative-ai-applications-python-fundamentals",
    "Microsoft Copilot": "microsoft-copilot",
    "Microsoft Copilot Masterclass": "microsoft-copilot",
    "Prompt Engineering Certification Course with LLM": "prompt-engineering-certification",
    "Prompt Engineering Masterclass": "prompt-engineering-certification",
    "Claude AI in 90 Minutes Productivity Course: Build Your AI Work Assistant": "claude-ai-productivity-90-minutes",
    "Claude AI Masterclass": "claude-ai-productivity-90-minutes",
    "AI & Machine Learning Bootcamp": "ai-ml-bootcamp",
    "Machine Learning with Python": "ai-ml-bootcamp",
    "SQL for Data Professionals": "sql-for-data-professionals",
    "SQL for Data Analytics": "sql-for-data-professionals",
    "Oracle PL/SQL Database Programming Course": "oracle-plsql-database-programming",
    "Tableau for Beginners": "tableau-for-beginners",
    "Data Analytics & Visualisation with Tableau": "tableau-for-beginners",
    "ChatGPT Masterclass": "chatgpt-masterclass",
    "AI Workflow Automation (No-Code)": "ai-workflow-automation-no-code",
    "AI-Powered Workflow Automation": "ai-powered-workflow-automation",
    "AI Fundamentals": "ai-fundamentals",
    "Python for Data Analytics": "python-for-data-analytics",
    "AI-Powered Data Analytics": "ai-powered-data-analytics",
    "Data Science Foundation": "data-science-foundation",
    "Advanced Data Visualization Using Tableau": "advanced-data-visualization-tableau",
    "Data Visualization with Seaborn Using Python": "data-visualization-with-seaborn",
    "Artificial Intelligence (AI) Course Malaysia": "artificial-intelligence-ai-course-malaysia",
    "Artificial Intelligence & Machine Learning Course Malaysia": "ai-machine-learning-course-malaysia",
    # AI vendor certs from New Course PDFs (2026)
    "AI Business Professional": "ai-business-professional",
    "Azure AI Apps and Agents Developer Associate": "azure-ai-apps-agents-developer",
    "Machine Learning Operations Engineer Associate": "mlops-engineer-associate",
    "Azure AI Cloud Developer Associate": "azure-ai-cloud-developer",
    "SQL AI Developer Associate": "sql-ai-developer-associate",
    "Azure Databricks Data Engineer Associate": "azure-databricks-data-engineer",
    "Machine Learning Engineer Associate": "aws-ml-engineer-associate",
    "Generative AI Developer Professional": "aws-generative-ai-developer-professional",
    "AI Business Strategist": "aws-ai-business-strategist",
    "AWS Certified AI Practitioner": "aws-ai-practitioner",
    "Generative AI Leader": "gcp-generative-ai-leader",
    "Professional Machine Learning Engineer": "gcp-professional-machine-learning-engineer",
    "Professional Data Engineer": "gcp-professional-data-engineer",
    "Claude Certified Associate - Foundations": "claude-certified-associate-foundations",
    "Claude Certified Developer - Foundations": "claude-certified-developer-foundations",
    "Claude Certified Architect - Foundations": "claude-certified-architect-foundations",
    "Claude Certified Architect - Professional": "claude-certified-architect-professional",
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
    ("offsec",    "Offensive Security","OffSec",          "Hands-on penetration testing and offensive cybersecurity.", "#0ea5e9", "#f0f9ff"),
    ("fortinet",  "Fortinet",         "Fortinet",        "FortiGate, Security Fabric, SD-WAN and network security certs.", "#ee3124", "#fef2f2"),
    ("anthropic", "Anthropic",        "Anthropic",       "Claude certifications and practical Anthropic AI workflows.", "#d97706", "#fffbeb"),
    ("openai",    "OpenAI",           "OpenAI",          "ChatGPT and practical OpenAI workplace productivity skills.", "#10a37f", "#ecfdf5"),
    ("salesforce","Salesforce",       "Salesforce",      "Admin, automation and CRM platform skills on Salesforce.", "#00a1e0", "#eff9ff"),
    ("servicenow","ServiceNow",       "ServiceNow",      "Now Platform administration and implementation programmes.", "#81b5a1", "#f0fdf6"),
    ("oracle",    "Oracle",           "Oracle",          "Oracle database development and PL/SQL programming.", "#f80000", "#fef2f2"),
    ("nonvendor", "Non-Vendor",       "Skills",          "Hands-on, role-ready skills \u2014 outcome over paperwork.","#10b981", "#ecfdf5"),
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
    ("comptia","cert","CompTIA","Cert","CompTIA Tech+",              "Digital literacy and tech fundamentals for any business professional.","Entry",            4.8,156,8240),
    ("comptia","spec","CompTIA","New 2026","CompTIA SecAI+",         "Secure and govern AI in cybersecurity operations. First cert of its kind.","Intermediate", 4.9,46, 1840),

    # ---- EC-Council ----
    ("eccouncil","cert","EC-Council","Cert","CEH v13 AI",            "Certified Ethical Hacker \u2014 flagship offensive security cert, AI-integrated.","Intermediate", 4.9,612,24180),
    ("eccouncil","cert","EC-Council","Cert","CPENT AI",              "Certified Penetration Testing Professional \u2014 advanced real-world attack labs.","Advanced",   4.8,118,3640),
    ("eccouncil","cert","EC-Council","Cert","CHFI v11",              "Computer Hacking Forensic Investigator \u2014 digital forensics and evidence.","Intermediate",  4.8,94, 4320),
    ("eccouncil","cert","EC-Council","Cert","Certified SOC Analyst (CSA)","SOC operations, threat monitoring, alert triage and incident reporting.","Entry\u2013Mid",4.8,168,9620),
    ("eccouncil","cert","EC-Council","Cert","CND v3",                "Certified Network Defender \u2014 proactive network protection and defense.","Intermediate",   4.7,124,5780),
    ("fortinet","cert","Fortinet","Cert","Fortinet FCP Network Security","Fortinet Certified Professional \u2014 FortiGate, VPN, SD-WAN and Security Fabric.","Professional",4.8,118,6420),
    ("eccouncil","cert","EC-Council","Cert","CCISO",                 "Chief Information Security Officer \u2014 executive cybersecurity leadership.","Executive",   4.9,42, 1620),
    ("eccouncil","cert","EC-Council","Cert","CTIA",                  "Certified Threat Intelligence Analyst \u2014 dark web intel, threat hunting.","Advanced",      4.8,86, 2940),
    ("eccouncil","cert","EC-Council","Cert","CCT \u2014 Cybersecurity Technician","Entry-level hands-on cybersecurity \u2014 the right starting point in security.","Entry",4.8,142,7940),
    ("eccouncil","cert","EC-Council","Cert","E|CIH","Certified Incident Handler \u2014 structured IR, playbooks and EC-Council exam readiness.","Intermediate",4.8,156,6820),

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
    ("microsoft","cert","Microsoft","Cert","DP-900: Azure Data Fundamentals","Relational and analytics data concepts on Azure \u2014 foundation for every data role.","Foundation",4.9,178,11240),
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
    ("microsoft","cert","Microsoft","Cert","AZ-500: Azure Security Engineer","Implement security controls, threat protection and identity in Azure.","Associate",            4.8,116,4280),
    ("microsoft","cert","Microsoft","Cert","AZ-700: Azure Network Engineer", "Design, implement and manage Azure networking, hybrid and ExpressRoute.","Associate",          4.8,82, 2640),
    ("microsoft","cert","Microsoft","Cert","AZ-140: Azure Virtual Desktop", "Plan, deliver and manage Azure Virtual Desktop for the modern workspace.","Specialty",          4.7,68, 2180),
    ("microsoft","cert","Microsoft","Cert","MD-102: M365 Endpoint Administrator","Intune, Autopilot and Windows endpoint management at enterprise scale.","Associate",       4.8,124,5840),
    ("microsoft","cert","Microsoft","Cert","MS-700: Managing Microsoft Teams","Plan, configure and manage Microsoft Teams \u2014 voice, meetings and governance.","Associate",4.7,98, 4360),
    ("microsoft","cert","Microsoft","Cert","AI-900: Azure AI Fundamentals", "Foundational AI and machine learning concepts on Azure \u2014 the AI runway cert.","Foundation",                4.9,212,11420),
    ("microsoft","cert","Microsoft","Cert","DP-100: Azure Data Scientist",  "Train, evaluate and deploy ML models on Azure ML at production grade.","Associate",                       4.8,86, 3120),
    ("microsoft","cert","Microsoft","Cert","DP-300: Azure Database Admin",  "Administer SQL Server and Azure SQL at scale \u2014 HA, security, performance.","Associate",              4.8,108,4640),
    ("microsoft","cert","Microsoft","Cert","PL-100: Power Platform App Maker","Citizen-developer apps on Power Platform \u2014 Apps, Power Automate, Dataverse.","Foundation",        4.8,168,7920),
    ("microsoft","cert","Microsoft","Cert","PL-200: Power Platform Functional","Configure model-driven apps, Power Automate flows and Dataverse for business solutions.","Associate", 4.7,98, 3840),
    ("microsoft","cert","Microsoft","Cert","PL-400: Power Platform Developer","Pro-code Power Platform \u2014 plugins, custom connectors, code components and ALM.","Associate",          4.8,76, 2640),
    ("microsoft","cert","Microsoft","Cert","PL-600: Power Platform Architect","Design end-to-end Power Platform solutions across data, security, integrations and governance.","Expert",4.9,52, 1820),

    # ---- Cisco ----
    ("cisco","cert","Cisco","Cert","CCNA",            "Routing, switching, automation and AI-driven networking. Industry standard.","Associate",   4.9,231,12940),
    ("cisco","cert","Cisco","Cert","CCNP Enterprise", "Advanced enterprise networking \u2014 routing, switching and SD-WAN.","Professional",       4.9,107,3840),
    ("cisco","cert","Cisco","Cert","CCNP Security",   "Cisco firewall, VPN, identity and threat defense solutions.","Professional",                 4.8,78, 2580),
    ("cisco","cert","Cisco","Cert","CCNP Collaboration","Cisco voice, video, contact-centre and collaboration deployment at depth.","Professional", 4.7,52, 1620),
    ("cisco","cert","Cisco","Cert","DevNet Associate", "Cisco network programmability \u2014 APIs, automation and infrastructure as code.","Associate",4.8,86, 3240),
    ("cisco","cert","Cisco","Cert","CCNP SPCOR","Service provider core networking \u2014 MPLS, segment routing and WAN-scale routing.","Professional",4.8,92, 3180),
    ("cisco","cert","Cisco","Cert","CCNP DCCOR","Data center core \u2014 NX-OS, ACI foundations and modern DC operations.","Professional",4.8,78, 2840),
    ("cisco","cert","Cisco","Cert","Cisco SD-WAN ENSDWI","Design, deploy and operate Cisco SD-WAN with policy-driven enterprise WANs.","Professional",4.8,104,4120),

    # ---- Google Cloud ----
    ("gcp","cert","Google Cloud","Cert","Cloud Digital Leader",                "GCP fundamentals for business and technology decision makers.","Foundation",     4.7,98, 5240),
    ("gcp","cert","Google Cloud","Cert","Associate Cloud Engineer",            "Deploy and manage applications on GCP \u2014 compute, storage and networking.","Associate",4.8,142,6480),
    ("gcp","cert","Google Cloud","Cert","Professional Cloud Architect",        "Design enterprise-grade GCP solutions \u2014 highest value GCP cert.","Professional",   4.9,76, 2940),

    # ---- PeopleCert (ITIL + PRINCE2) ----
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Foundation",            "Most sought-after ITSM cert by Malaysian enterprises \u2014 service management essentials.","Foundation",4.9,418,16280),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Specialist: CDS",       "Create, Deliver and Support \u2014 advanced service design and delivery.","Intermediate",4.8,124,4380),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Specialist: DSV",       "Drive Stakeholder Value \u2014 customer journeys, demand and value creation.","Intermediate",4.8,98,3240),
    ("peoplecert","cert","PeopleCert","Cert","ITIL 4 Strategist: DPI",       "Direct, Plan and Improve \u2014 strategic IT management and continual improvement.","Advanced",4.8,76,2480),
    ("peoplecert","cert","PeopleCert","Cert","PRINCE2 Foundation & Practitioner","Widely mandated in Malaysian government and GLC project environments.","Foundation\u2192Practitioner",4.8,164,7240),
    ("peoplecert","cert","PeopleCert","Cert","AgilePM Foundation & Practitioner","Agile project management at scale \u2014 PeopleCert / APMG framework.","Foundation\u2192Practitioner",4.8,98,3920),
    ("peoplecert","cert","PeopleCert","Cert","ISO 27001 Lead Implementer","Implement an ISO 27001 ISMS at depth \u2014 governance, risk and audit-ready controls.","Advanced",4.9,76,2640),

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
    ("isaca","cert","ISACA","Cert","CDPSE", "Certified Data Privacy Solutions Engineer \u2014 privacy by design and PDPA depth.","Advanced",   4.8,52, 1640),

    # ---- ISC2 ----
    ("isc2","cert","ISC2","Cert","CISSP",                       "The gold standard of security certs. Eight domains, globally mandated for leaders.","Expert",4.9,162,4980),
    ("isc2","cert","ISC2","Cert","SSCP",                        "Systems Security Certified Practitioner \u2014 solid mid-level security credential.","Intermediate",4.8,84,3080),
    ("isc2","cert","ISC2","Cert","CC \u2014 Certified in Cybersecurity","Free ISC2 entry-level cert \u2014 the ideal first step into the profession.","Entry",4.9,212,9840),
    ("isc2","cert","ISC2","Cert","CCSP",                        "Certified Cloud Security Professional \u2014 the senior cloud-security cert from ISC2.","Advanced",4.8,72,2840),
    ("isc2","cert","ISC2","Cert","HCISPP",                      "Healthcare Information Security and Privacy Practitioner \u2014 HIPAA / PDPA aligned.","Intermediate",4.7,46,1480),
    ("isc2","cert","ISC2","Cert","CSSLP",                       "Certified Secure Software Lifecycle Professional \u2014 secure SDLC and AppSec at depth.","Advanced",4.8,58,1860),

    # ---- Offensive Security ----
    ("offsec","cert","Offensive Security","Cert","OSCP",        "Offensive Security Certified Professional \u2014 the gold-standard pentest cert. PEN-200.","Advanced",4.9,128,4280),
    ("offsec","cert","Offensive Security","Cert","OSWE",        "Offensive Security Web Expert \u2014 advanced web-application exploitation. WEB-300.","Expert",4.9,42,1240),

    # ---- Skill-Based ----
    ("skill","skill","Skill-Based","Skills","Docker & Containers",     "Containerisation fundamentals \u2014 build, ship and run applications anywhere.","Foundation",     4.8,196,9420),
    ("skill","skill","Skill-Based","Skills","CI/CD with Jenkins & GitLab","Automated delivery pipelines from code commit to production.","Intermediate",                 4.8,148,6240),
    ("skill","skill","Skill-Based","Skills","Python Bootcamp Certification Training","Completely project-based Python Bootcamp Certification Training Course.","Beginner\u2192Intermediate",4.9,284,13680),
    ("skill","skill","Skill-Based","Skills","Data Science with Python Certification","Live Online | Project-Based | Career-Focused","Beginner\u2192Intermediate",4.9,198,8920),
    ("skill","skill","Skill-Based","Skills","Linux Administration",    "Server management, shell scripting and system operations on Linux.","Foundation\u2192Advanced",      4.8,212,10840),
    ("skill","skill","Skill-Based","Skills","SQL for Data Analytics","Turn raw business data into clear, reliable insights using SQL.","Beginner to Intermediate",                     4.9,316,15280),
    ("skill","skill","Skill-Based","Skills","Excel Advanced Analytics","PivotTables, Power Query and advanced formulas for business analysts.","Foundation",              4.8,268,11920),
    ("skill","skill","Skill-Based","Skills","Microsoft Excel 2019 Basic","Spreadsheet essentials \u2014 navigation, formulas, charts and workplace productivity.","Foundation",4.9,260,12880),
    ("skill","skill","Skill-Based","Skills","Certified Java Programming","Enterprise Java foundations through JDBC and Spring Boot introduction \u2014 portfolio-ready.","Beginner\u2192Intermediate",4.8,142,7180),
    ("skill","skill","Skill-Based","Skills","Full Stack Web Development","React, Node and SQL in one portfolio sprint \u2014 modern web stack for junior roles.","Beginner\u2192Intermediate",4.8,188,8640),
    ("skill","skill","Skill-Based","Skills","Digital Marketing Certification","SEO, paid media, analytics and campaign storytelling with Malaysian market examples.","Foundation\u2192Practitioner",4.8,124,5920),
    ("skill","skill","Skill-Based","Skills","Salesforce Admin & Automation","Lightning admin, security model, Flow automation and release hygiene on Salesforce.","Associate\u2192Advanced",4.8,96, 4980),
    ("skill","skill","Skill-Based","Skills","ServiceNow Administration Fundamentals","Core Now Platform admin \u2014 users, ACLs, workflows and safe instance operations.","Fundamentals",4.8,84, 4360),
    ("skill","skill","Skill-Based","Skills","ServiceNow Platform Implementation","Lead greenfield programmes \u2014 CMDB, integrations and steering-ready artefacts.","Professional",4.7,58, 2140),
    ("skill","skill","Skill-Based","AI 2026","Machine Learning with Python","Build predictive models, evaluate results and turn data into practical ML solutions.","Beginner to Intermediate",4.8,118,6420),
    ("skill","skill","Skill-Based","AI 2026","Generative AI for Workplace Productivity & Business Automation","Two-day workplace programme — professional prompts, department scenarios, AI workflows and responsible use.","All levels",4.9,94,5280),
    ("skill","skill","Skill-Based","AI 2026","Agentic AI","Multi-step agents, tool orchestration, memory and human-in-the-loop \u2014 agentic systems you can audit and scale.","Advanced",4.8,78,4620),
    ("skill","skill","Skill-Based","Skills","Cyber Security Bootcamp","Blue-team, ethical hacking labs and IR tabletop \u2014 security champions for Malaysian enterprises.","Foundation\u2192Intermediate",4.9,132,7180),
    ("skill","skill","Skill-Based","Skills","Android Development","Kotlin, Jetpack Compose, MVVM and Play Store readiness with portfolio coaching.","Beginner\u2192Intermediate",4.7,86, 4280),
    ("skill","skill","Skill-Based","Skills","Django Web Development","Models, DRF APIs, auth and deploy \u2014 production-shaped Python web apps.","Intermediate",4.8,82, 3840),
    ("skill","skill","Skill-Based","Skills","iOS Development","Swift, SwiftUI, TestFlight and MVVM \u2014 ship an iPhone portfolio app.","Beginner\u2192Intermediate",4.7,74, 3620),
    ("skill","skill","Skill-Based","Workshop","Netflix Data Analysis Workshop","pandas + visualization storytelling on a streaming dataset \u2014 two-day workshop.","Beginner+",4.9,62, 2840),
    # ---- AI Field + Data Science shorts ----
    ("skill","skill","Skill-Based","AI 2026","Building AI Chatbots with Python","Design, develop and test conversational apps with Python, LLM APIs and RAG.","Intermediate",4.8,64, 2760),
    ("skill","skill","Skill-Based","AI 2026","Deep Learning Using PyTorch","Build, train and evaluate neural networks through hands-on PyTorch projects.","Intermediate",4.8,58, 2420),
    ("skill","skill","Skill-Based","AI 2026","Build Generative AI Applications with LLMs","Turn LLMs into useful apps with APIs, retrieval, evaluation and deployment.","Intermediate",4.8,70, 2980),
    ("skill","skill","Skill-Based","AI 2026","Microsoft Copilot Masterclass","Work smarter with AI across Microsoft 365 — drafts, analysis and responsible use.","Beginner to Intermediate",4.9,96, 5340),
    ("skill","skill","Skill-Based","AI 2026","Prompt Engineering Masterclass","Design better prompts, evaluate outputs and build repeatable AI workflows.","Beginner to Intermediate",4.9,84, 3860),
    ("skill","skill","Skill-Based","AI 2026","Claude AI Masterclass","Master Claude for workplace productivity — writing, research and repeatable workflows.","Beginner to Intermediate",4.9,54, 2180),
    ("skill","skill","Skill-Based","Skills","Oracle PL/SQL Database Programming Course","Procedures, functions, packages, cursors and exceptions for Oracle database development.","Intermediate",4.8,66, 2640),
    ("skill","skill","Skill-Based","Skills","Data Analytics & Visualisation with Tableau","Turn raw business data into interactive dashboards and actionable insights.","Beginner to Intermediate",4.8,78, 3460),
    ("skill","skill","Skill-Based","Skills","Data Science Foundation","Data science lifecycle foundations \u2014 wrangling, EDA, light modelling and storytelling.","Beginner+",4.8,82, 3720),
    ("skill","skill","Skill-Based","Skills","Advanced Data Visualization Using Tableau","LOD, advanced calcs, interactivity and executive-ready Tableau dashboard design.","Intermediate",4.8,60, 2480),
    ("skill","skill","Skill-Based","Skills","Data Visualization with Seaborn Using Python","Statistical visuals with Seaborn \u2014 distributions, relationships and report-ready figures.","Beginner+",4.8,68, 2860),
    ("skill","skill","Skill-Based","AI 2026","Artificial Intelligence (AI) Course Malaysia","Instructor-led AI from fundamentals through Python, Machine Learning, Generative AI, LLMs, RAG and an introduction to AI agents.","Beginner to Intermediate",4.9,48,3920),
    ("skill","skill","Skill-Based","AI 2026","Artificial Intelligence & Machine Learning Course Malaysia","40-hour hands-on Machine Learning with Python — regression, classification, clustering, evaluation and neural networks.","Beginner to Intermediate",4.8,42,3560),

    # ---- Practical AI / data skill PDFs (2026) ----
    ("skill","skill","Skill-Based","AI 2026","ChatGPT Masterclass","Use ChatGPT for research, writing, analysis and repeatable workplace tasks.","Beginner to Intermediate",4.9,38,1820),
    ("skill","skill","Skill-Based","AI 2026","AI Workflow Automation (No-Code)","Design no-code automations connecting forms, email, spreadsheets, CRM and AI tools.","Beginner to Intermediate",4.8,28,1340),
    ("skill","skill","Skill-Based","AI 2026","AI-Powered Workflow Automation","Build intelligent workflows that interpret information with reliable human oversight.","Intermediate",4.8,24,1180),
    ("skill","skill","Skill-Based","AI 2026","AI Fundamentals","Beginner-friendly introduction to AI, machine learning and generative AI — no coding required.","Beginner",4.9,42,1960),
    ("skill","skill","Skill-Based","Skills","Python for Data Analytics","Prepare datasets, explore patterns and visualise insights with Python, Pandas and Seaborn.","Beginner to Intermediate",4.8,36,1680),
    ("skill","skill","Skill-Based","AI 2026","AI-Powered Data Analytics","Analyse spreadsheets and business data with AI tools — no Python or SQL required.","Beginner to Intermediate",4.8,30,1420),

    # ---- New AI vendor certifications (New Course PDFs) ----
    ("microsoft","cert","Microsoft","New 2026","AI Business Professional","Microsoft 365 Copilot foundations for business users, managers and analysts.","Foundation",4.8,36,1680),
    ("microsoft","cert","Microsoft","New 2026","Azure AI Apps and Agents Developer Associate","Build AI apps and agents on Azure with responsible development practices.","Associate",4.8,28,1420),
    ("microsoft","cert","Microsoft","New 2026","Machine Learning Operations Engineer Associate","MLOps on Azure — pipelines, monitoring and production ML operations.","Associate",4.8,24,1180),
    ("microsoft","cert","Microsoft","New 2026","Azure AI Cloud Developer Associate","Develop AI-powered cloud applications on Microsoft Azure.","Associate",4.8,26,1260),
    ("microsoft","cert","Microsoft","New 2026","SQL AI Developer Associate","Apply AI capabilities in SQL and data workloads on Microsoft platforms.","Associate",4.8,22,1040),
    ("microsoft","cert","Microsoft","New 2026","Azure Databricks Data Engineer Associate","Data engineering with Azure Databricks for analytics and AI pipelines.","Associate",4.8,30,1380),
    ("aws","cert","AWS","New 2026","Machine Learning Engineer Associate","Build, train and deploy ML solutions on AWS (MLA-C01).","Associate",4.8,32,1540),
    ("aws","cert","AWS","New 2026","Generative AI Developer Professional","Professional generative AI development on AWS (AIP-C01).","Professional",4.8,20,980),
    ("aws","cert","AWS","New 2026","AI Business Strategist","Guide AI investment, adoption and transformation on AWS (AIB-C01).","Foundation",4.8,18,860),
    ("aws","cert","AWS","New 2026","AWS Certified AI Practitioner","Foundational AI literacy and AWS AI services for the AIF-C01 exam.","Foundation",4.9,48,2140),
    ("gcp","cert","Google Cloud","New 2026","Generative AI Leader","Lead generative AI strategy and adoption on Google Cloud.","Foundation",4.8,22,1120),
    ("gcp","cert","Google Cloud","New 2026","Professional Machine Learning Engineer","Design and productionise ML solutions on Google Cloud.","Professional",4.8,34,1480),
    ("gcp","cert","Google Cloud","New 2026","Professional Data Engineer","Design reliable data processing systems on Google Cloud.","Professional",4.8,40,1720),
    ("anthropic","cert","Anthropic","New 2026","Claude Certified Associate - Foundations","Non-technical Claude foundations for everyday workplace use (CCAO-F).","Foundation",4.8,16,720),
    ("anthropic","cert","Anthropic","New 2026","Claude Certified Developer - Foundations","Developer foundations for building with Claude (CCDV-F).","Foundation",4.8,14,640),
    ("anthropic","cert","Anthropic","New 2026","Claude Certified Architect - Foundations","Architecture foundations for Claude solutions (CCAR-F).","Foundation",4.8,12,580),
    ("anthropic","cert","Anthropic","New 2026","Claude Certified Architect - Professional","Professional Claude solution architecture (CCAR-P).","Professional",4.8,10,520),
]

# Normalize brands/cats (Skill Vendor split + AI dual placement)
CARDS = apply_placements(CARDS)

# Dual-list new AI vendor certs (same rule as AI_VENDOR_CERT_EXTRA)
_NEW_AI_CERT_NAMES = {
    "AI Business Professional",
    "Azure AI Apps and Agents Developer Associate",
    "Machine Learning Operations Engineer Associate",
    "Azure AI Cloud Developer Associate",
    "SQL AI Developer Associate",
    "Azure Databricks Data Engineer Associate",
    "Machine Learning Engineer Associate",
    "Generative AI Developer Professional",
    "AI Business Strategist",
    "AWS Certified AI Practitioner",
    "Generative AI Leader",
    "Professional Machine Learning Engineer",
    "Professional Data Engineer",
    "Claude Certified Associate - Foundations",
    "Claude Certified Developer - Foundations",
    "Claude Certified Architect - Foundations",
    "Claude Certified Architect - Professional",
}
_fixed = []
for c in CARDS:
    brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats = c
    if name in _NEW_AI_CERT_NAMES:
        cats = tuple(dict.fromkeys(cats + ("ai", "skill")))
        cat = "cert"
    _fixed.append((brand, cat, vendor, badge, name, desc, level, rating, reviews, enrolled, cats))
CARDS = _fixed


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
    if badge_label == "Workshop":
        return '<span class="cbadge">Workshop</span>'
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
     rating, reviews, enrolled, cats) = c
    bh = badge_html(badge_label, badge_label)
    rating_str = f"{rating:.1f}"
    enrolled_str = fmt_int(enrolled)
    slug = P1.get(name) or name_to_slug(name)
    cats_attr = " ".join(cats)
    data_ai = "1" if "ai" in cats else "0"

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
    common_attrs = (
        f'data-cat="{cat}" data-cats="{cats_attr}" data-ai="{data_ai}" '
        f'data-brand="{brand}" data-slug="{slug}" data-vendor="{vendor}" '
        f'data-level="{level}"'
    )
    if name in P1:
        return (f'      <a href="{canonical_path_for_slug(slug)}" '
                f'class="cc show" {common_attrs}>{inner}</a>')
    return f'      <div class="cc show" {common_attrs}>{inner}</div>'


def brand_block(brand_meta, cards):
    key, label, _badge, tagline, color, tint = brand_meta
    count = len(cards)
    cards_html = "\n".join(card_html(c) for c in cards)
    initials = "".join(part[0] for part in label.split()[:2]).upper()
    # Use data-course-count (NOT data-count) — data-count is reserved for the
    # hero animated counter which replaces element textContent.
    size_cls = f" brand-block--n{count}" if count <= 2 else ""
    return (
        f'    <div class="brand-block{size_cls}" data-brand="{key}" '
        f'data-course-count="{count}" style="--bk:{color};--bk-tint:{tint}">\n'
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
        '      <button class="ftab" data-cat="ai">AI &amp; Automation</button>\n'
        '      <button class="ftab" data-cat="skill">Skill-Based Programs</button>\n'
        '      <button class="ftab" data-cat="spec">Specialized &amp; Compliance</button>\n'
        '    </div>'
    )

    grid = (
        '    <div class="cg">\n'
        + "\n".join(blocks)
        + '\n    </div>'
    )
    return tabs, grid


def _replace_courses_section(html: str, new_tabs: str, new_grid: str) -> str:
    """Update filter-tabs and .cg only — preserve catalog-search-wrap between them."""
    sec_pat = re.compile(r'(<section id="courses">)(.*?)(</section>)', re.DOTALL)
    sec_m = sec_pat.search(html)
    if not sec_m:
        raise SystemExit('Could not locate <section id="courses"> in index.html')

    sec_body = sec_m.group(2)

    tabs_pat = re.compile(r'    <div class="filter-tabs">.*?</div>', re.DOTALL)
    if not tabs_pat.search(sec_body):
        raise SystemExit("Could not locate filter-tabs in courses section")
    sec_body = tabs_pat.sub(new_tabs, sec_body, count=1)

    cg_start = sec_body.find('    <div class="cg">')
    if cg_start < 0:
        raise SystemExit("Could not locate .cg grid in courses section")

    # Closing `    </div>` of .cg is immediately before `  </div>` (closes .sw)
    before_sw_close = sec_body.rfind("\n  </div>")
    if before_sw_close < 0:
        raise SystemExit("Could not locate .sw wrapper close in courses section")
    cg_close = sec_body.rfind("    </div>", 0, before_sw_close)
    if cg_close < 0 or cg_close < cg_start:
        raise SystemExit("Could not locate .cg closing tag")

    sec_body = sec_body[:cg_start] + new_grid + sec_body[cg_close + len("    </div>") :]

    new_sec = sec_m.group(1) + sec_body + sec_m.group(3)
    return html[: sec_m.start()] + new_sec + html[sec_m.end() :]


def main():
    html = INDEX.read_text(encoding="utf-8")
    new_tabs, new_grid = build_catalog()
    html = _replace_courses_section(html, new_tabs, new_grid)
    INDEX.write_text(html, encoding="utf-8")
    total_cards = sum(1 for _ in CARDS)
    total_brands = sum(1 for bm in BRANDS if any(c[0] == bm[0] for c in CARDS))
    print(f"Catalog rebuilt: {total_brands} brand groups, {total_cards} courses.")


if __name__ == "__main__":
    main()
