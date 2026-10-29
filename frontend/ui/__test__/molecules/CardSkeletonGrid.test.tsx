import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CardSkeletonGrid } from "@/ui/molecules/CardSkeletonGrid";

describe("CardSkeletonGrid", () => {
  it("renders the requested number of busy placeholders", () => {
    render(<CardSkeletonGrid count={3} label="Loading phones" />);

    const list = screen.getByRole("list", { name: "Loading phones" });
    expect(list).toHaveAttribute("aria-busy", "true");
    expect(screen.getAllByRole("listitem")).toHaveLength(3);
  });
});
