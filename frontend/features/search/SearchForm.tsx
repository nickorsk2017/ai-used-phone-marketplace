"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Description, Label, Spinner, TextArea, TextField } from "@heroui/react";
import type { KeyboardEvent } from "react";
import { Controller, useForm } from "react-hook-form";
import { searchFormSchema, type SearchFormValues } from "@/schemas/searchFormSchema";

interface SearchFormProps {
  defaultPrompt: string;
  isLoading: boolean;
  onSearch: (prompt: string) => void;
}

export function SearchForm({ defaultPrompt, isLoading, onSearch }: SearchFormProps) {
  const { control, handleSubmit, formState } = useForm<SearchFormValues>({
    resolver: zodResolver(searchFormSchema),
    defaultValues: { prompt: defaultPrompt },
    mode: "onChange",
  });

  const submit = handleSubmit(({ prompt }) => onSearch(prompt));

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      void submit();
    }
  };

  const canSubmit = formState.isValid && !isLoading;

  return (
    <form className="flex flex-col gap-4" onSubmit={submit} noValidate>
      <Controller
        name="prompt"
        control={control}
        render={({ field }) => (
          <TextField
            fullWidth
            name={field.name}
            value={field.value}
            onChange={field.onChange}
            onBlur={field.onBlur}
            className="flex flex-col gap-2"
          >
            <Label className="text-base font-medium">Prompt</Label>
            <Description>Describe the phone you need. It helps to mention the condition (like new, average, for repair), your budget in USD and the brand, if you know it.</Description>
            <TextArea
              ref={field.ref}
              rows={4}
              placeholder="Samsung with a good camera and a long battery life, like new, under $400"
              onKeyDown={onKeyDown}
              className="resize-y text-base"
            />
          </TextField>
        )}
      />
      <div className="flex items-center justify-end gap-3">
        <span className="hidden text-sm text-muted sm:inline">Ctrl + Enter</span>
        <Button type="submit" size="lg" isDisabled={!canSubmit} isPending={isLoading}>
          {isLoading ? <Spinner color="current" size="sm" /> : null}
          Search
        </Button>
      </div>
    </form>
  );
}
