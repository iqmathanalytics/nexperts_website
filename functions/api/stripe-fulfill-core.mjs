/**
 * POST /api/stripe-fulfill
 * - { session_id } → fulfill paid session (email + sheet)
 * - { session_id, status_only: true } → payment status for waiting modal (no side effects)
 */

import {
  fulfillCheckoutSessionById,
  getCheckoutSessionStatus,
} from "./enrollment-fulfill.mjs";
import { corsHeaders, jsonResponse } from "./stripe-http.mjs";

export async function stripeFulfillHandler(event) {
  const method = String(event.httpMethod || event.method || "GET").toUpperCase();
  const origin = (event.headers && (event.headers.origin || event.headers.Origin)) || "";

  if (method === "OPTIONS") {
    return { statusCode: 204, headers: corsHeaders(origin), body: "" };
  }
  if (method !== "POST") {
    return jsonResponse(405, { ok: false, error: "method_not_allowed" });
  }

  let body = {};
  try {
    body =
      typeof event.body === "string"
        ? JSON.parse(event.body || "{}")
        : event.body || {};
  } catch {
    return jsonResponse(400, { ok: false, error: "invalid_json" });
  }

  const sessionId = String(body.session_id || body.sessionId || "").trim();
  if (!sessionId) {
    return jsonResponse(400, { ok: false, error: "session_required" });
  }

  const statusOnly =
    body.status_only === true ||
    body.statusOnly === true ||
    String(body.mode || "").toLowerCase() === "status";

  try {
    if (statusOnly) {
      const status = await getCheckoutSessionStatus(sessionId);
      if (!status.ok) {
        const code = status.error === "stripe_not_configured" ? 503 : 400;
        return jsonResponse(code, status);
      }
      return jsonResponse(200, status);
    }

    const result = await fulfillCheckoutSessionById(sessionId);
    if (!result.ok) {
      const status =
        result.error === "not_paid"
          ? 402
          : result.error === "invalid_session"
            ? 400
            : result.error === "stripe_not_configured"
              ? 503
              : 400;
      return jsonResponse(status, result);
    }
    return jsonResponse(200, result);
  } catch (err) {
    console.error("stripe_fulfill_error", err && err.message);
    return jsonResponse(500, {
      ok: false,
      error: "fulfill_failed",
      detail: String((err && err.message) || "").slice(0, 160),
    });
  }
}
