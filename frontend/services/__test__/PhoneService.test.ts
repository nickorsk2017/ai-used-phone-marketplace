import { afterEach, describe, expect, it, vi } from "vitest";
import { jsonResponse } from "@/mocks/jsonResponse";
import { testPhone } from "@/mocks/testPhone";

async function loadService(stub: boolean) {
  vi.resetModules();
  vi.stubEnv("NEXT_PUBLIC_API_STUB", stub ? "true" : "false");
  return import("@/services/PhoneService");
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe("PhoneService", () => {
  it("returns stub data without network calls when the stub is on", async () => {
    const fetchMock = vi.fn<typeof fetch>();
    vi.stubGlobal("fetch", fetchMock);
    const { PhoneService } = await loadService(true);
    const { STUB_PHONE_IDS } = await import("@/services/stubs/phoneStub");

    expect(await PhoneService.getById(STUB_PHONE_IDS[0])).toMatchObject({ success: true, data: { id: STUB_PHONE_IDS[0] } });
    expect(await PhoneService.getContact(STUB_PHONE_IDS[0])).toMatchObject({ success: true, data: { whatsapp: expect.stringMatching(/^\+\d+$/) } });
    expect(await PhoneService.getById("missing")).toMatchObject({ success: true, data: null });
    expect(await PhoneService.getContact("missing")).toMatchObject({ success: false, status: 404 });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("calls the Backend and validates the listing when the stub is off", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse({ ...testPhone, user_id: "u1" }));
    vi.stubGlobal("fetch", fetchMock);
    const { PhoneService } = await loadService(false);

    expect(await PhoneService.getById(testPhone.id)).toEqual({ success: true, data: testPhone, errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/phones/${testPhone.id}`);
  });

  it("returns null data on 404 and 422, an error on other statuses and invalid data", async () => {
    const { PhoneService } = await loadService(false);

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
    const { PhoneService } = await loadService(false);

    expect(await PhoneService.getContact(testPhone.id)).toEqual({ success: true, data: contact, errorText: "" });
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/phones/${testPhone.id}/contact`);
  });

  it("unwraps my listings and passes errors through", async () => {
    const { PhoneService } = await loadService(false);

    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({ listings: [testPhone] })));
    expect(await PhoneService.getMyListings()).toEqual({ success: true, data: [testPhone], errorText: "" });
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse({}, 503)));
    expect(await PhoneService.getMyListings()).toMatchObject({ success: false, status: 503 });
  });
});
