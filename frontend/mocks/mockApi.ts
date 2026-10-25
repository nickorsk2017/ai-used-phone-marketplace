import { vi } from "vitest";

export type ApiHandler = (init: RequestInit) => Response | Promise<Response>;

/** Stubs `fetch` with handlers keyed by `<METHOD> <path>`. An unexpected request fails the test. */
export function mockApi(handlers: Record<string, ApiHandler>) {
  const fetchMock = vi.fn<typeof fetch>(async (input, init = {}) => {
    const key = `${init.method ?? "GET"} ${String(input)}`;
    const handler = handlers[key];
    if (!handler) {
      throw new Error(`Unexpected request ${key}`);
    }
    return handler(init);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export function requestBody(init: RequestInit) {
  return JSON.parse(String(init.body));
}
