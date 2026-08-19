# Phase 2 — Sales process in Zoho CRM (Free)

Configure this **after** Phase 1 is creating Leads from the website. No code changes. Free edition supports Convert, one standard Deal pipeline, 10 email templates, and 5 active workflow rules per module.

Student confirmation mail stays on **Brevo**. Templates below are for the **sales team** (or for sending one-to-one from the Lead record if your mailbox is connected later on Standard).

---

## 1. Lead statuses

**Setup → Customization → Modules and Fields → Leads → Lead Status.**

Use this order:

1. **Not Contacted** — website / WhatsApp / import default
2. **Contacted** — first call, WhatsApp, or email sent
3. **Qualified** — wants a course, dates, or corporate quote
4. **Lost Lead** — not proceeding (add a note with why)
5. **Junk Lead** — spam (optional; hide from list views)

**Converted** is set by Zoho when you click **Convert**. Do not treat Converted as a manual picklist step.

---

## 2. Convert Lead → Contact + Deal

When the person is ready to enrol (or a company is ready for a quote):

1. Open the Lead → **Convert**.
2. Create **Contact** (always).
3. Create **Account** if Corporate / group or HRD Corp (company name = Account). Individuals can skip Account or use a personal Account.
4. Create **Deal**:
   - Deal name: `{Course} — {First Last}` (or `{Company} — {Course}` for corporate)
   - Amount: quoted fee in MYR
   - Closing date: expected enrolment / invoice date
   - Stage: start at **Enquiry** (after you add the stages below)

---

## 3. Deal stages (training sales)

**Setup → Customization → Pipelines** (Free: one standard pipeline). Rename stages to:

1. **Enquiry** — just converted; still scoping
2. **Quoted** — price / dates / HRD Corp outline sent
3. **Invoice sent** — waiting for payment or PO
4. **Enrolled** — paid / confirmed seat
5. **Completed** — training delivered
6. **Closed Lost** — did not enrol

Probability is optional. Closed Lost should be a lost stage so reports stay honest.

---

## 4. Email templates (max 10 on Free)

**Setup → Email → Email Templates** (Leads / Contacts / Deals as needed). Suggested set:

1. First follow-up (individual) — course, next intake, ask for WhatsApp
2. First follow-up (corporate / group)
3. HRD Corp claim next steps
4. Pricing / payment options
5. Schedule / intake dates
6. Quote attached (after convert)
7. Invoice / payment reminder
8. Enrolment confirmation
9. Lost / not now (leave the door open)
10. Spare / workshop-event invite

Use merge fields: First Name, Last Name, Email. Course lives in **Description** on Free — copy from the Lead description when composing, or wait for Standard custom fields (`Course`).

Workflow alerts on Free can only email **CRM users**. Do not rely on Zoho to email the student automatically.

---

## 5. Four-hour follow-up (confirm Phase 0 workflow)

Re-open **Setup → Automation → Workflow Rules**.

- On Lead **create**, Task: `Follow up within 4 business hours`
- Owner: the user who owns website leads
- Optional second rule (still within 5 active rules/module): when Lead Status changes to **Contacted**, mark the follow-up task complete (or skip if you complete tasks by hand)

Business hours: **Setup → General → Company Settings → Business Hours** — Malaysia weekdays, e.g. 09:00–18:00 MYT.

---

## 6. Daily working order

1. Open list view **New website**.
2. Call or WhatsApp; log a **Call** or **Note**.
3. Set status to **Contacted** or **Qualified**.
4. Convert when they are a real opportunity; work the Deal stages.
5. Do not delete Leads — use **Lost Lead** / **Junk Lead**.

When this is in use for a week, run Phase 3 (sheet import) so history sits in the same pipeline.
