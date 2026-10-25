import { USER_ID_STORAGE_KEY } from "@/config/api";

/** `user_id` of the browser session: docs/backend/AUTH.md#session-flow. */
export function getUserId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    return window.localStorage.getItem(USER_ID_STORAGE_KEY);
  } catch {
    return null;
  }
}

export function setUserId(userId: string): void {
  try {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, userId);
  } catch {
    // Storage is unavailable: the session lives until the page is reloaded.
  }
}

export function clearUserId(): void {
  try {
    window.localStorage.removeItem(USER_ID_STORAGE_KEY);
  } catch {
    // Storage is unavailable: nothing to clear.
  }
}
