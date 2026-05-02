# Website enquiries → Google Sheet (Apps Script)

This folder contains **Google Apps Script** bound to your **Google Sheet**. The current `EnquiryWebhook.gs` **only appends a row** for each POST — it does **not** send email. Use **Brevo + Netlify** (below) for student and team emails.

## What the Apps Script does

1. Accepts `POST` with the same JSON payload as the website (`first`, `last`, `email`, …).
2. Optionally checks `ENQUIRY_SECRET` (must match `secret` in `js/enquiry-config.js` if set).
3. **Appends one row** to the **`Enquiries`** sheet.

## One-time setup

1. Open the **Google Sheet** that should store leads (or create a new one).
2. **Extensions → Apps Script** → paste **`EnquiryWebhook.gs`** (project must stay **bound** to that spreadsheet).
3. Run **`setupSheetHeaders`** once → **Run** → approve permissions (creates/clears the `Enquiries` tab and headers).
4. *(Recommended)* **Project Settings → Script properties** → add:
   - `ENQUIRY_SECRET` = a long random string (same value as `secret` in `js/enquiry-config.js` if the site POSTs to this web app).
5. **Deploy → New deployment** → **Web app**
   - **Execute as:** *Me*
   - **Who has access:** *Anyone*
6. Copy the **Web App URL** into `js/enquiry-config.js` → `webAppUrl` **only if** you set `provider: "apps_script"` to log rows via Google (see note below).

## Testing the sheet

- In the script editor, run **`testAppendSampleRow`** once, then open the **`Enquiries`** tab — you should see a sample row.
- Or POST from the site with `provider: "apps_script"` and a valid `webAppUrl`, then confirm a new row appears.

## Security (practical)

- **Set `ENQUIRY_SECRET`** in production; same value as `secret` in `js/enquiry-config.js` when using this web app.
- Apps Script has execution time and URL fetch quotas; sheet-only usage is light.

### Using Brevo for email and Apps Script for the sheet

The website **`js/enquiry-submit.js`** currently sends to **one** `provider` (`brevo` **or** `apps_script`). To **both** email via Brevo and log to Sheets, either: extend the Netlify function to `UrlFetchApp`-equivalent server-side POST to the Apps Script URL after a successful Brevo send, or add a second client call (ask if you want that implemented).

---

## Alternative: Brevo (transactional email via Netlify)

If **Google / Apps Script mail is not reaching inboxes** (spam, Workspace routing, or group rules), use **Brevo** instead. The browser calls a **Netlify serverless function**, which sends two emails through Brevo’s API (same content as this script: student acknowledgement + internal lead to `enquiry@nexpertsacademy.com`).

### What you need to provide

1. **Brevo account** — [brevo.com](https://www.brevo.com/) (free tier includes transactional sends).
2. **Brevo SMTP API key** — Dashboard → SMTP & API → API keys → create a key with permission to send transactional emails.
3. **A verified sender in Brevo** — Domains & senders → add and verify the domain (or verify a single sender email). You will send **from** this address (e.g. `noreply@yourdomain.com` or a verified mailbox).
4. **Netlify** — Site must be deployed on Netlify (same site that serves `/.netlify/functions/enquiry-brevo`).

### Netlify environment variables

In **Site configuration → Environment variables**, add:

| Variable | Required | Description |
|----------|----------|-------------|
| `BREVO_API_KEY` | Yes | Your Brevo API key (never put this in the frontend). |
| `BREVO_SENDER_EMAIL` | Yes | Verified sender email in Brevo. |
| `BREVO_SENDER_NAME` | No | Display name (default: `Nexperts Academy`). |
| `BREVO_INTERNAL_TO` | No | Inbox for lead notifications (reply-to on student mail + internal `to`). Same value as `teamInbox` in `js/enquiry-config.js`. **Aliases:** `BREVO_ENQUIRY_TO`, `NEXPERTS_ENQUIRY_EMAIL`, `ENQUIRY_EMAIL` (first non-empty wins). **Multiple:** comma- or semicolon-separated list. |
| `BREVO_ENQUIRY_SECRET` | Recommended | Same string as `secret` in `js/enquiry-config.js` to block random POSTs. |
| `BREVO_ALLOWED_ORIGINS` | No | CORS `Access-Control-Allow-Origin` (default `*`). Set to your site origin if you lock it down. |
| `NEXPERTS_PUBLIC_SITE_URL` | No | Base URL for CTA links in emails (default `https://www.nexpertsacademy.com`). |
| `NEXPERTS_LEADS_SHEET_URL` | No | Google Sheet link shown on the internal lead email (defaults to your shared Enquiries sheet). |

Redeploy the site after changing env vars.

### Frontend config (`js/enquiry-config.js`)

```js
window.NEXPERTS_ENQUIRY_CONFIG = {
  provider: "brevo",
  brevoEndpoint: "/.netlify/functions/enquiry-brevo",
  secret: "same-as-BREVO_ENQUIRY_SECRET",
  webAppUrl: "", // not used when provider is brevo
};
```

For local testing with `netlify dev`, the function URL is the same path on `http://localhost:8888` (or whatever port Netlify prints).

### Local machine (`netlify dev`)

1. Copy `.env.example` → `.env` and fill `BREVO_API_KEY`, `BREVO_SENDER_EMAIL` (must be **verified** in Brevo for your domain, e.g. `noreply@nexpertsai.com`), and optionally `BREVO_INTERNAL_TO` (default `enquiry@nexpertsacademy.com`). The file `.env` is **gitignored** — do not commit it.
2. In `js/enquiry-config.js` set `provider: "brevo"`.
3. From the repo root: `npm install` then `npm run dev` (or `npx netlify dev` if you prefer not to install deps).
4. Open the URL Netlify prints (often `http://localhost:8888`) and submit **contact.html** or the home “Enquire” modal. Watch the terminal for function logs if something fails.

### Files involved

- `netlify/functions/enquiry-brevo.mjs` — handler that calls `https://api.brevo.com/v3/smtp/email` twice.
- `netlify.toml` — sets `functions` directory and `publish = "."` (adjust if your publish directory differs).
- `js/enquiry-submit.js` — chooses Apps Script vs Brevo from `provider`.
