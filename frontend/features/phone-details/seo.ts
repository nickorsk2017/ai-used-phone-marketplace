import type { Metadata } from "next";
import { SITE_URL } from "@/config/api";
import { CONDITION_LABELS } from "@/config/phone";
import { formatPriceUsd } from "@/utils/format";
import { phoneDetailsPath } from "@/utils/routes";

/** Length of the meta description: docs/features/PHONE_DETAILS.md#metadata. */
const META_DESCRIPTION_LENGTH = 155;

/** schema.org `itemCondition`: docs/features/PHONE_DETAILS.md#structured-data. */
const ITEM_CONDITION_SCHEMA: Record<Entity.PhoneCondition, string> = {
  like_new: "https://schema.org/UsedCondition",
  average: "https://schema.org/UsedCondition",
  for_repair: "https://schema.org/DamagedCondition",
};

/** Metadata of the Phone details page: docs/features/PHONE_DETAILS.md#metadata. */
export function buildPhoneMetadata(phone: Entity.Phone): Metadata {
  const title = `${phone.model_name}, ${CONDITION_LABELS[phone.condition]}, ${formatPriceUsd(phone.price)}`;
  const description = phone.description.slice(0, META_DESCRIPTION_LENGTH).trimEnd();
  const url = phoneDetailsPath(phone.id);

  return {
    title: { absolute: title },
    description,
    alternates: { canonical: url },
    openGraph: { title, description, url },
  };
}

/** JSON-LD `Product` with an `Offer`: docs/features/PHONE_DETAILS.md#structured-data. */
export function buildPhoneJsonLd(phone: Entity.Phone) {
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    name: phone.model_name,
    model: phone.model_code,
    description: phone.description,
    offers: {
      "@type": "Offer",
      url: new URL(phoneDetailsPath(phone.id), SITE_URL).toString(),
      price: phone.price,
      priceCurrency: "USD",
      itemCondition: ITEM_CONDITION_SCHEMA[phone.condition],
      availability: "https://schema.org/InStock",
    },
  };
}

/** JSON for a `<script>` tag: `<` is escaped against XSS through the listing text. */
export function serializeJsonLd(data: unknown): string {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}
