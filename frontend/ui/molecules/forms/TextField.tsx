"use client";

import { Description, FieldError, Input, Label, TextArea, TextField as HeroTextField } from "@heroui/react";
import { Controller, type Control, type FieldPathByValue, type FieldValues } from "react-hook-form";

interface TextFieldProps<TInput extends FieldValues, TOutput> {
  control: Control<TInput, unknown, TOutput>;
  name: FieldPathByValue<TInput, string>;
  label: string;
  description?: string;
  placeholder?: string;
  type?: "text" | "tel";
  autoComplete?: string;
  rows?: number;
  onValueChange?: (value: string) => void;
}

export function TextField<TInput extends FieldValues, TOutput>({
  control,
  name,
  label,
  description,
  placeholder,
  type,
  autoComplete,
  rows,
  onValueChange,
}: TextFieldProps<TInput, TOutput>) {
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => {
        const inputJSX = rows ? (
          <TextArea ref={field.ref} rows={rows} placeholder={placeholder} className="resize-y" />
        ) : (
          <Input ref={field.ref} placeholder={placeholder} />
        );

        return (
          <HeroTextField
            fullWidth
            name={field.name}
            type={type}
            autoComplete={autoComplete}
            value={field.value}
            onChange={(value) => {
              field.onChange(value);
              onValueChange?.(value);
            }}
            onBlur={field.onBlur}
            isInvalid={Boolean(fieldState.error)}
            validationBehavior="aria"
            className="flex flex-col gap-1"
          >
            <Label>{label}</Label>
            {inputJSX}
            {description ? <Description>{description}</Description> : null}
            <FieldError>{fieldState.error?.message}</FieldError>
          </HeroTextField>
        );
      }}
    />
  );
}
