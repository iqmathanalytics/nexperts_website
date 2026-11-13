import { geoHandler } from "../../functions/api/geo-core.mjs";

export async function handler(event) {
  return geoHandler(event || {});
}
