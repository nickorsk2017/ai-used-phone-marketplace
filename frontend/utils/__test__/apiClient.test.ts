import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import { USER_ID_HEADER, USER_ID_STORAGE_KEY } from "@/config/api";
import { apiRequest, NETWORK_ERROR_STATUS } from "@/utils/apiClient";

const okSchema = z.object({ ok: z.boolean() });

function mockFetch(response: Response) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
  window.localStorage.clear();
});

describe("apiRequest", () => {
  it("sends a JSON body and returns the validated data", async () => {
    const fetchMock = mockFetch(Response.json({ ok: true, extra: 1 }));

    await expect(
      apiRequest("/api/search", { method: "POST", body: { prompt: "x" }, schema: okSchema }),
    ).resolves.toEqual({ success: true, data: { ok: true }, errorText: "" });

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/search");
    expect(init.method).toBe("POST");
    expect(init.body).toBe(JSON.stringify({ prompt: "x" }));
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(init.headers[USER_ID_HEADER]).toBeUndefined();
  });

  it("sends X-User-Id when the session has a user", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, "user-1");
    const fetchMock = mockFetch(Response.json({}));

    await apiRequest("/api/search");

    expect(fetchMock.mock.calls[0][1].headers[USER_ID_HEADER]).toBe("user-1");
  });

  it("returns the status and the Backend detail on an error response", async () => {
    mockFetch(Response.json({ detail: "Model not found" }, { status: 422 }));

    await expect(apiRequest("/api/search")).resolves.toEqual({
      success: false,
      errorText: "Model not found",
      status: 422,
    });
  });

  it("returns a default error text when the error body has no detail", async () => {
    mockFetch(new Response(null, { status: 503 }));

    await expect(apiRequest("/api/search")).resolves.toMatchObject({
      success: false,
      errorText: "Request failed with status 503",
      status: 503,
    });
  });

  it("returns an error when the data does not match the schema", async () => {
    mockFetch(Response.json({ ok: "yes" }));

    await expect(apiRequest("/api/search", { schema: okSchema })).resolves.toMatchObject({
      success: false,
      errorText: "Invalid response",
    });
  });

  it("returns success without data for 204", async () => {
    mockFetch(new Response(null, { status: 204 }));

    await expect(apiRequest("/api/phones/1", { method: "DELETE" })).resolves.toEqual({
      success: true,
      data: undefined,
      errorText: "",
    });
  });

  it("returns a network error status when fetch fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(apiRequest("/api/search")).resolves.toEqual({
      success: false,
      errorText: "Network error",
      status: NETWORK_ERROR_STATUS,
    });
  });
});
