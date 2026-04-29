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
