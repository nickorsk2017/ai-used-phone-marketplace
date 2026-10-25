import { Card, Skeleton } from "@heroui/react";

interface CardSkeletonGridProps {
  count: number;
  label: string;
}

export function CardSkeletonGrid({ count, label }: CardSkeletonGridProps) {
  return (
    <ul className="grid gap-4 sm:grid-cols-2" aria-busy="true" aria-label={label}>
      {Array.from({ length: count }, (_, index) => (
        <li key={index}>
          <Card className="gap-4">
            <Skeleton className="h-5 w-2/3 rounded-lg" />
            <Skeleton className="h-4 w-1/3 rounded-lg" />
            <Skeleton className="h-10 w-full rounded-lg" />
            <Skeleton className="h-6 w-24 rounded-full" />
          </Card>
        </li>
      ))}
    </ul>
  );
}
