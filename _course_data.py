# -*- coding: utf-8 -*-
"""Per-course unique content data for Phase-1 detail pages.

Each course entry is unique on:
- exam_main / exam_optional
- pass_rate + pass_intro + pass_compare
- next_steps + path_chips + salary_html
- reviews (4 unique people each)
- price + price_orig + price_save
- next_intake date
"""

HERO_IMG = "../image/people-taking-part-high-protocol-event.jpg"


def common_meta(duration, fmt, delivery, pass_rate, intake):
    return [
        ("\u23f1", "Duration", duration, None),
        ("\U0001F4BB", "Format", fmt, None),
        ("\U0001F310", "Delivery", delivery, None),
        ("\u2705", "Pass rate", f"{pass_rate}%", "#86efac"),
        ("\U0001F4C5", "Next intake", intake, None),
    ]


COURSES = []

from _course_batch_comptia import BATCH as _B_COMPTIA
COURSES.extend(_B_COMPTIA)

from _course_batch_eccouncil import BATCH as _B_ECCOUNCIL
COURSES.extend(_B_ECCOUNCIL)

from _course_batch_aws import BATCH as _B_AWS
COURSES.extend(_B_AWS)

from _course_batch_microsoft import BATCH as _B_MS
COURSES.extend(_B_MS)

from _course_batch_cisco_gcp import BATCH as _B_CG
COURSES.extend(_B_CG)

from _course_batch_itil_pm_devops import BATCH as _B_IPD
COURSES.extend(_B_IPD)

from _course_batch_isaca_isc2 import BATCH as _B_ISA
COURSES.extend(_B_ISA)

# Phase 2 Batch A: Microsoft cloud + AWS dev/ops associates
from _course_batch_phase2a import BATCH as _B_P2A
COURSES.extend(_B_P2A)

# Phase 2 Batch B: Cybersecurity (CompTIA + EC-Council + ISC2)
from _course_batch_phase2b import BATCH as _B_P2B
COURSES.extend(_B_P2B)

# Phase 2 Batch C: Cloud Pro tier (AWS Pro/Specialty + Kubernetes + Terraform + GCP)
from _course_batch_phase2c import BATCH as _B_P2C
COURSES.extend(_B_P2C)

# Phase 2 Batch D: Microsoft + Cisco depth (AZ-500/700/140, MD-102, MS-700, CCNP Sec/Collab, DevNet)
from _course_batch_phase2d import BATCH as _B_P2D
COURSES.extend(_B_P2D)

# Phase 2 Batch E: Data, BI & AI tier 2 (AI-900, DP-100, DP-300, PL-100/200/400/600, Tableau)
from _course_batch_phase2e import BATCH as _B_P2E
COURSES.extend(_B_P2E)

# Phase 2 Batch F: ITSM, PM & Agile (PRINCE2, CAPM, CSM, ITIL CDS/DSV/DPI, AgilePM, ISO 27001 LI)
from _course_batch_phase2f import BATCH as _B_P2F
COURSES.extend(_B_P2F)

# Phase 2 Batch G (FINAL): Specialty depth (CRISC, CGEIT, CDPSE, CCSP, HCISPP, CSSLP, OSCP, OSWE)
from _course_batch_phase2g import BATCH as _B_P2G
COURSES.extend(_B_P2G)

# Phase 3: Popular missing-page courses to round out the catalog at 92 with full coverage
# (CISA, SQL, Python, Excel, Linux, Docker, CompTIA Tech+, CCT, CI/CD, CND v3, CompTIA Cloud+)
from _course_batch_phase3 import BATCH as _B_P3
COURSES.extend(_B_P3)
