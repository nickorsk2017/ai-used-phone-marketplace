import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { testPhone } from "@/mocks/testPhone";
import { PhoneCard } from "@/ui/organisms/PhoneCard";

describe("PhoneCard", () => {
  it("renders the model, price, OS, specs and condition", () => {
    render(<PhoneCard phone={testPhone} />);

    expect(screen.getByText("$450")).toBeInTheDocument();
    expect(screen.getByText("iOS")).toBeInTheDocument();
    expect(screen.getByText("12 MP")).toBeInTheDocument();
    expect(screen.getByText("3,095 mAh")).toBeInTheDocument();
    expect(screen.getByText('6.1"')).toBeInTheDocument();
    expect(screen.getByText("Like new")).toBeInTheDocument();
    expect(screen.getByText(testPhone.condition_note!)).toBeInTheDocument();
  });

  it("links the model name to the Phone details page", () => {
    render(<PhoneCard phone={testPhone} />);

    expect(screen.getByRole("link", { name: testPhone.model_name })).toHaveAttribute(
      "href",
      `/phones/${testPhone.id}`,
    );
  });

  it("omits the condition note when it is empty", () => {
    render(<PhoneCard phone={{ ...testPhone, condition_note: "" }} />);

    expect(screen.queryByText(testPhone.condition_note!)).not.toBeInTheDocument();
  });

  it("renders the actions", () => {
    render(<PhoneCard phone={testPhone} actions={<button type="button">Delete</button>} />);

    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
  });
});
