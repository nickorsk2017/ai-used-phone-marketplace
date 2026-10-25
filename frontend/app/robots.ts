import type { MetadataRoute } from "next";

/** docs/features/PHONE_DETAILS.md#robots. */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/phones/",
      disallow: ["/my-listings", "/api/"],
    },
  };
}
