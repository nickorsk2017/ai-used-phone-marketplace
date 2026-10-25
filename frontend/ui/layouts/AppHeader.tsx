"use client";

import NextLink from "next/link";
import { usePathname } from "next/navigation";
import { APP_NAME, NAV_ITEMS } from "@/config/app";
import { cn } from "@/utils/cn";

export function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex w-full max-w-4xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <NextLink href="/" className="min-w-0 truncate text-sm font-semibold text-accent">
          {APP_NAME}
        </NextLink>
        <nav aria-label="Main">
          <ul className="flex shrink-0 gap-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              return (
                <li key={item.href}>
                  <NextLink
                    href={item.href}
                    aria-current={isActive ? "page" : undefined}
                    className={cn(
                      "rounded-lg px-2 py-2 text-sm whitespace-nowrap transition-colors hover:bg-default sm:px-3",
                      isActive ? "font-medium text-foreground" : "text-muted",
                    )}
                  >
                    {item.label}
                  </NextLink>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </header>
  );
}
