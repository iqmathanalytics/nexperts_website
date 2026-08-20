/**
 * Website enquiry → Zoho CRM Leads (upsert by Email).
 * Used by enquiry-brevo-core.mjs (Cloudflare Pages + Netlify).
 *
 * Skips when ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET / ZOHO_REFRESH_TOKEN are missing
 * so local/dev still works. Failures must not fail the enquiry HTTP 200.
 *
 * Free edition: no custom fields — extra data goes in Description + standard
 * Lead_Source / Industry / Company / Website. Set ZOHO_USE_CUSTOM_FIELDS=1
 * after upgrading to Standard and creating the API names in Zoho.
 */

const DEFAULT_ACCOUNTS_URL = "https://accounts.zoho.com";
const DEFAULT_API_DOMAIN = "https://www.zohoapis.com";
const DEFAULT_API_VERSION = "v8";

const SOURCE_TO_LEAD_SOURCE = {
  contact_page: "Website - Contact",
  landing_modal: "Website - Homepage",
  course_sidebar: "Website - Course",
};

const PICKLIST_FIELDS = ["Lead_Source", "Industry", "Lead_Status"];

let tokenCache = { access: "", expiresAt: 0 };

function envStr(env, key, fallback = "") {
  const v = String((env && env[key]) || "").trim();
  return v || fallback;
}

export function isZohoConfigured(env) {
  const e = env || process.env || {};
  return Boolean(
    envStr(e, "ZOHO_CLIENT_ID") &&
      envStr(e, "ZOHO_CLIENT_SECRET") &&
      envStr(e, "ZOHO_REFRESH_TOKEN"),
  );
}

export function mapLeadSource(source) {
  const s = String(source || "").trim();
  return SOURCE_TO_LEAD_SOURCE[s] || "Website";
}

/** Map form enquiry type → Industry picklist (Phase 0 values). */
export function mapIndustry(type) {
  const t = String(type || "").trim();
  if (!t) return "";
  if (/corporate/i.test(t)) return "Corporate / group training";
  if (/hrd/i.test(t)) return "HRD Corp";
  if (/schedule|intake/i.test(t)) return "Schedule / intake";
  if (/pricing|payment/i.test(t)) return "Pricing";
  if (/eligib/i.test(t)) return "Eligibility";
  if (/^other$/i.test(t)) return "Other";
  if (/individual/i.test(t)) return "Individual enrolment";
  return t.slice(0, 120);
}

export function useCustomFields(env) {
  const v = envStr(env, "ZOHO_USE_CUSTOM_FIELDS").toLowerCase();
  return v === "1" || v === "true" || v === "yes";
}

function truncateField(value, max) {
  const s = String(value || "").trim();
  if (!s) return "";
  if (s.length <= max) return s;
  return `${s.slice(0, Math.max(0, max - 1))}…`;
}

function buildDescription(data) {
  const course = String((data && data.course) || "").trim();
  const message = String((data && data.message) || "").trim();
  const lines = [
    "Website enquiry",
    `Course: ${course || "—"}`,
    `Enquiry type: ${data.type || "—"}`,
    `Preferred office: ${data.office || "—"}`,
    `Source: ${data.source || "—"}`,
    `Page: ${data.pageUrl || "—"}`,
    `Curriculum: ${data.curriculumPage || "—"}`,
    `Submitted: ${data.submittedAt || "—"}`,
    "",
    "Message:",
    message || "—",
  ];
  return lines.join("\n").slice(0, 30000);
}

/** Free edition: Company shows course for list + email merges; message stays in Description. */
export function mapCompanyListField(data) {
  const course = String((data && data.course) || "").trim();
  const office = String((data && data.office) || "").trim();
  const message = String((data && data.message) || "").trim();

  // Prefer course alone so ${Leads.Company} is a clean course name in email templates.
  if (course) return truncateField(course, 200);
  if (message) return truncateField(message, 200);
  return truncateField(office, 200);
}

function dropEmpty(record) {
  const out = { ...record };
  for (const [k, v] of Object.entries(out)) {
    if (k === "Last_Name") continue;
    if (v == null || String(v).trim() === "") delete out[k];
  }
  return out;
}

/**
 * Map the website enquiry payload to a Zoho Lead record (API names).
 */
export function mapEnquiryToLead(data, env) {
  const e = env || process.env || {};
  const first = String((data && data.first) || "").trim();
  const last = String((data && data.last) || "").trim() || "Unknown";
  const email = String((data && data.email) || "").trim();
  const phone = String((data && data.phone) || "").trim();
  const office = String((data && data.office) || "").trim();
  const pageUrl = String((data && data.pageUrl) || "").trim();
  const industry = mapIndustry(data && data.type);

  const record = {
    First_Name: first.slice(0, 40),
    Last_Name: last.slice(0, 80),
    Email: email,
    Phone: phone,
    Mobile: phone,
    Company: mapCompanyListField(data),
    Website: pageUrl.slice(0, 255),
    Lead_Source: mapLeadSource(data && data.source),
    Lead_Status: envStr(e, "ZOHO_LEAD_STATUS", "Not Contacted"),
    Description: buildDescription(data || {}),
  };

  if (industry) record.Industry = industry;

  if (useCustomFields(e)) {
    const courseApi = envStr(e, "ZOHO_FIELD_COURSE", "Course");
    const typeApi = envStr(e, "ZOHO_FIELD_ENQUIRY_TYPE", "Enquiry_Type");
    const officeApi = envStr(e, "ZOHO_FIELD_OFFICE", "Preferred_Office");
    const pageApi = envStr(e, "ZOHO_FIELD_PAGE_URL", "Page_URL");
    const sourceApi = envStr(e, "ZOHO_FIELD_FORM_SOURCE", "Form_Source");
    const course = String((data && data.course) || "").trim();
    const type = String((data && data.type) || "").trim();
    const source = String((data && data.source) || "").trim();
    if (course) record[courseApi] = course.slice(0, 255);
    if (type) record[typeApi] = type.slice(0, 255);
    if (office) record[officeApi] = office.slice(0, 255);
    if (pageUrl) record[pageApi] = pageUrl.slice(0, 255);
    if (source) record[sourceApi] = source.slice(0, 120);
  }

  return dropEmpty(record);
}

async function parseJsonResponse(res) {
  const text = await res.text();
  let json = null;
  try {
    json = text ? JSON.parse(text) : null;
  } catch {
    json = { message: text };
  }
  return { json, text };
}

export async function refreshAccessToken(env) {
  const e = env || process.env || {};
  const now = Date.now();
  if (tokenCache.access && now < tokenCache.expiresAt - 60_000) {
    return tokenCache.access;
  }

  const accounts = envStr(e, "ZOHO_ACCOUNTS_URL", DEFAULT_ACCOUNTS_URL).replace(/\/$/, "");
  const body = new URLSearchParams({
    refresh_token: envStr(e, "ZOHO_REFRESH_TOKEN"),
    client_id: envStr(e, "ZOHO_CLIENT_ID"),
    client_secret: envStr(e, "ZOHO_CLIENT_SECRET"),
    grant_type: "refresh_token",
  });

  const res = await fetch(`${accounts}/oauth/v2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  const { json, text } = await parseJsonResponse(res);
  const access = json && json.access_token;
  if (!access) {
    const msg =
      (json && (json.error_description || json.error || json.message)) ||
      text.slice(0, 180) ||
      "zoho_token_failed";
    throw new Error(String(msg).slice(0, 200));
  }
  const ttlMs = Number(json.expires_in || 3600) * 1000;
  tokenCache = { access, expiresAt: Date.now() + (Number.isFinite(ttlMs) ? ttlMs : 3600_000) };
  return access;
}

function invalidApiNameFromZoho(row) {
  const details = row && row.details;
  if (!details) return "";
  if (typeof details.api_name === "string") return details.api_name;
  if (typeof details.json_path === "string") {
    const m = details.json_path.match(/\$\.data\[0\]\.([A-Za-z0-9_]+)/);
    if (m) return m[1];
  }
  return "";
}

async function postLeadUpsert(apiUrl, token, record) {
  const res = await fetch(apiUrl, {
    method: "POST",
    headers: {
      Authorization: `Zoho-oauthtoken ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      data: [record],
      duplicate_check_fields: ["Email"],
    }),
  });
  const { json, text } = await parseJsonResponse(res);
  const row = json && Array.isArray(json.data) ? json.data[0] : null;

  if (row && row.code === "SUCCESS" && row.details && row.details.id) {
    return {
      ok: true,
      id: String(row.details.id),
      action: String(row.action || "insert"),
    };
  }

  const code = (row && row.code) || (json && json.code) || `http_${res.status}`;
  const message =
    (row && row.message) ||
    (json && (json.message || json.error)) ||
    text.slice(0, 160) ||
    "zoho_upsert_failed";
  return {
    ok: false,
    code: String(code),
    error: `${code}: ${String(message).slice(0, 160)}`,
    invalidApiName: invalidApiNameFromZoho(row),
  };
}

function stripOrFallbackPicklist(record, apiName) {
  const next = { ...record };
  if (apiName === "Lead_Source" && next.Lead_Source && next.Lead_Source !== "Web Research") {
    next.Lead_Source = "Web Research";
    return next;
  }
  delete next[apiName];
  return next;
}

/**
 * Create or update a Lead. Returns { skipped } if env is not configured.
 */
export async function upsertEnquiryLead(data, env) {
  const e = env || process.env || {};
  if (!isZohoConfigured(e)) {
    return { skipped: true };
  }

  const email = String((data && data.email) || "").trim();
  if (!email) {
    return { skipped: false, ok: false, error: "missing_email" };
  }

  const apiDomain = envStr(e, "ZOHO_API_DOMAIN", DEFAULT_API_DOMAIN).replace(/\/$/, "");
  const version = envStr(e, "ZOHO_API_VERSION", DEFAULT_API_VERSION).replace(/^\//, "");
  const apiUrl = `${apiDomain}/crm/${version}/Leads/upsert`;
  const token = await refreshAccessToken(e);

  let record = mapEnquiryToLead(data, e);
  let lastErr = "zoho_upsert_failed";

  for (let attempt = 0; attempt < 5; attempt++) {
    const result = await postLeadUpsert(apiUrl, token, record);
    if (result.ok) {
      return {
        skipped: false,
        ok: true,
        id: result.id,
        action: result.action,
      };
    }
    lastErr = result.error;
    const apiName = result.invalidApiName;
    if (apiName && (PICKLIST_FIELDS.includes(apiName) || apiName in record)) {
      const before = JSON.stringify(record);
      record = dropEmpty(stripOrFallbackPicklist(record, apiName));
      if (JSON.stringify(record) !== before) continue;
    }
    break;
  }

  throw new Error(String(lastErr).slice(0, 220));
}
