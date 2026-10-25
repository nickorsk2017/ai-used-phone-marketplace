import { describe, expect, it } from "vitest";
import { listingFormSchema, userFormSchema } from "@/schemas/myListingsFormSchemas";

const validListing = {
  description: "iPhone 13 Pro with a 6.1-inch display.",
  camera_megapixels: 12,
  battery_capacity: 3095,
  display_size: 6.1,
  condition_note: "Small scratch on the frame",
  condition: "like_new" as const,
  price: 450,
};

describe("userFormSchema", () => {
  it("normalizes the WhatsApp number", () => {
    expect(
      userFormSchema.parse({ first_name: " Ann ", last_name: "Lee", whatsapp: "+1 (415) 555-2671" }),
    ).toEqual({ first_name: "Ann", last_name: "Lee", whatsapp: "+14155552671" });
  });

  it("rejects a number without the country code and empty names", () => {
    const result = userFormSchema.safeParse({ first_name: "", last_name: "", whatsapp: "4155552671" });
    expect(result.success).toBe(false);
    const messages = result.error?.issues.map((issue) => issue.message);
    expect(messages).toContain("Enter the number in international format, for example +1 415 555 2671.");
    expect(messages).toContain("Fill in this field.");
  });
});

describe("listingFormSchema", () => {
  it("accepts a valid listing and an empty condition note", () => {
    expect(listingFormSchema.parse({ ...validListing, condition_note: "" }).condition_note).toBe("");
  });

  it.each([
    ["price", 0],
    ["price", 10.5],
    ["camera_megapixels", -1],
    ["battery_capacity", Number.NaN],
    ["display_size", 0],
  ])("rejects %s = %s", (field, value) => {
    expect(listingFormSchema.safeParse({ ...validListing, [field]: value }).success).toBe(false);
  });

  it("blocks contacts in the listing text", () => {
    const result = listingFormSchema.safeParse({
      ...validListing,
      condition_note: "Call +1 415 555 2671",
    });
    expect(result.error?.issues[0]?.message).toBe("Remove card numbers, phone numbers and links. Buyers see your WhatsApp number separately.");
  });

  it("requires the condition", () => {
    expect(listingFormSchema.safeParse({ ...validListing, condition: undefined }).success).toBe(false);
  });
});
