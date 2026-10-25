import { afterEach, describe, expect, it, vi } from "vitest";
import { SEARCH_RESULTS_LIMIT, SearchService } from "@/services/SearchService";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testPhone } from "@/mocks/testPhone";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("SearchService", () => {
  it("sends the prompt and returns the results", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse({ results: [testPhone] }));
    vi.stubGlobal("fetch", fetchMock);

    expect(await SearchService.search("iPhone")).toEqual({ success: true, data: [testPhone], errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe("/api/search");
    expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual({ prompt: "iPhone" });
  });

  it("limits the results", async () => {
    const results = Array.from({ length: SEARCH_RESULTS_LIMIT + 5 }, (_, index) => ({ ...testPhone, id: `p-${index}` }));
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({ results })));

    const response = await SearchService.search("phone");
    expect(response.success && response.data).toHaveLength(SEARCH_RESULTS_LIMIT);
  });

  it("returns the error of a failed request", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 503)));

    expect(await SearchService.search("phone")).toMatchObject({ success: false, status: 503 });
  });
});
