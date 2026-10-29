import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageContainer } from "@/ui/layouts/PageContainer";

describe("PageContainer", () => {
  it("renders the children in the main landmark", () => {
    render(<PageContainer>Content</PageContainer>);

    expect(screen.getByRole("main")).toHaveTextContent("Content");
  });
});
