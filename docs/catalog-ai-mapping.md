# Phase 0 — AI & Automation + Skill Vendor Mapping

Decisions: **1A** (AI vendor certs stay in Industry Certifications + AI & Automation + Skill-Based) · **2A** (all Skill-Based courses use Vendor / Non-Vendor brands).

## Placement keys

- `cats`: space-separated placements on one card (`cert`, `ai`, `skill`, `spec`)
- `brand`: vendor brand block key

## A. New / overwrite from New Course PDFs

| Course | Exam | Brand | Cats | Slug | Action |
|--------|------|-------|------|------|--------|
| AI Business Professional | AB-730 | microsoft | cert ai skill | ai-business-professional | create |
| Azure AI Apps and Agents Developer Associate | AI-103 | microsoft | cert ai skill | azure-ai-apps-agents-developer | create |
| Azure AI Fundamentals | AI-901 | microsoft | cert ai skill | ai-900 | overwrite |
| Machine Learning Operations Engineer Associate | AI-300 | microsoft | cert ai skill | mlops-engineer-associate | create |
| Azure AI Cloud Developer Associate | AI-200 | microsoft | cert ai skill | azure-ai-cloud-developer | create |
| SQL AI Developer Associate | DP-800 | microsoft | cert ai skill | sql-ai-developer-associate | create |
| Azure Databricks Data Engineer Associate | DP-750 | microsoft | cert ai skill | azure-databricks-data-engineer | create |
| Machine Learning Engineer Associate | MLA-C01 | aws | cert ai skill | aws-ml-engineer-associate | create |
| Generative AI Developer Professional | AIP-C01 | aws | cert ai skill | aws-generative-ai-developer-professional | create |
| AI Business Strategist | AIB-C01 | aws | cert ai skill | aws-ai-business-strategist | create |
| AWS Certified AI Practitioner | AIF-C01 | aws | cert ai skill | aws-ai-practitioner | create |
| Generative AI Leader | Generative AI Leader | gcp | cert ai skill | gcp-generative-ai-leader | create |
| Cloud Digital Leader | Cloud Digital Leader | gcp | cert ai skill | gcp-cloud-digital-leader | overwrite |
| Professional Machine Learning Engineer | Professional ML Engineer | gcp | cert ai skill | gcp-professional-machine-learning-engineer | create |
| Professional Data Engineer | Professional Data Engineer | gcp | cert ai skill | gcp-professional-data-engineer | create |
| Claude Certified Associate - Foundations | CCAO-F | anthropic | cert ai skill | claude-certified-associate-foundations | create |
| Claude Certified Developer - Foundations | CCDV-F | anthropic | cert ai skill | claude-certified-developer-foundations | create |
| Claude Certified Architect - Foundations | CCAR-F | anthropic | cert ai skill | claude-certified-architect-foundations | create |
| Claude Certified Architect - Professional | CCAR-P | anthropic | cert ai skill | claude-certified-architect-professional | create |

## B. Existing AI courses → add `ai` (+ `skill` for vendor certs)

| Course | Brand | Cats |
|--------|-------|------|
| AI-900: Azure AI Fundamentals | microsoft | cert ai skill |
| DP-100: Azure Data Scientist | microsoft | cert ai skill |
| AI-102: Azure AI Engineer | microsoft | cert ai skill |
| AWS Machine Learning Specialty | aws | cert ai skill |
| CompTIA SecAI+ | comptia | spec ai skill |
| CPENT AI | eccouncil | cert ai skill |
| Microsoft Copilot | microsoft | skill ai |
| Claude AI 90 Minutes | anthropic | skill ai |
| AI & Machine Learning Bootcamp | nonvendor | skill ai |
| Generative AI Workplace Productivity | nonvendor | skill ai |
| Agentic AI | nonvendor | skill ai |
| Building a Chatbot Using Python | nonvendor | skill ai |
| Deep Learning Using PyTorch | nonvendor | skill ai |
| Generative AI Applications and Python Fundamentals | nonvendor | skill ai |
| Prompt Engineering Certification | nonvendor | skill ai |
| Artificial Intelligence (AI) Course Malaysia | nonvendor | skill ai |
| Artificial Intelligence & Machine Learning Course Malaysia | nonvendor | skill ai |

## C. Non-AI Skill-Based remap (skill only)

| Course | Brand |
|--------|-------|
| Excel Advanced Analytics | microsoft |
| Microsoft Excel 2019 Basic | microsoft |
| Salesforce Admin & Automation | salesforce |
| ServiceNow Administration Fundamentals | servicenow |
| ServiceNow Platform Implementation | servicenow |
| Tableau for Beginners | tableau |
| Advanced Data Visualization Using Tableau | tableau |
| Oracle PL/SQL Database Programming | oracle |
| Docker & Containers | nonvendor |
| CI/CD with Jenkins & GitLab | nonvendor |
| Python Bootcamp | nonvendor |
| Data Science with Python | nonvendor |
| Linux Administration | nonvendor |
| SQL for Data Professionals | nonvendor |
| Certified Java Programming | nonvendor |
| Full Stack Web Development | nonvendor |
| Digital Marketing Certification | nonvendor |
| Cyber Security Bootcamp | nonvendor |
| Android Development | nonvendor |
| Django Web Development | nonvendor |
| iOS Development | nonvendor |
| Netflix Data Analysis Workshop | nonvendor |
| Data Science Foundation | nonvendor |
| Data Visualization with Seaborn | nonvendor |
