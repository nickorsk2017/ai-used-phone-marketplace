import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Alert } from "@/ui/molecules/Alert";

describe("Alert", () => {
  it("renders the title in an alert region", () => {
    render(<Alert title="Search is unavailable" />);

    expect(screen.getByRole("alert")).toHaveTextContent("Search is unavailable");
  });

  it("renders the action", () => {
    render(<Alert title="Search is unavailable" action={<button type="button">Retry</button>} />);

    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
});
