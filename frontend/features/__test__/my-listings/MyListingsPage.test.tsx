import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { USER_ID_HEADER, USER_ID_STORAGE_KEY } from "@/config/api";
import { MyListingsPage } from "@/features/my-listings/MyListingsPage";
import { mockApi, requestBody } from "@/mocks/mockApi";
import { testListing } from "@/mocks/testListing";
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

describe("MyListingsPage session flow", () => {
  it("creates a user when there is no user_id and saves it", async () => {
    const fetchMock = mockApi({
      "POST /api/users": () => Response.json(testUser, { status: 201 }),
      "GET /api/my-listings": () => Response.json({ listings: [] }),
    });
    const u = userEvent.setup();
    render(<MyListingsPage />);

    const dialog = await screen.findByRole("dialog", { name: "Create your seller profile" });
    await u.type(within(dialog).getByLabelText("First name"), "Ann");
    await u.type(within(dialog).getByLabelText("Last name"), "Lee");
    await u.type(within(dialog).getByLabelText("WhatsApp number"), "+1 415 555 2671");
    await u.click(within(dialog).getByRole("button", { name: "Continue" }));

    expect(await screen.findByText("You have no listings yet. Add your first phone for sale.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Add new phone" })).toHaveLength(1);
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBe(testUser.id);
    expect(requestBody(fetchMock.mock.calls[0]![1]!)).toEqual({
      first_name: "Ann",
      last_name: "Lee",
      whatsapp: "+14155552671",
    });
    const listingsInit = fetchMock.mock.calls[1]![1]!;
    expect((listingsInit.headers as Record<string, string>)[USER_ID_HEADER]).toBe(testUser.id);
  });

  it("shows field errors and does not call the API for an invalid profile", async () => {
    const fetchMock = mockApi({});
    const u = userEvent.setup();
    render(<MyListingsPage />);

    const dialog = await screen.findByRole("dialog", { name: "Create your seller profile" });
    await u.type(within(dialog).getByLabelText("WhatsApp number"), "4155552671");
    await u.click(within(dialog).getByRole("button", { name: "Continue" }));

    expect(await within(dialog).findByText("Enter the number in international format, for example +1 415 555 2671.")).toBeInTheDocument();
    expect(within(dialog).getAllByText("Fill in this field.")).toHaveLength(2);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("loads the existing user and the listings", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, testUser.id);
    mockApi({
      "GET /api/users/u-1": () => Response.json(testUser),
      "GET /api/my-listings": () => Response.json({ listings: [testListing] }),
    });
    render(<MyListingsPage />);

    expect(await screen.findByRole("link", { name: testListing.model_name })).toHaveAttribute(
      "href",
      "/phones/p-1",
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Edit profile/ })).not.toBeInTheDocument();
  });

  it("removes a stale user_id on 404 and shows the user modal", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, "gone");
    mockApi({ "GET /api/users/gone": () => new Response(null, { status: 404 }) });
    render(<MyListingsPage />);

    expect(await screen.findByRole("dialog", { name: "Create your seller profile" })).toBeInTheDocument();
    expect(window.localStorage.getItem(USER_ID_STORAGE_KEY)).toBeNull();
  });
});

describe("MyListingsPage delete", () => {
  it("deletes a listing after confirmation", async () => {
    window.localStorage.setItem(USER_ID_STORAGE_KEY, testUser.id);
    mockApi({
      "GET /api/users/u-1": () => Response.json(testUser),
      "GET /api/my-listings": () => Response.json({ listings: [testListing] }),
      "DELETE /api/phones/p-1": () => new Response(null, { status: 204 }),
    });
    const u = userEvent.setup();
    render(<MyListingsPage />);

    await u.click(await screen.findByRole("button", { name: `Delete ${testListing.model_name}` }));
    const dialog = await screen.findByRole("alertdialog");
    await u.click(within(dialog).getByRole("button", { name: "Delete listing" }));

    expect(await screen.findByText("You have no listings yet. Add your first phone for sale.")).toBeInTheDocument();
  });
});
