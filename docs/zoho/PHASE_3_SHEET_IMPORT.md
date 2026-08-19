# Phase 3 — Import Google Sheet enquiries into Zoho (Free cap)

Do this **after** Phase 1 has been live for a few days so new website rows are already in Zoho. Importing first would duplicate whatever the API already upserted (same email = one Lead if you choose **update duplicates**).

Free limits that matter:

- **5,000 records** in the whole org (Leads + Contacts + Deals + …)
- **1,000 rows per import batch**
- Default script cap: **4,000 unique emails** so live upserts still have room

Keep the Google Sheet as the full archive. Import only recent / still-workable leads.

---

## 1. Export the sheet

1. Open the Enquiries spreadsheet (same ID as in Apps Script / `NEXPERTS_LEADS_SHEET_URL`).
2. **File → Download → Comma Separated Values (.csv)** of the **Enquiries** tab.
3. Save locally, e.g. `Enquiries.csv`. Expected headers:

   `Submitted At (ISO)`, `Source`, `Page URL`, `First`, `Last`, `Email`, `Phone`, `Office`, `Course`, `Type`, `Message`, `User Agent`

---

## 2. Convert to Zoho import CSV

From the repo root:

```bash
python scripts/zoho_sheet_to_leads_csv.py Enquiries.csv --since 2025-01-01 --limit 4000
```

This writes `Enquiries-zoho-leads.csv` with Zoho display-name headers. Behaviour:

- Drops rows without a valid email
- Keeps the **latest** row per email
- Maps Source / Type the same way as the website API
- Sets Lead Source to `Google Sheet Import` when the sheet source is not a website form
- Puts course, office, message, and URL into **Description** (Free has no custom fields)

If the output has more than 1,000 rows, split it (Excel, or any CSV splitter) into batches of 1,000.

---

## 3. Import in Zoho

1. **Leads → Import**.
2. Upload a 1,000-row file (UTF-8).
3. Map:

   | CSV column | Zoho field |
   |------------|------------|
   | First Name | First Name |
   | Last Name | Last Name |
   | Email | Email |
   | Phone | Phone |
   | Mobile | Mobile |
   | Company | Company (preferred office) |
   | Website | Website |
   | Lead Source | Lead Source |
   | Industry | Industry |
   | Lead Status | Lead Status |
   | Description | Description |

4. Duplicate handling: **Skip** or **Overwrite** by Email so you do not clone Phase 1 website leads.
5. Repeat for each batch. Watch the org record count (Setup → Data Administration / storage).

---

## 4. After import

- Open the **Google Sheet Import** Lead Source filter (or add a list view if you still have a Free slot).
- Do not re-import the same months. New enquiries continue via `/api/enquiry-brevo`.
- Leave the sheet running until Phase 4 (retire only after the team lives in Zoho).
