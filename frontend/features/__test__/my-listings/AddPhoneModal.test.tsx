import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { USER_ID_STORAGE_KEY } from "@/config/api";
import { MyListingsPage } from "@/features/my-listings/MyListingsPage";
import { type ApiHandler, mockApi, requestBody } from "@/mocks/mockApi";
import { testListing } from "@/mocks/testListing";
import { testPhoneDescription } from "@/mocks/testPhoneDescription";
import { testUser } from "@/mocks/testUser";
import { useMyListingsStore } from "@/stores/myListingsStore";
import { useSessionStore } from "@/stores/sessionStore";

beforeEach(() => {
  useSessionStore.setState({ status: "checking", user: null });
  useMyListingsStore.setState({ status: "idle", listings: [] });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("MyListingsPage add phone flow", () => {
  async function openAddModal(handlers: Record<string, ApiHandler>) {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, testUser.id);
    const fetchMock = mockApi({
      "GET /api/users/u-1": () => Response.json(testUser),
      "GET /api/my-listings": () => Response.json({ listings: [] }),
      ...handlers,
    });
    const u = userEvent.setup();
    render(<MyListingsPage />);
    await screen.findByText("You have no listings yet. Add your first phone for sale.");
    await u.click(screen.getByRole("button", { name: "Add new phone" }));
    const dialog = await screen.findByRole("dialog", { name: "Add new phone" });
    return { u, dialog, fetchMock };
  }

  async function generate(u: ReturnType<typeof userEvent.setup>, dialog: HTMLElement, name = "iphone 13 pro") {
    await u.type(within(dialog).getByLabelText("Model name"), name);
    await u.click(within(dialog).getByRole("button", { name: "Generate description" }));
  }

  async function fillListing(u: ReturnType<typeof userEvent.setup>, dialog: HTMLElement, note: string) {
    await u.type(within(dialog).getByLabelText("Condition note"), note);
    await u.click(within(dialog).getByRole("button", { name: /Condition/ }));
    await u.click(await screen.findByRole("option", { name: "Average condition" }));
    await u.type(within(dialog).getByLabelText("Price, USD"), "450");
  }

  it("shows the 422 error next to the model name", async () => {
    const { u, dialog } = await openAddModal({
      "POST /api/phones/description": () => new Response(null, { status: 422 }),
    });

    await generate(u, dialog, "iPhone 99");

    expect(await within(dialog).findByText("Model not found. Check that the model really exists.")).toBeInTheDocument();
    expect(within(dialog).getByRole("button", { name: "Publish" })).toBeDisabled();
  });

  it("generates the data, saves the listing and adds it to the list", async () => {
    const { u, dialog, fetchMock } = await openAddModal({
      "POST /api/phones/description": () => Response.json(testPhoneDescription),
      "POST /api/phones": () => Response.json(testListing, { status: 201 }),
    });

    await generate(u, dialog);
    expect(await within(dialog).findByText(testPhoneDescription.model_name)).toBeInTheDocument();
    expect(within(dialog).getByText("iOS")).toBeInTheDocument();
    expect(within(dialog).getByLabelText("Description")).toHaveValue(testPhoneDescription.description);
    expect(within(dialog).queryByText(testPhoneDescription.model_code)).not.toBeInTheDocument();

    await fillListing(u, dialog, "Light scratches");
    await u.click(within(dialog).getByRole("button", { name: "Publish" }));

    expect(await screen.findByRole("link", { name: testListing.model_name })).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
    const saveCall = fetchMock.mock.calls.find(([url, init]) => url === "/api/phones" && init?.method === "POST");
    expect(requestBody(saveCall![1]!)).toEqual({
      model_code: "A2483",
      model_name: "iPhone 13 Pro",
      os: "ios",
      camera_megapixels: 12,
      battery_capacity: 3095,
      display_size: 6.1,
      description: testPhoneDescription.description,
      condition: "average",
      condition_note: "Light scratches",
      price: 450,
    });
  });

  it("blocks contacts in the condition note before the request", async () => {
    const { u, dialog, fetchMock } = await openAddModal({
      "POST /api/phones/description": () => Response.json(testPhoneDescription),
    });

    await generate(u, dialog);
    await within(dialog).findByText(testPhoneDescription.model_name);
    await fillListing(u, dialog, "Call me +1 415 555 2671");
    await u.click(within(dialog).getByRole("button", { name: "Publish" }));

    expect(await within(dialog).findByText("Remove card numbers, phone numbers and links. Buyers see your WhatsApp number separately.")).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => url === "/api/phones")).toBe(false);
  });

  it("keeps the form data when saving fails", async () => {
    const { u, dialog } = await openAddModal({
      "POST /api/phones/description": () => Response.json(testPhoneDescription),
      "POST /api/phones": () => new Response(null, { status: 503 }),
    });

    await generate(u, dialog);
    await within(dialog).findByText(testPhoneDescription.model_name);
    await fillListing(u, dialog, "Light scratches");
    await u.click(within(dialog).getByRole("button", { name: "Publish" }));

    expect(await within(dialog).findByRole("alert")).toHaveTextContent("The listing was not saved. Please try again.");
    expect(within(dialog).getByLabelText("Condition note")).toHaveValue("Light scratches");
    expect(within(dialog).getByRole("button", { name: "Publish" })).toBeEnabled();
  });
});
