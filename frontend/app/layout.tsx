import type { Metadata } from "next";
import { SITE_URL } from "@/config/api";
import { APP_DESCRIPTION, APP_NAME } from "@/config/app";
import { HeaderProfile } from "@/features/profile/HeaderProfile";
import { AppHeader } from "@/ui/layouts/AppHeader";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: APP_NAME, template: `%s | ${APP_NAME}` },
  description: APP_DESCRIPTION,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-background font-sans text-foreground">
        <AppHeader actions={<HeaderProfile />} />
        {children}
      </body>
    </html>
  );
}
