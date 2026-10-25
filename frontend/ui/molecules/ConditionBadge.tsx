import { chipVariants } from "@heroui/styles";
import { CONDITION_CHIP_COLORS, CONDITION_LABELS } from "@/config/phone";

interface ConditionBadgeProps {
  condition: Entity.PhoneCondition;
}

/** HeroUI Chip styles without client JavaScript, for server-rendered pages. */
export function ConditionBadge({ condition }: ConditionBadgeProps) {
  const slots = chipVariants({ color: CONDITION_CHIP_COLORS[condition], variant: "soft" });
  return (
    <span className={slots.base()} data-slot="chip">
      <span className={slots.label()} data-slot="chip-label">
        {CONDITION_LABELS[condition]}
      </span>
    </span>
  );
}
