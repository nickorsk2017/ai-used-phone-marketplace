export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/** Temporary switch to stub API data until the Backend is implemented. */
export const API_STUB_ENABLED = process.env.NEXT_PUBLIC_API_STUB === "true";

/** Public site URL: base for canonical and Open Graph URLs. */
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const USER_ID_STORAGE_KEY = "user_id";

export const USER_ID_HEADER = "X-User-Id";
