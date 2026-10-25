import { cn } from "@/utils/cn";
import type { Spec } from "@/utils/phoneSpecs";

interface SpecListProps {
  specs: Spec[];
  className?: string;
}

export function SpecList({ specs, className }: SpecListProps) {
  return (
    <dl className={cn("grid", className)}>
      {specs.map((spec) => (
        <div key={spec.label} className="flex flex-col gap-1">
          <dt className="text-xs text-muted">{spec.label}</dt>
          <dd className="text-sm font-medium">{spec.value}</dd>
        </div>
      ))}
    </dl>
  );
}
