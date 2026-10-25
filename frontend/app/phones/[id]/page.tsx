import type { Metadata } from "next";
import { PhoneDetailsPage } from "@/features/phone-details/PhoneDetailsPage";
import { loadPhonePage } from "@/features/phone-details/loadPhonePage";
import { buildPhoneMetadata } from "@/features/phone-details/seo";

/** ISR: docs/features/PHONE_DETAILS.md#rendering. */
export const revalidate = 60;

export function generateStaticParams() {
  return [];
}

export async function generateMetadata({ params }: PageProps<"/phones/[id]">): Promise<Metadata> {
  const { id } = await params;
  return buildPhoneMetadata(await loadPhonePage(id));
}

export default async function Page({ params }: PageProps<"/phones/[id]">) {
  const { id } = await params;
  return <PhoneDetailsPage phone={await loadPhonePage(id)} />;
}
