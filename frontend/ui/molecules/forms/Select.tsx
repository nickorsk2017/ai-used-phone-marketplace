"use client";

import { FieldError, Label, ListBox, Select as HeroSelect } from "@heroui/react";
import { Controller, type Control, type FieldPathByValue, type FieldValues } from "react-hook-form";

export interface SelectOption {
  id: string;
  label: string;
}

interface SelectProps<TInput extends FieldValues, TOutput> {
  control: Control<TInput, unknown, TOutput>;
  name: FieldPathByValue<TInput, string>;
  label: string;
  placeholder: string;
  options: readonly SelectOption[];
}

export function Select<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  placeholder,
  options,
}: SelectProps<TInput, TOutput>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <HeroSelect
          fullWidth
          name={field.name}
          value={field.value ?? null}
          onChange={(key) => field.onChange(key ?? undefined)}
          onBlur={field.onBlur}
          isInvalid={Boolean(fieldState.error)}
          validationBehavior="aria"
          placeholder={placeholder}
          className="flex flex-col gap-1"
        >
          <Label>{label}</Label>
          <HeroSelect.Trigger ref={field.ref}>
            <HeroSelect.Value />
            <HeroSelect.Indicator />
          </HeroSelect.Trigger>
          <FieldError>{fieldState.error?.message}</FieldError>
          <HeroSelect.Popover>
            <ListBox>
              {options.map((option) => (
                <ListBox.Item key={option.id} id={option.id} textValue={option.label}>
                  {option.label}
                  <ListBox.ItemIndicator />
                </ListBox.Item>
              ))}
            </ListBox>
          </HeroSelect.Popover>
        </HeroSelect>
      )}
    />
  );
}
