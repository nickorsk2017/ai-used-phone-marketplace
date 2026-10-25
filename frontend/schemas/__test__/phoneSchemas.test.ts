import { describe, expect, it } from "vitest";
import { phoneSchema } from "@/schemas/phoneSchemas";
import { testPhone } from "@/mocks/testPhone";

describe("phoneSchema", () => {
  it("accepts a listing, strips user_id and parses a decimal string", () => {
    const parsed = phoneSchema.parse({ ...testPhone, display_size: "6.1", user_id: "secret" });
    expect(parsed).toEqual(testPhone);
    expect(parsed).not.toHaveProperty("user_id");
  });

  it("rejects an unknown condition and a non-positive price", () => {
    expect(phoneSchema.safeParse({ ...testPhone, condition: "new" }).success).toBe(false);
    expect(phoneSchema.safeParse({ ...testPhone, price: 0 }).success).toBe(false);
  });
});
