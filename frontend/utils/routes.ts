/** URL of the Phone details page: docs/features/PHONE_DETAILS.md#route. */
export function phoneDetailsPath(id: string): string {
  return `/phones/${encodeURIComponent(id)}`;
}
