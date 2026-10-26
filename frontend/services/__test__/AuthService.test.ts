import { afterEach, describe, expect, it, vi } from "vitest";
import { AuthService } from "@/services/AuthService";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testUser } from "@/mocks/testUser";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("AuthService.getCurrentUser", () => {
  it("returns the user of the session cookie", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(testUser));
    vi.stubGlobal("fetch", fetchMock);

    expect(await AuthService.getCurrentUser()).toMatchObject({ success: true, data: testUser });
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/users/me");
    expect(fetchMock.mock.calls[0]?.[1]?.credentials).toBe("include");
  });

  it("returns null on 401: there is no valid session", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 401)));

    expect(await AuthService.getCurrentUser()).toEqual({ success: true, data: null, errorText: "" });
  });

  it("returns the error on other failures", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 503)));

    expect(await AuthService.getCurrentUser()).toMatchObject({ success: false, status: 503 });
  });
});

describe("AuthService.register", () => {
  const body = { whatsapp: testUser.whatsapp, first_name: testUser.first_name, last_name: testUser.last_name };

  it("creates the user without storing anything in the browser", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse(testUser, 201)));

    expect(await AuthService.register(body)).toMatchObject({ success: true, data: testUser });
    expect(window.localStorage.length).toBe(0);
  });

  it("returns the error when the request fails", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 500)));

    expect(await AuthService.register(body)).toMatchObject({ success: false, status: 500 });
  });
});
