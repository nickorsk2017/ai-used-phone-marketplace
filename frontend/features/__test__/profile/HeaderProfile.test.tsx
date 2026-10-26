import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { HeaderProfile } from "@/features/profile/HeaderProfile";
import { mockApi, requestBody } from "@/mocks/mockApi";
import { testUser } from "@/mocks/testUser";
import { useSessionStore } from "@/stores/sessionStore";

beforeEach(() => {
  useSessionStore.setState({ status: "checking", user: null });
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("HeaderProfile without a user", () => {
  it("renders nothing when there is no valid session", async () => {
    const fetchMock = mockApi({ "GET /api/users/me": () => new Response(null, { status: 401 }) });
    const { container } = render(<HeaderProfile />);

    await waitFor(() => expect(useSessionStore.getState().status).toBe("anonymous"));
    expect(container).toBeEmptyDOMElement();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe("HeaderProfile", () => {
  it("updates the profile with PUT and shows the new name", async () => {
    const updatedUser = { ...testUser, first_name: "Anna", whatsapp: "+14155550000" };
    const fetchMock = mockApi({
      "GET /api/users/me": () => Response.json(testUser),
      "PUT /api/users/me": () => Response.json(updatedUser),
    });
    const user = userEvent.setup();
    render(<HeaderProfile />);

    await user.click(await screen.findByRole("button", { name: "Edit profile Ann Lee" }));
    const dialog = await screen.findByRole("dialog", { name: "Edit your seller profile" });
    expect(within(dialog).getByLabelText("WhatsApp number")).toHaveValue(testUser.whatsapp);
    await user.clear(within(dialog).getByLabelText("First name"));
    await user.type(within(dialog).getByLabelText("First name"), "Anna");
    await user.clear(within(dialog).getByLabelText("WhatsApp number"));
    await user.type(within(dialog).getByLabelText("WhatsApp number"), "+1 415 555 0000");
    await user.click(within(dialog).getByRole("button", { name: "Save" }));

    expect(await screen.findByRole("button", { name: "Edit profile Anna Lee" })).toBeInTheDocument();
    const putCall = fetchMock.mock.calls.find(([, init]) => init?.method === "PUT")!;
    expect(requestBody(putCall[1]!)).toEqual({ first_name: "Anna", last_name: "Lee", whatsapp: "+14155550000" });
  });

  it("keeps the form and shows an error when saving fails", async () => {
    mockApi({
      "GET /api/users/me": () => Response.json(testUser),
      "PUT /api/users/me": () => new Response(null, { status: 500 }),
    });
    const user = userEvent.setup();
    render(<HeaderProfile />);

    await user.click(await screen.findByRole("button", { name: "Edit profile Ann Lee" }));
    const dialog = await screen.findByRole("dialog", { name: "Edit your seller profile" });
    await user.click(within(dialog).getByRole("button", { name: "Save" }));

    expect(await within(dialog).findByText("Could not save the profile. Please try again.")).toBeInTheDocument();
    expect(within(dialog).getByLabelText("First name")).toHaveValue(testUser.first_name);
  });

  it("drops the user when the session is no longer valid on save", async () => {
    mockApi({
      "GET /api/users/me": () => Response.json(testUser),
      "PUT /api/users/me": () => new Response(null, { status: 401 }),
    });
    const user = userEvent.setup();
    const { container } = render(<HeaderProfile />);

    await user.click(await screen.findByRole("button", { name: "Edit profile Ann Lee" }));
    const dialog = await screen.findByRole("dialog", { name: "Edit your seller profile" });
    await user.click(within(dialog).getByRole("button", { name: "Save" }));

    await waitFor(() => expect(useSessionStore.getState().status).toBe("anonymous"));
    await waitFor(() => expect(container).toBeEmptyDOMElement());
  });
});
