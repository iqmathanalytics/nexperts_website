# Zoho Free — email templates implementation report

Date: 2026-08-20  
Edition: **Zoho CRM Free**  
Requirements: [`docs/updates_on_p2.txt`](../updates_on_p2.txt)  
Code: [`functions/api/zoho-crm.mjs`](../../functions/api/zoho-crm.mjs)

This report matches deliverable §26 A–M. Items that require Zoho UI or live send are marked **You verify**.

---

## A. Existing fields reused

| Zoho Lead field | Used for |
|-----------------|----------|
| First Name | Template greeting |
| Last Name | Record identity |
| Email | Upsert + send |
| Phone / Mobile | Contact |
| Company | **Interested course** (website `course`) |
| Website | Page URL |
| Lead Source | Website - Contact / Homepage / Course |
| Industry | Enquiry type (Individual, Corporate, HRD Corp, …) |
| Description | Full enquiry (course, office, message, URLs, timestamp) |
| Lead Status | Lifecycle / Lost not now |
| Lead Owner | Where Insert Fields allows it |

---

## B. New Zoho fields created

**None.** Free edition does not support custom fields. No Quotes/Invoices/Courses/Events modules created.

---

## C. Exact Zoho field labels (Free standard)

First Name, Last Name, Email, Phone, Mobile, Company, Website, Lead Source, Industry, Description, Lead Status, Lead Owner (as shown in Zoho UI).

---

## D. Exact Zoho API names (website mapper)

`First_Name`, `Last_Name`, `Email`, `Phone`, `Mobile`, `Company`, `Website`, `Lead_Source`, `Industry`, `Description`, `Lead_Status`

Dormant Standard path (not enabled): `Course`, `Enquiry_Type`, `Preferred_Office`, `Page_URL`, `Form_Source` via `ZOHO_USE_CUSTOM_FIELDS=1`.

---

## E. Which email template uses which fields

See [TEMPLATE_FIELD_MAP.md](TEMPLATE_FIELD_MAP.md) for the full matrix.

Summary:

| Template | Dynamic (Free) | Manual / Deferred |
|----------|----------------|-------------------|
| 1 First follow-up individual | First Name, Company, Description | Fee/dates if present |
| 2 First follow-up corporate group | First Name, Company, Description, Industry | Participants, dates, mode, location, true company name |
| 3 HRD Corp claim next steps | First Name, Company, Industry | Reg no, employee count, HRD account, fee, status |
| 4 Pricing payment options | First Name, Company, Industry | Fee, duration, mode, intake, payment link |
| 5 Schedule intake dates | First Name, Company | All schedule fields |
| 6 Quote attached | First Name, Company | Quote #/date/total/validity/link + PDF attach |
| 7 Invoice payment reminder | First Name, Company | Invoice/payment fields; paid guard = checklist |
| 8 Enrolment confirmation | First Name, Company | Dates, mode, location, joining link, status |
| 9 Lost not now | First Name, Company, Lead Status, Lead Owner | Future follow-up date |
| 10 Workshop event invite | First Name | All event fields |

---

## F. Fields still manual

All `[AMOUNT]`, `[DATE]`, `[PAYMENT LINK]`, quote/invoice/event placeholders, HRD registration details, participants, training mode/location/time unless typed into Description before send. See placeholder table in TEMPLATE_FIELD_MAP.

---

## G. Fields dynamically populated (from website)

First Name, Last Name, Email, Phone, Company (course), Website, Lead Source, Industry, Description (includes message + office + course + URLs), Lead Status (default Not Contacted).

---

## H. Automations added

**None** for the 10 templates.

Kept existing: new Lead → Task “Follow up within 4 business hours” (Phase 0/2).

---

## I. Automations intentionally NOT added

- Auto first follow-up email to lead  
- Quote sent → quote email  
- Invoice overdue → payment reminder  
- Payment confirmed → enrolment confirmation  
- Workshop campaign auto-invite  
- Deluge “required field” send blockers  

Reason: Free cannot custom-field the data, cannot host Quotes/Invoices, and workflow email to leads is not reliable/allowed like paid editions.

---

## J. Test results for all 10 templates

### Code / mapping tests (automated in repo)

| Check | Result |
|-------|--------|
| Course → Company (alone) | Pass — `mapCompanyListField` |
| Message → Description | Pass — `buildDescription` |
| Industry mapping | Pass — `mapIndustry` |
| Lead Source mapping | Pass — `mapLeadSource` |
| `ZOHO_USE_CUSTOM_FIELDS` default off | Pass |

### Zoho UI / send tests (**You verify** after TEMPLATE_EDIT_GUIDE)

Create a test Lead:

- First Name: `Aisha`  
- Company: `Certified Ethical Hacker (CEH)`  
- Industry: `Individual enrolment`  
- Description: paste a sample enquiry block  
- Email: your inbox  

| # | Template | Preview First Name | Preview Company | No fake merges | Manual placeholders OK | Desktop | Mobile | Notes |
|---|----------|--------------------|-----------------|----------------|------------------------|---------|--------|-------|
| 1 | First follow-up individual | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 2 | First follow-up corporate group | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 3 | HRD Corp claim next steps | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 4 | Pricing payment options | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 5 | Schedule intake dates | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 6 | Quote attached | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | Attach PDF |
| 7 | Invoice payment reminder | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | Skip if paid |
| 8 | Enrolment confirmation | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 9 | Lost not now | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |
| 10 | Workshop event invite | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | |

Missing-data check: if Company empty, email must not show `null`/`undefined` — Free merge shows blank; do not invent fee merges.

---

## K. Zoho CRM configuration you still need to perform manually

1. Follow [TEMPLATE_EDIT_GUIDE.md](TEMPLATE_EDIT_GUIDE.md) — replace `[COURSE NAME]` with Company merge on all templates; keep other placeholders Manual.  
2. Use [TEMPLATE_SEND_CHECKLIST.md](TEMPLATE_SEND_CHECKLIST.md) for every send.  
3. Complete section J checklist above.  
4. Ensure Lead Source / Industry picklists match Phase 0 (already done if Phase 2 complete).

---

## L. Credentials / API configuration required

Already required for website → Zoho (Phase 1):

- `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`  
- Optional: `ZOHO_ACCOUNTS_URL`, `ZOHO_API_DOMAIN`  

**Do not** set `ZOHO_USE_CUSTOM_FIELDS=1` until Standard fields exist.

No new credentials for Free template sends (salesperson uses Zoho login).

---

## M. Limitations caused by Zoho CRM Free

- Zero custom fields → most template data stays Manual.  
- No Quotes / Invoices / Products → templates 6–7 cannot be module-driven.  
- No custom Courses/Events modules → no CRM source of truth for intakes/events.  
- Workflow emails to leads not available like paid plans → no safe auto-send of the 10 templates.  
- No Deluge Functions → no programmatic send guards (paid status, missing PDF).  
- Email integration / logging limited vs Standard.  
- 5,000 records / 3 users / 10 email templates cap.  
- Company field doubles as “course” for merges (true company name for corporate leads may need manual edit on the Lead before send).

When you upgrade, reopen [PHASE_4_HARDEN.md](PHASE_4_HARDEN.md) and re-map templates to custom fields / Quotes / Invoices.
