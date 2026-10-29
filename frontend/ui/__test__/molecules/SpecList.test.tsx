import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SpecList } from "@/ui/molecules/SpecList";

describe("SpecList", () => {
  it("renders each spec as a term and its value", () => {
    render(
      <SpecList
        specs={[
          { label: "Camera", value: "12 MP" },
          { label: "Battery", value: "3,095 mAh" },
        ]}
      />,
    );

    const terms = screen.getAllByRole("term").map((node) => node.textContent);
    const values = screen.getAllByRole("definition").map((node) => node.textContent);
    expect(terms).toEqual(["Camera", "Battery"]);
    expect(values).toEqual(["12 MP", "3,095 mAh"]);
  });

  it("renders an empty list without specs", () => {
    const { container } = render(<SpecList specs={[]} />);

    expect(container.querySelector("dl")).toBeEmptyDOMElement();
  });
});
