import { beforeEach, describe, expect, it, vi } from "vitest";
import { PhoneService } from "@/services/PhoneService";
import { loadPhonePage } from "@/features/phone-details/loadPhonePage";
import { testPhone } from "@/mocks/testPhone";

vi.mock("@/services/PhoneService", () => ({ PhoneService: { getById: vi.fn() } }));
vi.mock("next/navigation", () => ({
  notFound: vi.fn(() => {
    throw new Error("NOT_FOUND");
  }),
}));

const getPhoneMock = vi.mocked(PhoneService.getById);

beforeEach(() => {
  getPhoneMock.mockReset();
});

describe("loadPhonePage", () => {
  it("returns the listing by id", async () => {
    getPhoneMock.mockResolvedValue({ success: true, data: testPhone, errorText: "" });
    await expect(loadPhonePage(testPhone.id)).resolves.toEqual(testPhone);
    expect(getPhoneMock).toHaveBeenCalledWith(testPhone.id);
  });

  it("returns 404 for a missing listing", async () => {
    getPhoneMock.mockResolvedValue({ success: true, data: null, errorText: "" });
    await expect(loadPhonePage("missing")).rejects.toThrow("NOT_FOUND");
  });

  it("throws the error text when the request fails", async () => {
    getPhoneMock.mockResolvedValue({ success: false, errorText: "Request failed with status 500", status: 500 });
    await expect(loadPhonePage(testPhone.id)).rejects.toThrow("Request failed with status 500");
  });
});
