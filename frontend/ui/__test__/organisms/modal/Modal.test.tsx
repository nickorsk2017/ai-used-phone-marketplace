import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Modal } from "@/ui/organisms/modal/Modal";

describe("Modal", () => {
  it("renders nothing when closed", () => {
    render(
      <Modal isOpen={false} onOpenChange={vi.fn()} title="Add phone">
        Body
      </Modal>,
    );

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders the title, subtitle, body and footer when open", () => {
    render(
      <Modal
        isOpen
        onOpenChange={vi.fn()}
        title="Add phone"
        subtitle="Describe your phone"
        footer={<button type="button">Save</button>}
      >
        Body
      </Modal>,
    );

    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("Add phone");
    expect(dialog).toHaveTextContent("Describe your phone");
    expect(dialog).toHaveTextContent("Body");
    expect(screen.getByRole("button", { name: "Save" })).toBeInTheDocument();
  });

  it("closes with the close button", async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal isOpen onOpenChange={onOpenChange} title="Add phone">
        Body
      </Modal>,
    );

    await user.click(screen.getByRole("button", { name: "Close" }));

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("hides the close button when hasCloseButton is false", () => {
    render(
      <Modal isOpen onOpenChange={vi.fn()} title="Add phone" hasCloseButton={false}>
        Body
      </Modal>,
    );

    expect(screen.queryByRole("button", { name: "Close" })).not.toBeInTheDocument();
  });

  it("wraps the content in a form and submits it", async () => {
    const onSubmit = vi.fn((event: { preventDefault: () => void }) => event.preventDefault());
    const user = userEvent.setup();
    render(
      <Modal
        isOpen
        onOpenChange={vi.fn()}
        title="Add phone"
        onSubmit={onSubmit}
        footer={<button type="submit">Save</button>}
      >
        Body
      </Modal>,
    );

    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(onSubmit).toHaveBeenCalledOnce();
  });
});
