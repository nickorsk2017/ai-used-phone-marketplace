"use client";

import { FieldError, Label, NumberField as HeroNumberField } from "@heroui/react";
import { Controller, type Control, type FieldPathByValue, type FieldValues } from "react-hook-form";

interface NumberFieldProps<TInput extends FieldValues, TOutput> {
  control: Control<TInput, unknown, TOutput>;
  name: FieldPathByValue<TInput, number>;
  label: string;
  fractionDigits?: number;
  currency?: string;
}

export function NumberField<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  fractionDigits = 0,
  currency,
}: NumberFieldProps<TInput, TOutput>) {
  const formatOptions: Intl.NumberFormatOptions = currency
    ? { style: "currency", currency, maximumFractionDigits: 0 }
    : { maximumFractionDigits: fractionDigits };

  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <HeroNumberField
          fullWidth
          name={field.name}
          value={field.value}
          onChange={field.onChange}
          onBlur={field.onBlur}
          minValue={0}
          formatOptions={formatOptions}
          isInvalid={Boolean(fieldState.error)}
          validationBehavior="aria"
          className="flex flex-col gap-1"
        >
          <Label>{label}</Label>
          <HeroNumberField.Group>
            <HeroNumberField.Input ref={field.ref} />
          </HeroNumberField.Group>
          <FieldError>{fieldState.error?.message}</FieldError>
        </HeroNumberField>
      )}
    />
  );
}
