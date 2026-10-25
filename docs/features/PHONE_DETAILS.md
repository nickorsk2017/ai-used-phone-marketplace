# Phone Details

The public page of a single listing. It is the only page that requires SEO, which is why the Frontend uses Next.js (see [DESIGN.md](../DESIGN.md)).

## Route

`/phones/[id]`

- `id`: listing ID from PostgreSQL. It is the only value in the URL and the only value used to find the listing.

## Page Content

1. Model name and OS.
2. Phone parameters used by the search: model, camera, battery, display.
3. Price in USD.
4. Condition badge: like new, average condition, for repair.
5. Model description: see [MY_LISTING.md](MY_LISTING.md#description-response).
6. The user's note about the phone condition.
7. "Deal" button.

The page has no images in v1.0 (see `TASK.md`, Out of scope).

## Deal Flow

1. The user clicks the "Deal" button.
2. The Frontend calls `GET /api/phones/{id}/contact` with the listing ID. The `user_id` of the listing owner is not sent to the Frontend (see [AUTH.md](../backend/AUTH.md#access)). The WhatsApp number is loaded only on click to protect it from scrapers and spam.
3. A modal window shows the WhatsApp number and a "Copy WhatsApp number" button.
4. The button copies the number to the clipboard with the Clipboard API and shows a "Copied" confirmation.

The WhatsApp number is not rendered in the server HTML and is not part of the structured data. This also keeps the number separate from the listing text, as required by the Antifraud rule in `TASK.md`.

## Rendering

- Next.js App Router, Server Component.
- Incremental Static Regeneration: the page is rendered on the server on the first request, cached and revalidated every 60 seconds (`revalidate = 60`).
- `generateStaticParams` returns an empty list. Pages are generated on demand, so the build does not depend on the number of listings.
- Data is fetched from the Backend with `GET /api/phones/{id}`. The response is validated against the shared listing schema (Pydantic on the Backend, the same shape typed on the Frontend).
- Only the "Deal" button and the modal window are Client Components. The rest of the page is server HTML without client JavaScript.

## SEO

### Metadata

Generated in `generateMetadata` from the listing data:

| Tag | Value |
| --- | --- |
| `title` | `{Model}, {Condition}, ${Price}` |
| `description` | First 155 characters of the model description |
| `canonical` | `/phones/{id}` |
| `og:title`, `og:description`, `og:url`, `og:type` | Same as above, `og:type = product` |

### Structured Data

The page includes JSON-LD of type `Product` with an `Offer` (`price`, `priceCurrency = USD`, `itemCondition`). The condition is mapped to schema.org values:

| Condition | `itemCondition` |
| --- | --- |
| `like_new` | `https://schema.org/UsedCondition` |
| `average` | `https://schema.org/UsedCondition` |
| `for_repair` | `https://schema.org/DamagedCondition` |

### Robots

- `app/robots.ts` allows `/phones/` and disallows `/my-listings` and `/api/`.
- The Search page and My listings page are not indexed (`noindex`). Search results depend on the user's prompt and have no stable content.

## Errors

- Listing not found or deleted: `notFound()`, HTTP 404. The page is removed from the index by search engines.
- Backend unavailable: the cached page is served if it exists. Otherwise the error page is shown with HTTP 500: see [DESIGN.md](../frontend/DESIGN.md#errors).

## Acceptance Criteria

1. The server HTML (without JavaScript) contains the model name, parameters, price, condition, description and condition note.
2. The server HTML does not contain the WhatsApp number.
3. The JSON-LD passes the Google Rich Results Test without errors.
4. A deleted listing returns HTTP 404 no later than 60 seconds after deletion.
5. Lighthouse SEO score is 100 for the page.

## Tradeoffs

### No sitemap in v1.0

A sitemap is not needed in v1.0 (PoC). The PoC is a short demo, search engines are not expected to index it. Sitemap: see [ROADMAP.md](../ROADMAP.md#production-baseline).

### Time-based revalidation only

v1.0 uses time-based revalidation only (`revalidate = 60`, see [Rendering](#rendering)). There is no on-demand revalidation. After a listing is updated or deleted, the page shows the previous version for up to 60 seconds.

On-demand revalidation: see [ROADMAP.md](../ROADMAP.md#high-load).
