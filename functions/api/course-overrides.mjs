/**
 * Cloudflare Pages Function — GET/POST/OPTIONS `/api/course-overrides`.
 * Requires KV binding: COURSE_OVERRIDES (see docs/DEPLOY_CLOUDFLARE.md).
 */
import { KV_KEY, handler } from "./course-overrides-core.mjs";

function applyCfEnv(env) {
  const prev =
    typeof globalThis.process !== "undefined" &&
    globalThis.process &&
    globalThis.process.env &&
    typeof globalThis.process.env === "object"
      ? { ...globalThis.process.env }
      : {};
  const vars = {};
  if (env && typeof env === "object") {
    for (const [k, v] of Object.entries(env)) {
      if (
        v != null &&
        (typeof v === "string" ||
          typeof v === "number" ||
          typeof v === "boolean")
      ) {
        vars[k] = typeof v === "string" ? v : String(v);
      }
    }
  }
  globalThis.process = globalThis.process || {};
  globalThis.process.env = { ...prev, ...vars };
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

function kvStorage(env) {
  const kv = env && env.COURSE_OVERRIDES;
  if (!kv) return {};
  return {
    async getPublished() {
      const raw = await kv.get(KV_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    },
    async setPublished(data) {
      await kv.put(KV_KEY, JSON.stringify(data));
    },
  };
}

async function handleRequest(context) {
  const { request, env } = context;
  applyCfEnv(env);
  const body = request.method === "GET" || request.method === "OPTIONS" ? "" : await request.text();
  const event = {
    httpMethod: request.method || "GET",
    headers: headersToObject(request.headers),
    body,
  };
  const result = await handler(event, kvStorage(env), env);
  return new Response(result.body ?? "", {
    status: result.statusCode,
    headers: result.headers,
  });
}

export const onRequestGet = handleRequest;
export const onRequestPost = handleRequest;
export const onRequestOptions = handleRequest;
