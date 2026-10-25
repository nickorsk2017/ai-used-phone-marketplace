import { describe, expect, it } from "vitest";
import { buildPhoneJsonLd, buildPhoneMetadata, serializeJsonLd } from "@/features/phone-details/seo";
import { testPhone } from "@/mocks/testPhone";

describe("buildPhoneMetadata", () => {
  it("builds title, description, canonical and Open Graph", () => {
    const metadata = buildPhoneMetadata({ ...testPhone, price: 1200 });
    const title = "iPhone 13 Pro, Like new, $1,200";

    expect(metadata.title).toEqual({ absolute: title });
    expect(metadata.description).toBe(testPhone.description.slice(0, 155).trimEnd());
    expect((metadata.description as string).length).toBeLessThanOrEqual(155);
    expect(metadata.alternates?.canonical).toBe(`/phones/${testPhone.id}`);
    expect(metadata.openGraph).toMatchObject({ title, url: `/phones/${testPhone.id}` });
  });
});

describe("buildPhoneJsonLd", () => {
  it("maps the condition to schema.org values", () => {
    expect(buildPhoneJsonLd(testPhone).offers.itemCondition).toBe("https://schema.org/UsedCondition");
    expect(buildPhoneJsonLd({ ...testPhone, condition: "average" }).offers.itemCondition).toBe(
      "https://schema.org/UsedCondition",
    );
    expect(buildPhoneJsonLd({ ...testPhone, condition: "for_repair" }).offers.itemCondition).toBe(
      "https://schema.org/DamagedCondition",
    );
  });

  it("is a Product with a USD Offer", () => {
    expect(buildPhoneJsonLd(testPhone)).toMatchObject({
      "@type": "Product",
      name: testPhone.model_name,
      offers: { "@type": "Offer", price: 450, priceCurrency: "USD" },
    });
  });

  it("escapes < in the serialized JSON", () => {
    const json = serializeJsonLd(buildPhoneJsonLd({ ...testPhone, description: "</script><b>" }));
    expect(json).not.toContain("<");
    expect(JSON.parse(json).description).toBe("</script><b>");
  });
});
