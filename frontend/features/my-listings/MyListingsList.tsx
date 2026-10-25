import { Button, EmptyState } from "@heroui/react";
import { Alert } from "@/ui/molecules/Alert";
import { CardSkeletonGrid } from "@/ui/molecules/CardSkeletonGrid";
import { PhoneCard } from "@/ui/organisms/PhoneCard";
import type { MyListingsStatus } from "@/stores/myListingsStore";

const SKELETON_COUNT = 4;

interface MyListingsListProps {
  status: MyListingsStatus;
  listings: Entity.Phone[];
  onRetry: () => void;
  onAdd: () => void;
  onDelete: (phone: Entity.Phone) => void;
}

export function MyListingsList({ status, listings, onRetry, onAdd, onDelete }: MyListingsListProps) {
  if (status === "idle" || status === "loading") {
    return <CardSkeletonGrid count={SKELETON_COUNT} label="My listings" />;
  }

  if (status === "error") {
    return (
      <Alert
        title="Could not load your listings."
        action={
          <Button size="sm" variant="danger-soft" onPress={onRetry}>
            Try again
          </Button>
        }
      />
    );
  }

  if (listings.length === 0) {
    return (
      <EmptyState className="flex flex-col items-center gap-4 py-12">
        <p className="text-muted">You have no listings yet. Add your first phone for sale.</p>
        <Button onPress={onAdd}>Add new phone</Button>
      </EmptyState>
    );
  }

  return (
    <ul className="grid gap-4 sm:grid-cols-2" aria-label="My listings">
      {listings.map((phone) => (
        <li key={phone.id}>
          <PhoneCard
            phone={phone}
            actions={
              <Button
                size="sm"
                variant="danger-soft"
                onPress={() => onDelete(phone)}
                aria-label={`Delete ${phone.model_name}`}
              >
                Delete
              </Button>
            }
          />
        </li>
      ))}
    </ul>
  );
}
