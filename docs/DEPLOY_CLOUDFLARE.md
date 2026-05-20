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
| `BREVO_INTERNAL_TO` or `BREVO_ENQUIRY_TO` | Internal enquiry inbox (comma-separated allowed; default fallback is `vaheed.2000@gmail.com`) |
| `BREVO_ENQUIRY_SECRET` | Must match `secret` in `js/enquiry-config.js` if you use server-side verification |
| `BREVO_ALLOWED_ORIGINS` | CORS origin(s); use `*` or your site origin |
| `APPS_SCRIPT_ENQUIRY_URL` | Optional; same Google Apps Script web app URL as in `enquiry-config.js` for sheet logging |
| `APPS_SCRIPT_ENQUIRY_SECRET` | Optional; aligns with Apps Script if used |
| `NEXPERTS_PUBLIC_SITE_URL` | Optional; reserved for other server logic (enquiry **email buttons** always use `https://www.nexpertsacademy.com` unless overridden below) |
| `NEXPERTS_EMAIL_SITE_URL` | Optional; override base URL for **all public links inside Brevo emails** (defaults to `https://www.nexpertsacademy.com` so preview/Netlify hosts never appear in student or lead mail) |
| `NEXPERTS_LEADS_SHEET_URL` | Optional; sheet URL shown in internal emails |
| `ADMIN_USER` | **Same username** you use to sign in at `/admin/` (e.g. `admin`) — set for **Production** (and Preview if you use preview URLs) |
| `ADMIN_PASS` | **Same password** you use to sign in at `/admin/` (e.g. `123`) — mark **Encrypted** |

Mark secrets **Encrypted** in the dashboard. After changing these values, **redeploy** so Functions see the new credentials. If they are missing, the API falls back to `admin` / `123`.

### KV for admin course publish (required for **Publish live**)

Admin **Publish live** stores overrides in **Cloudflare KV**, not Netlify Blobs.

This repo’s **`wrangler.toml`** includes `pages_build_output_dir`, so Cloudflare treats that file as the **source of truth** for bindings. You will see *“Bindings for this project are being managed through wrangler.toml”* in the dashboard — that is expected; configure KV in the file, not under Settings → Functions.

1. **Workers & Pages** → **KV** → **Create namespace** (e.g. `nexperts-course-overrides`).
2. Open the namespace and copy its **Namespace ID** (a long hex string).
3. In this repo, edit **`wrangler.toml`** — set `id` under `[[kv_namespaces]]` (binding name must stay **`COURSE_OVERRIDES`**):

```toml
[[kv_namespaces]]
binding = "COURSE_OVERRIDES"
id = "paste-your-namespace-id-here"
```

4. Commit, push, and wait for the Pages deploy to finish.

Optional (CLI, with Wrangler logged in): `npx wrangler kv namespace create nexperts-course-overrides` — use the printed `id` in `wrangler.toml`.

Without a valid KV `id`, **Publish live** returns **503**. You can still **Export** JSON, commit `data/course-overrides.json`, and redeploy (build bakes HTML + overlay reads the static file).

6. Save and deploy. The first build runs after you confirm.

## 3. Python version (optional)

The build runs Python scripts (`scripts/build_contact_course_select.py`, `scripts/inject_ga4.py`). The repo includes **`.python-version`** (`3.11`) so compatible Cloudflare build images can pick a consistent Python. If the build cannot find `python`, set **Environment variable** `PYTHON_VERSION` to `3.11` in the Pages project (see Cloudflare docs for the current variable name and supported versions).

## 4. Redirects

Canonical public course URLs use **`/courses/{slug}`** (pretty path). The **`_redirects`** file maps each slug to `courses/{slug}.html` with a **200** rewrite, adds **301** chains from legacy Wix paths and old `/course_pages/*.html` links to `/courses/*`, and handles static pages. Cloudflare Pages parses **`_redirects`** from the build output (same filename as Netlify, but not identical behaviour):

- **Relative paths only** for rules in this file; **no** full URLs on the source side like Netlify allows for apex redirects.
- **Status codes** must be bare `301`, `302`, etc. Netlify’s **`301!` (forced)** syntax is **invalid** on Pages (drop the `!`).
- **Domain-level redirects** (different hostname / `https://…/* …`) are **not supported** in `_redirects` — use **Rules → Redirect Rules** (or **Bulk Redirects**) on your Cloudflare **zone** for apex → `www`, HTTP → HTTPS, etc., plus **SSL/TLS → Always Use HTTPS**.
- **Limits:** up to **2,000 static** and **100 dynamic** redirects (splats / placeholders count as dynamic). A few bad splat lines can exhaust the dynamic budget and cause Pages to **skip the rest of the file**; fix deploy log warnings so every legacy path rule applies.

After deploy, confirm the build log shows **no** “Skipping remaining … lines” and spot-check sample legacy URLs.

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

## 8. Admin course publish (`/api/course-overrides`)

- **Cloudflare Pages:** `functions/api/course-overrides.mjs` → **`/api/course-overrides`**
- **Netlify** (if used): `netlify/functions/course-overrides.mjs` → `/.netlify/functions/course-overrides`

The public site (`admin/overlay.js`) calls **`/api/course-overrides`** on your domain (not Netlify paths).

After **Publish live** in `/admin/`:

1. Data is saved to KV (`COURSE_OVERRIDES`).
2. All visitors load overrides via the API + `data/course-overrides.json` fallback.

## 9. Keeping Brevo logic in sync

Server-side Brevo logic exists in two places so each platform can bundle it:

- `netlify/functions/enquiry-brevo.mjs` (Netlify)
- `functions/api/enquiry-brevo-core.mjs` (Cloudflare Pages)

When you change email templates or Brevo behaviour, update **both** files (or extract a shared module later).

Course overrides shared logic: `functions/api/course-overrides-core.mjs` (used by Cloudflare; Netlify function is a separate copy with Blobs).
