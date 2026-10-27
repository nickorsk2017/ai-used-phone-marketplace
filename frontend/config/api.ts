/** Backend URL. Server-side requests use `API_INTERNAL_URL` when it is set: docs/INFRA.md#docker-compose. */
const SERVER_API_BASE_URL = typeof window === "undefined" ? process.env.API_INTERNAL_URL : undefined;

export const API_BASE_URL = SERVER_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/** Public site URL: base for canonical and Open Graph URLs. */
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
