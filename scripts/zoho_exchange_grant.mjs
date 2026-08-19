/**
 * One-time: exchange a Zoho Self Client grant token for a refresh token.
 *
 * Usage (PowerShell):
 *   $env:ZOHO_CLIENT_ID="..."
 *   $env:ZOHO_CLIENT_SECRET="..."
 *   $env:ZOHO_ACCOUNTS_URL="https://accounts.zoho.com"
 *   node scripts/zoho_exchange_grant.mjs YOUR_GRANT_TOKEN
 *
 * Print the refresh_token, then store it as ZOHO_REFRESH_TOKEN in Cloudflare.
 * Do not commit tokens.
 */
const grant = String(process.argv[2] || "").trim();
const clientId = String(process.env.ZOHO_CLIENT_ID || "").trim();
const clientSecret = String(process.env.ZOHO_CLIENT_SECRET || "").trim();
const accounts = String(process.env.ZOHO_ACCOUNTS_URL || "https://accounts.zoho.com")
  .trim()
  .replace(/\/$/, "");

if (!grant || !clientId || !clientSecret) {
  console.error(
    "Need ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, and a grant token argument.\nSee docs/zoho/PHASE_0_SETUP.md",
  );
  process.exit(1);
}

const body = new URLSearchParams({
  grant_type: "authorization_code",
  client_id: clientId,
  client_secret: clientSecret,
  code: grant,
});

const res = await fetch(`${accounts}/oauth/v2/token`, {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: body.toString(),
});
const json = await res.json().catch(() => ({}));

if (!json.refresh_token) {
  console.error("Zoho did not return a refresh_token:");
  console.error(JSON.stringify(json, null, 2));
  process.exit(1);
}

console.log("Save these as Cloudflare Pages encrypted env vars:\n");
console.log(`ZOHO_CLIENT_ID=${clientId}`);
console.log("ZOHO_CLIENT_SECRET=(already have)");
console.log(`ZOHO_REFRESH_TOKEN=${json.refresh_token}`);
console.log(`ZOHO_ACCOUNTS_URL=${accounts}`);
if (accounts.includes("zoho.in")) {
  console.log("ZOHO_API_DOMAIN=https://www.zohoapis.in");
} else if (accounts.includes("zoho.eu")) {
  console.log("ZOHO_API_DOMAIN=https://www.zohoapis.eu");
} else if (accounts.includes("zoho.com.au")) {
  console.log("ZOHO_API_DOMAIN=https://www.zohoapis.com.au");
} else {
  console.log("ZOHO_API_DOMAIN=https://www.zohoapis.com");
}
console.log("\nAccess token (short-lived, Functions refresh this automatically):");
console.log(json.access_token || "(none)");
