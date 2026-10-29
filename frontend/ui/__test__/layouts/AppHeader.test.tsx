import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppHeader } from "@/ui/layouts/AppHeader";

const pathname = vi.hoisted(() => ({ value: "/" }));

vi.mock("next/navigation", () => ({ usePathname: () => pathname.value }));

describe("AppHeader", () => {
  it("marks the current page in the navigation", () => {
    pathname.value = "/my-listings";
    render(<AppHeader />);

    expect(screen.getByRole("link", { name: "My listings" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("link", { name: "Search" })).not.toHaveAttribute("aria-current");
  });

  it("renders the actions", () => {
    pathname.value = "/";
    render(<AppHeader actions={<button type="button">Profile</button>} />);

    expect(screen.getByRole("button", { name: "Profile" })).toBeInTheDocument();
  });
});
