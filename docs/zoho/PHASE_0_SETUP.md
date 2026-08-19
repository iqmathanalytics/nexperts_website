# Phase 0 — Zoho CRM Free org setup

Do this **in the Zoho UI** before Cloudflare env vars are set. Website forms do not change. The API integration (Phase 1) will not create Leads until a refresh token exists.

Sign up: [Zoho CRM Free](https://www.zoho.com/crm/signup.html?plan=free) (3 users, forever free).

Malaysia orgs usually use the **zoho.com** data centre (`accounts.zoho.com` + `www.zohoapis.com`). If the signup URL is `zoho.in`, `zoho.eu`, or `zoho.com.au`, note that — the website env must match.

---

## 1. Organisation and users

1. Organisation name: **Nexperts Academy Sdn Bhd**.
2. Time zone: **Asia/Kuala_Lumpur** (Albany follow-ups are still logged in KL time unless you split owners later).
3. Currency: **MYR**.
4. Invite at most **2 more users** (Free cap is 3 including you).
5. Confirm everyone can open **Leads**.

---

## 2. Lead Source picklist

**Setup → Customization → Modules and Fields → Leads → Lead Source** (or open a Lead layout and edit the Lead Source field).

Add these values (exact spelling — the website API sends these):

- `Website - Contact`
- `Website - Homepage`
- `Website - Course`
- `Website` (fallback)
- `WhatsApp`
- `Google Sheet Import`

Keep Zoho’s built-in **Web Research** (used as a last-resort API fallback if a custom value is missing).

---

## 3. Industry picklist (enquiry type)

Free edition has **no custom fields**, so enquiry type is stored on **Industry**.

Add these values (exact spelling):

- `Individual enrolment`
- `Corporate / group training`
- `HRD Corp`
- `Schedule / intake`
- `Pricing`
- `Eligibility`
- `Other`

You can hide unused default industries (Apparel, Banking, …) from the picklist so the team only sees Nexperts types.

---

## 4. Lead Status

Keep or restore the standard values used in Phase 2:

- `Not Contacted` — default for new website leads (API sets this)
- `Contacted`
- `Qualified`
- `Lost Lead`

Converted is applied automatically when you use **Convert**.

---

## 5. Custom list views (5 per module on Free)

**Leads → Create View**. Suggested filters:

| View name | Criteria |
|-----------|----------|
| New website | Lead Status is Not Contacted **and** Lead Source contains Website |
| Corporate / group | Industry is Corporate / group training |
| HRD Corp | Industry is HRD Corp |
| Course-page leads | Lead Source is Website - Course |
| WhatsApp | Lead Source is WhatsApp |

---

## 5b. Leads list columns (course + message)

On **Free**, there are no custom fields and **Designation** is often hidden from the Leads list. Use columns you already have:

| Zoho column | Shows in the list |
|-------------|-------------------|
| **Company** | `Course · message` (e.g. `Certified Ethical Hacker (CEH) · Need March intake…`). Course only, message only, or office if both are empty. |
| **Description** | Full enquiry (office, page URL, complete message). Add this column for long messages. |
| **Industry** | Enquiry type (Individual, Corporate, HRD Corp, …) |

**List view setup:**

1. Open **Leads**.
2. **Customize columns** → ensure **Company** and **Industry** are visible.
3. Optional: add **Description** for the full message when Company truncates it.
4. Save the view.

You do **not** need Designation. Read **Company** as course + short message in one cell.

---

## 6. Follow-up workflow (4 business hours)

**Setup → Automation → Workflow Rules → Create Rule** → module **Leads**.

- **When:** Record action → **Create**
- **Condition:** Lead Source contains `Website` (optional; skip the condition to cover WhatsApp too)
- **Instant action → Task:**
  - Subject: `Follow up within 4 business hours`
  - Due date: **Same day** (or 1 day if you prefer)
  - Status: Not Started
  - Assigned to: record owner (the CRM user who owns new website leads)

Free workflow emails can only go to **CRM users**, not the student. Student + `enquiry@` mail stay on **Brevo**.

---

## 7. API Self Client + refresh token

Tokens must **never** go in `js/enquiry-config.js` (that file is public).

1. Open [Zoho API Console](https://api-console.zoho.com/).
2. **Add Client** → **Self Client**.
3. **Generate Code**:
   - Scope (space-separated or one per line, as the console requires):

     ```
     ZohoCRM.modules.leads.CREATE
     ZohoCRM.modules.leads.READ
     ZohoCRM.modules.leads.UPDATE
     ```

   - Time duration: 10 minutes
   - Scope description: `Nexperts website enquiries`
4. Copy the **grant token** immediately (it expires).
5. From the repo root, with the grant token and client id/secret:

   ```bash
   set ZOHO_CLIENT_ID=your_client_id
   set ZOHO_CLIENT_SECRET=your_client_secret
   set ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
   node scripts/zoho_exchange_grant.mjs YOUR_GRANT_TOKEN
   ```

   On PowerShell:

   ```powershell
   $env:ZOHO_CLIENT_ID="your_client_id"
   $env:ZOHO_CLIENT_SECRET="your_client_secret"
   $env:ZOHO_ACCOUNTS_URL="https://accounts.zoho.com"
   node scripts/zoho_exchange_grant.mjs YOUR_GRANT_TOKEN
   ```

6. Save the printed **refresh token**. It does not expire unless you revoke it.
7. After Phase 1 is deployed, paste into Cloudflare Pages (encrypted):

   | Variable | Value |
   |----------|--------|
   | `ZOHO_CLIENT_ID` | Self Client ID |
   | `ZOHO_CLIENT_SECRET` | Self Client secret |
   | `ZOHO_REFRESH_TOKEN` | Refresh token from step 6 |
   | `ZOHO_ACCOUNTS_URL` | `https://accounts.zoho.com` (or `.in` / `.eu` / `.com.au`) |
   | `ZOHO_API_DOMAIN` | `https://www.zohoapis.com` (or `zohoapis.in` / `.eu` / `.com.au`) |

8. **Redeploy** Pages so Functions pick up the secrets.

Other data centres:

| Accounts host | API host |
|---------------|----------|
| `https://accounts.zoho.com` | `https://www.zohoapis.com` |
| `https://accounts.zoho.in` | `https://www.zohoapis.in` |
| `https://accounts.zoho.eu` | `https://www.zohoapis.eu` |
| `https://accounts.zoho.com.au` | `https://www.zohoapis.com.au` |

---

## 8. Smoke-check before calling the site done

- [ ] Three users max; all can see Leads
- [ ] Lead Source + Industry values match the lists above
- [ ] New-lead workflow creates a follow-up task
- [ ] Refresh token generated and stored only in Cloudflare (or local `.env`), not in git

When this list is done, Phase 1 can create Leads from the live enquiry forms.
