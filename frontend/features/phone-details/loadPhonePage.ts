import { notFound } from "next/navigation";
import { cache } from "react";
import { PhoneService } from "@/services/PhoneService";

/** One Backend request per render, shared by `generateMetadata` and the page. */
const getPhoneOnce = cache((id: string) => PhoneService.getById(id));

/** Loads the listing of `/phones/[id]`: docs/features/PHONE_DETAILS.md#route. Missing listing: 404. */
export async function loadPhonePage(id: string): Promise<Entity.Phone> {
  const response = await getPhoneOnce(id);
  if (!response.success) {
    throw new Error(response.errorText);
  }
  if (!response.data) {
    notFound();
  }
  return response.data;
}
