"use client";

import { useSearchStore } from "@/stores/searchStore";
import { PageContainer } from "@/ui/layouts/PageContainer";
import { SearchForm } from "./SearchForm";
import { SearchResults } from "./SearchResults";

export function SearchPage() {
  const prompt = useSearchStore((state) => state.prompt);
  const status = useSearchStore((state) => state.status);
  const results = useSearchStore((state) => state.results);
  const clarification = useSearchStore((state) => state.clarification);
  const error = useSearchStore((state) => state.error);
  const search = useSearchStore((state) => state.search);

  return (
    <PageContainer>
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Find your next phone</h1>
      </header>
      <SearchForm
        defaultPrompt={prompt}
        isLoading={status === "loading"}
        onSearch={(value) => void search(value)}
      />
      <SearchResults status={status} results={results} clarification={clarification} error={error} />
    </PageContainer>
  );
}
