# Deploy on Cloudflare Pages

This site is static HTML at the repository root, with a **Pages Function** at `/api/enquiry-brevo` for Brevo email (same behaviour as the Netlify function).

## 1. Prerequisites

- Cloudflare account
- GitHub repository connected (this repo)
- Brevo API + sender email (same as for Netlify)

## 2. Create a Pages project

1. Log in to the [Cloudflare dashboard](https://dash.cloudflare.com/).
2. Go to **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
3. Select your Git provider, then the **Nexperts Website** repository.
4. Configure the build:

| Setting | Value |
|--------|--------|
| **Framework preset** | None |
| **Build command** | `npm run build` |
| **Build output directory** | `/` (root of the repo after build) |
| **Root directory** | `/` (leave default unless the repo is a monorepo) |

5. **Environment variables** (Production + Preview as needed) — mirror what you use on Netlify:

| Variable | Purpose |
|----------|---------|
| `BREVO_API_KEY` | Brevo API key |
| `BREVO_SENDER_EMAIL` | Verified sender address |
| `BREVO_SENDER_NAME` | Display name (optional) |
| `BREVO_INTERNAL_TO` or `BREVO_ENQUIRY_TO` | Internal enquiry inbox (comma-separated allowed) |
| `BREVO_ENQUIRY_SECRET` | Must match `secret` in `js/enquiry-config.js` if you use server-side verification |
| `BREVO_ALLOWED_ORIGINS` | CORS origin(s); use `*` or your site origin |
| `APPS_SCRIPT_ENQUIRY_URL` | Optional; same Google Apps Script web app URL as in `enquiry-config.js` for sheet logging |
| `APPS_SCRIPT_ENQUIRY_SECRET` | Optional; aligns with Apps Script if used |
| `NEXPERTS_PUBLIC_SITE_URL` | Optional; public site URL for email links |
| `NEXPERTS_LEADS_SHEET_URL` | Optional; sheet URL shown in internal emails |

Mark secrets **Encrypted** in the dashboard.

6. Save and deploy. The first build runs after you confirm.

## 3. Python version (optional)

The build runs Python scripts (`scripts/build_contact_course_select.py`, `scripts/inject_ga4.py`). The repo includes **`.python-version`** (`3.11`) so compatible Cloudflare build images can pick a consistent Python. If the build cannot find `python`, set **Environment variable** `PYTHON_VERSION` to `3.11` in the Pages project (see Cloudflare docs for the current variable name and supported versions).

## 4. Redirects

The site ships a root **`_redirects`** file (same idea as Netlify). Cloudflare Pages serves it from the **published output** when placed at the site root. After deploy, spot-check a few legacy paths from that file.

## 5. Enquiry endpoint (Brevo)

- **Cloudflare Pages** (including custom domains): the browser uses **`/api/enquiry-brevo`** by default (see `js/enquiry-submit.js`).
- **Netlify** `*.netlify.app`: the default remains **`/.netlify/functions/enquiry-brevo`**.
- If you still use **Netlify with a custom domain** (not `*.netlify.app`), set explicitly in `js/enquiry-config.js`:

```js
brevoEndpoint: "/.netlify/functions/enquiry-brevo",
```

## 6. Custom domain

In the Pages project → **Custom domains**, attach `www.nexpertsacademy.com` (or your host). Follow Cloudflare DNS prompts. HTTPS is automatic on Cloudflare.

## 7. Local checks (optional)

With [Wrangler](https://developers.cloudflare.com/workers/wrangler/install-and-update/) installed:

```bash
npx wrangler pages dev . -- npm run build
```

Or build first, then run `wrangler pages dev` against the built tree per Wrangler docs.

## 8. Keeping Brevo logic in sync

Server-side Brevo logic exists in two places so each platform can bundle it:

- `netlify/functions/enquiry-brevo.mjs` (Netlify)
- `functions/api/enquiry-brevo-core.mjs` (Cloudflare Pages)

When you change email templates or Brevo behaviour, update **both** files (or extract a shared module later).
