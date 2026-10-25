import { describe, expect, it } from "vitest";
import { searchFormSchema } from "@/schemas/searchFormSchema";

describe("searchFormSchema", () => {
  it("accepts a prompt and trims it", () => {
    expect(searchFormSchema.parse({ prompt: "  iPhone under $300  " })).toEqual({
      prompt: "iPhone under $300",
    });
  });

  it("rejects an empty or whitespace prompt", () => {
    expect(searchFormSchema.safeParse({ prompt: "" }).success).toBe(false);
    expect(searchFormSchema.safeParse({ prompt: "   " }).success).toBe(false);
  });
});
