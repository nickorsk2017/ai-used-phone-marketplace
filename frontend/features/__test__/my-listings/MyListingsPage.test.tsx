import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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
  it("creates a user when there is no session", async () => {
    const fetchMock = mockApi({
      "GET /api/users/me": () => new Response(null, { status: 401 }),
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
    expect(window.localStorage.length).toBe(0);
    const postCall = fetchMock.mock.calls.find(([, init]) => init?.method === "POST")!;
    expect(requestBody(postCall[1]!)).toEqual({
      first_name: "Ann",
      last_name: "Lee",
      whatsapp: "+14155552671",
    });
    const listingsCall = fetchMock.mock.calls.find(([url]) => String(url) === "/api/my-listings")!;
    expect(listingsCall[1]!.credentials).toBe("include");
    expect((listingsCall[1]!.headers as Record<string, string>)["X-User-Id"]).toBeUndefined();
  });

  it("shows field errors and does not call the API for an invalid profile", async () => {
    const fetchMock = mockApi({ "GET /api/users/me": () => new Response(null, { status: 401 }) });
    const u = userEvent.setup();
    render(<MyListingsPage />);

    const dialog = await screen.findByRole("dialog", { name: "Create your seller profile" });
    await u.type(within(dialog).getByLabelText("WhatsApp number"), "4155552671");
    await u.click(within(dialog).getByRole("button", { name: "Continue" }));

    expect(await within(dialog).findByText("Enter the number in international format, for example +1 415 555 2671.")).toBeInTheDocument();
    expect(within(dialog).getAllByText("Fill in this field.")).toHaveLength(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("loads the existing user and the listings", async () => {
    mockApi({
      "GET /api/users/me": () => Response.json(testUser),
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

  it("shows the user modal when the session is no longer valid", async () => {
    mockApi({ "GET /api/users/me": () => new Response(null, { status: 401 }) });
    render(<MyListingsPage />);

    expect(await screen.findByRole("dialog", { name: "Create your seller profile" })).toBeInTheDocument();
  });
});

describe("MyListingsPage delete", () => {
  it("deletes a listing after confirmation", async () => {
    mockApi({
      "GET /api/users/me": () => Response.json(testUser),
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
