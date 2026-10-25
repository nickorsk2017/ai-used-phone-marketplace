import type { Metadata } from "next";
import { MyListingsPage } from "@/features/my-listings/MyListingsPage";

export const metadata: Metadata = {
  title: "My listings",
  robots: { index: false, follow: false },
};

export default function Page() {
  return <MyListingsPage />;
}
