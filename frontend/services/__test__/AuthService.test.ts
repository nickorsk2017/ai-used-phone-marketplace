import { afterEach, describe, expect, it, vi } from "vitest";
import { USER_ID_STORAGE_KEY } from "@/config/api";
import { AuthService } from "@/services/AuthService";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testUser } from "@/mocks/testUser";

afterEach(() => {
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("AuthService.getCurrentUser", () => {
  it("returns null without a request when there is no user_id", async () => {
    const fetchMock = vi.fn<typeof fetch>();
    vi.stubGlobal("fetch", fetchMock);

    expect(await AuthService.getCurrentUser()).toEqual({ success: true, data: null, errorText: "" });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns the user of the saved user_id", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, testUser.id);
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse(testUser)));

    expect(await AuthService.getCurrentUser()).toMatchObject({ success: true, data: testUser });
  });

  it("clears a stale user_id on 404 and returns null", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, "gone");
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 404)));

    expect(await AuthService.getCurrentUser()).toMatchObject({ success: true, data: null });
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBeNull();
  });

  it("keeps the user_id and returns the error on other failures", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, testUser.id);
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 503)));

    expect(await AuthService.getCurrentUser()).toMatchObject({ success: false, status: 503 });
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBe(testUser.id);
  });
});

describe("AuthService.register", () => {
  const body = { whatsapp: testUser.whatsapp, first_name: testUser.first_name, last_name: testUser.last_name };

  it("creates the user and saves the user_id", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse(testUser, 201)));

    expect(await AuthService.register(body)).toMatchObject({ success: true, data: testUser });
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBe(testUser.id);
  });

  it("does not save the user_id when the request fails", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 500)));

    expect(await AuthService.register(body)).toMatchObject({ success: false, status: 500 });
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBeNull();
  });
});
