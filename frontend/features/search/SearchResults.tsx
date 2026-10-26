import { Card, EmptyState } from "@heroui/react";
import type { SearchError, SearchStatus } from "@/stores/searchStore";
import { Alert } from "@/ui/molecules/Alert";
import { CardSkeletonGrid } from "@/ui/molecules/CardSkeletonGrid";
import { PhoneCard } from "@/ui/organisms/PhoneCard";

const SKELETON_COUNT = 6;

// Texts by the response of `POST /api/search`: docs/features/SEARCH_PAGE.md#errors.
const ERROR_TEXTS: Record<SearchError, string> = {
  rejected: "We could not process this prompt. Please describe the phone in other words.",
  rate_limited: "Too many requests. Wait 10 seconds and try again.",
  failed: "Something went wrong. Please try again later.",
};

interface SearchResultsProps {
  status: SearchStatus;
  results: Entity.Phone[];
  clarification?: string | null;
  error?: SearchError | null;
}

export function SearchResults({ status, results, clarification, error }: SearchResultsProps) {
  if (status === "idle") {
    return null;
  }

  if (status === "error") {
    return <Alert title={ERROR_TEXTS[error ?? "failed"]} />;
  }

  if (status === "loading") {
    return <CardSkeletonGrid count={SKELETON_COUNT} label="Results" />;
  }

  // Shown in place of the listings: docs/features/SEARCH_PAGE.md#clarification.
  if (clarification) {
    return (
      <Card role="status" className="w-full">
        <Card.Content className="p-6 sm:p-8">
          <p className="text-lg leading-relaxed sm:text-xl">{clarification}</p>
        </Card.Content>
      </Card>
    );
  }

  if (results.length === 0) {
    return (
      <EmptyState className="py-12">
        <p className="text-muted">No phones match your prompt. Try to describe the phone in other words.</p>
      </EmptyState>
    );
  }

  return (
    <section className="flex flex-col gap-4" aria-labelledby="search-results-heading">
      <h2 id="search-results-heading" className="text-lg font-semibold">
        Results
        <span className="ml-2 text-sm font-normal text-muted">{results.length}</span>
      </h2>
      <ul className="grid gap-4 sm:grid-cols-2">
        {results.map((phone) => (
          <li key={phone.id}>
            <PhoneCard phone={phone} />
          </li>
        ))}
      </ul>
    </section>
  );
}
