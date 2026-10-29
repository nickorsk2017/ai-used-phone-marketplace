import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useEffect } from "react";
import { useForm, useWatch } from "react-hook-form";
import { describe, expect, it, vi } from "vitest";
import { NumberField } from "@/ui/molecules/forms/NumberField";
import { Select } from "@/ui/molecules/forms/Select";
import { TextField } from "@/ui/molecules/forms/TextField";

interface FormValues {
  model: string;
  price: number;
  condition: string;
}

const CONDITION_OPTIONS = [
  { id: "like_new", label: "Like new" },
  { id: "for_repair", label: "For repair" },
] as const;

function TestForm({
  error,
  onValues,
  onModelChange,
}: {
  error?: keyof FormValues;
  onValues?: (values: FormValues) => void;
  onModelChange?: (value: string) => void;
}) {
  const { control, setError } = useForm<FormValues>({
    defaultValues: { model: "", price: 300, condition: "" },
  });
  const values = useWatch({ control }) as FormValues;

  useEffect(() => {
    if (error) {
      setError(error, { message: `Invalid ${error}` });
    }
  }, [error, setError]);

  useEffect(() => {
    onValues?.(values);
  });

  return (
    <form>
      <TextField
        control={control}
        name="model"
        label="Model"
        description="For example, iPhone 13"
        onValueChange={onModelChange}
      />
      <NumberField control={control} name="price" label="Price" currency="USD" />
      <Select
        control={control}
        name="condition"
        label="Condition"
        placeholder="Select condition"
        options={CONDITION_OPTIONS}
      />
    </form>
  );
}

describe("TextField", () => {
  it("writes the typed value to the form and calls onValueChange", async () => {
    const onValues = vi.fn();
    const onModelChange = vi.fn();
    const user = userEvent.setup();
    render(<TestForm onValues={onValues} onModelChange={onModelChange} />);

    await user.type(screen.getByRole("textbox", { name: "Model" }), "Pixel 8");

    expect(onValues).toHaveBeenLastCalledWith(expect.objectContaining({ model: "Pixel 8" }));
    expect(onModelChange).toHaveBeenLastCalledWith("Pixel 8");
    expect(screen.getByText("For example, iPhone 13")).toBeInTheDocument();
  });

  it("shows the form error and marks the field invalid", async () => {
    render(<TestForm error="model" />);

    expect(await screen.findByText("Invalid model")).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Model" })).toHaveAttribute("aria-invalid", "true");
  });
});

describe("NumberField", () => {
  it("formats the value as USD", () => {
    render(<TestForm />);

    expect(screen.getByRole("textbox", { name: "Price" })).toHaveValue("$300");
  });

  it("shows the form error", async () => {
    render(<TestForm error="price" />);

    expect(await screen.findByText("Invalid price")).toBeInTheDocument();
  });
});

describe("Select", () => {
  it("writes the selected option to the form", async () => {
    const onValues = vi.fn();
    const user = userEvent.setup();
    render(<TestForm onValues={onValues} />);

    await user.click(screen.getByRole("button", { name: /Condition/ }));
    await user.click(await screen.findByRole("option", { name: "For repair" }));

    expect(onValues).toHaveBeenLastCalledWith(expect.objectContaining({ condition: "for_repair" }));
  });

  it("shows the form error", async () => {
    render(<TestForm error="condition" />);

    expect(await screen.findByText("Invalid condition")).toBeInTheDocument();
  });
});
