import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PhoneDetailsPage } from "@/features/phone-details/PhoneDetailsPage";
import { testPhone } from "@/mocks/testPhone";

describe("PhoneDetailsPage", () => {
  it("renders model, parameters, price, condition, description and condition note", () => {
    render(<PhoneDetailsPage phone={testPhone} />);

    expect(screen.getByRole("heading", { level: 1, name: "iPhone 13 Pro" })).toBeInTheDocument();
    expect(screen.getAllByText("iOS").length).toBeGreaterThan(0);
    expect(screen.getByText("12 MP")).toBeInTheDocument();
    expect(screen.getByText("3,095 mAh")).toBeInTheDocument();
    expect(screen.getByText('6.1"')).toBeInTheDocument();
    expect(screen.getByText("$450")).toBeInTheDocument();
    expect(screen.getByText("Like new")).toBeInTheDocument();
    expect(screen.getByText(testPhone.description)).toBeInTheDocument();
    expect(screen.getByText(testPhone.condition_note)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Deal" })).toBeInTheDocument();
  });

  it("includes Product JSON-LD and no contact data", () => {
    const { container } = render(<PhoneDetailsPage phone={testPhone} />);
    const script = container.querySelector('script[type="application/ld+json"]');

    expect(JSON.parse(script?.textContent ?? "{}")).toMatchObject({ "@type": "Product" });
    expect(container.innerHTML).not.toMatch(/whatsapp/i);
  });

  it("hides the condition note section when the note is empty", () => {
    render(<PhoneDetailsPage phone={{ ...testPhone, condition_note: "  " }} />);
    expect(screen.queryByRole("heading", { level: 2, name: /note/i })).not.toBeInTheDocument();
  });
});
