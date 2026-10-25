import { EmptyState } from "@heroui/react";
import type { SearchStatus } from "@/stores/searchStore";
import { Alert } from "@/ui/molecules/Alert";
import { CardSkeletonGrid } from "@/ui/molecules/CardSkeletonGrid";
import { PhoneCard } from "@/ui/organisms/PhoneCard";

const SKELETON_COUNT = 6;

interface SearchResultsProps {
  status: SearchStatus;
  results: Entity.Phone[];
}

export function SearchResults({ status, results }: SearchResultsProps) {
  if (status === "idle") {
    return null;
  }

  if (status === "error") {
    return <Alert title="Something went wrong. Please try again later." />;
  }

  if (status === "loading") {
    return <CardSkeletonGrid count={SKELETON_COUNT} label="Results" />;
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
