import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DealButton } from "@/features/phone-details/DealButton";

const PHONE_ID = "7f1c2a3e-0000-4000-8000-000000000001";
const contact = { whatsapp: "+14155552671", first_name: "Emily", last_name: "Carter" };

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("DealButton", () => {
  it("loads the contact only on click and copies the WhatsApp number", async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse(contact));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    const writeText = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
    render(<DealButton phoneId={PHONE_ID} />);

    expect(fetchMock).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Deal" }));

    expect(await screen.findByText(contact.whatsapp)).toBeInTheDocument();
    expect(screen.getByText("Emily Carter")).toBeInTheDocument();
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`/api/phones/${PHONE_ID}/contact`);

    await user.click(screen.getByRole("button", { name: "Copy WhatsApp number" }));
    expect(writeText).toHaveBeenCalledWith(contact.whatsapp);
    expect(await screen.findByRole("button", { name: "Copied" })).toBeInTheDocument();
  });

  it("shows an error when copying fails", async () => {
    vi.stubGlobal("fetch", vi.fn<typeof fetch>(async () => jsonResponse(contact)));
    const user = userEvent.setup();
    vi.spyOn(navigator.clipboard, "writeText").mockRejectedValue(new Error("denied"));
    render(<DealButton phoneId={PHONE_ID} />);

    await user.click(screen.getByRole("button", { name: "Deal" }));
    await user.click(await screen.findByRole("button", { name: "Copy WhatsApp number" }));
    expect(await screen.findByText("Could not copy the number. Copy it manually.")).toBeInTheDocument();
  });

  it("shows an error and retries when the contact fails to load", async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({}, 500))
      .mockResolvedValueOnce(jsonResponse(contact));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<DealButton phoneId={PHONE_ID} />);

    await user.click(screen.getByRole("button", { name: "Deal" }));
    expect(await screen.findByText("Could not load the contact. Please try again.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Try again" }));
    await waitFor(() => expect(screen.getByText(contact.whatsapp)).toBeInTheDocument());
  });
});
