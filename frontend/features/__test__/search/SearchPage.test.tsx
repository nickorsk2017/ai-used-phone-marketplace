import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useSearchStore } from "@/stores/searchStore";
import { SearchPage } from "@/features/search/SearchPage";

const phone: Entity.Phone = {
  id: "7f1c2a3e-0000-4000-8000-000000000001",
  model_code: "A2483",
  model_name: "iPhone 13 Pro",
  os: "ios",
  camera_megapixels: 12,
  battery_capacity: 3095,
  display_size: 6.1,
  description: "iPhone 13 Pro with a 6.1-inch ProMotion display.",
  condition: "like_new",
  condition_note: "No scratches, original box.",
  price: 450,
  created_at: "2026-10-01T10:00:00Z",
  updated_at: "2026-10-01T10:00:00Z",
};

const PROMPT = "iPhone like new under $500";

function getPrompt() {
  return screen.getByRole("textbox");
}

function getSubmit() {
  return screen.getByRole("button", { name: "Search" });
}

beforeEach(() => {
  useSearchStore.getState().reset();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("SearchPage", () => {
  it("renders the hint, the placeholder and one textarea in the idle state", () => {
    render(<SearchPage />);

    expect(screen.getByText("Describe the phone you need. It helps to mention the condition (like new, average, for repair), your budget in USD and the brand, if you know it.")).toBeInTheDocument();
    expect(getPrompt()).toHaveAttribute("placeholder", "Samsung with a good camera and a long battery life, like new, under $400");
    expect(screen.getAllByRole("textbox")).toHaveLength(1);
    expect(getSubmit()).toBeDisabled();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("shows loading and then the results with links to the Phone details page", async () => {
    let resolve: (value: Response) => void = () => {};
    const fetchMock = vi.fn<typeof fetch>(() => new Promise<Response>((r) => (resolve = r)));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(getPrompt(), PROMPT);
    await user.click(getSubmit());

    expect(screen.getByRole("list", { name: "Results" })).toHaveAttribute("aria-busy", "true");
    expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual({ prompt: PROMPT });

    resolve(Response.json({ results: [phone] }));

    const link = await screen.findByRole("link", { name: phone.model_name });
    expect(link).toHaveAttribute("href", `/phones/${phone.id}`);
    expect(screen.getByText("$450")).toBeInTheDocument();
    expect(screen.getByText("Like new")).toBeInTheDocument();
    expect(screen.getByText("12 MP")).toBeInTheDocument();
    expect(screen.getByText("3,095 mAh")).toBeInTheDocument();
    expect(screen.getByText("iOS")).toBeInTheDocument();
  });

  it("shows the empty state when nothing is found", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ results: [] })));
    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(getPrompt(), PROMPT);
    await user.click(getSubmit());

    expect(await screen.findByText("No phones match your prompt. Try to describe the phone in other words.")).toBeInTheDocument();
  });

  it("shows the error and keeps the prompt in the field", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 503 })));
    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(getPrompt(), PROMPT);
    await user.click(getSubmit());

    expect(await screen.findByRole("alert")).toHaveTextContent("Something went wrong. Please try again later.");
    expect(getPrompt()).toHaveValue(PROMPT);
    await waitFor(() => expect(getSubmit()).toBeEnabled());
  });

  it("submits with Ctrl+Enter", async () => {
    const fetchMock = vi.fn().mockResolvedValue(Response.json({ results: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    render(<SearchPage />);

    await user.type(getPrompt(), PROMPT);
    await user.keyboard("{Control>}{Enter}{/Control}");

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  });
});
