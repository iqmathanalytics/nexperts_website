/**
 * Cloudflare Pages Function — POST/OPTIONS for `/api/enquiry-brevo`.
 * Injects Pages env bindings into `process.env` for the shared Brevo handler.
 */
import { handler } from "./enquiry-brevo-core.mjs";

function applyCfEnv(env) {
  const prev =
    typeof globalThis.process !== "undefined" &&
    globalThis.process &&
    globalThis.process.env &&
    typeof globalThis.process.env === "object"
      ? { ...globalThis.process.env }
      : {};
  globalThis.process = globalThis.process || {};
  globalThis.process.env = { ...prev, ...env };
}

function headersToObject(headers) {
  const out = {};
  try {
    if (headers && typeof headers.entries === "function") {
      for (const [k, v] of headers.entries()) {
        out[String(k).toLowerCase()] = v;
      }
    }
  } catch (_) {
    /* ignore */
  }
  return out;
}

export async function onRequestPost(context) {
  const { request, env } = context;
  applyCfEnv(env);
  const body = await request.text();
  const event = {
    httpMethod: request.method || "POST",
    headers: headersToObject(request.headers),
    body,
  };
  const result = await handler(event);
  return new Response(result.body, {
    status: result.statusCode,
    headers: result.headers,
  });
}

export async function onRequestOptions(context) {
  const { env } = context;
  applyCfEnv(env);
  const result = await handler({
    httpMethod: "OPTIONS",
    headers: {},
    body: "",
  });
  return new Response(result.body ?? "", {
    status: result.statusCode,
    headers: result.headers,
  });
}
