/**
 * Cloudflare Pages Function — GET `/api/geo`.
 * Returns the visitor country from the Cloudflare edge (no third-party IP API).
 * Used only for client-side enroll-card display; HTML/schema stay Malaysia RM.
 */
export async function onRequestGet(context) {
  const { request } = context;
  const cf = request && request.cf ? request.cf : {};
  const headerCountry =
    request && request.headers && typeof request.headers.get === "function"
      ? request.headers.get("CF-IPCountry")
      : "";
  const raw =
    (typeof cf.country === "string" && cf.country) || headerCountry || "";
  const country = String(raw).toUpperCase();
  const unknown = !country || country === "XX" || country === "T1";
  return new Response(JSON.stringify({ country: unknown ? "" : country }), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "private, max-age=300",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
