import { afterEach, describe, expect, it, vi } from "vitest";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testPhone } from "@/mocks/testPhone";

async function loadService() {
  vi.resetModules();
  return import("@/services/PhoneService");
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("PhoneService", () => {
  it("calls the Backend and validates the listing", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse({ ...testPhone, user_id: "u1" }));
    vi.stubGlobal("fetch", fetchMock);
    const { PhoneService } = await loadService();

    expect(await PhoneService.getById(testPhone.id)).toEqual({ success: true, data: testPhone, errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/phones/${testPhone.id}`);
  });

  it("returns null data on 404 and 422, an error on other statuses and invalid data", async () => {
    const { PhoneService } = await loadService();

    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 404)));
    expect(await PhoneService.getById("a")).toMatchObject({ success: true, data: null });
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 422)));
    expect(await PhoneService.getById("a")).toMatchObject({ success: true, data: null });
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 500)));
    expect(await PhoneService.getById("a")).toMatchObject({ success: false, status: 500 });
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({ id: "a" })));
    expect(await PhoneService.getById("a")).toMatchObject({ success: false, errorText: "Invalid response" });
  });

  it("loads the contact from the contact endpoint", async () => {
    const contact = { whatsapp: "+14155552671", first_name: "Emily", last_name: "Carter" };
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(contact));
    vi.stubGlobal("fetch", fetchMock);
    const { PhoneService } = await loadService();

    expect(await PhoneService.getContact(testPhone.id)).toEqual({ success: true, data: contact, errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/phones/${testPhone.id}/contact`);
  });

  it("unwraps my listings and passes errors through", async () => {
    const { PhoneService } = await loadService();

    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({ listings: [testPhone] })));
    expect(await PhoneService.getMyListings()).toEqual({ success: true, data: [testPhone], errorText: "" });
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 503)));
    expect(await PhoneService.getMyListings()).toMatchObject({ success: false, status: 503 });
  });
});
