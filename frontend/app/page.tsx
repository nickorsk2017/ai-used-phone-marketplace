import type { Metadata } from "next";
import { SearchPage } from "@/features/search/SearchPage";

export const metadata: Metadata = {
  robots: { index: false, follow: true },
};

export default function Page() {
  return <SearchPage />;
}
