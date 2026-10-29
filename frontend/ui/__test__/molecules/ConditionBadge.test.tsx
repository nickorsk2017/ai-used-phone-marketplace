import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CONDITION_LABELS } from "@/config/phone";
import { ConditionBadge } from "@/ui/molecules/ConditionBadge";

describe("ConditionBadge", () => {
  it.each(Object.entries(CONDITION_LABELS) as [Entity.PhoneCondition, string][])(
    "renders the label of %s",
    (condition, label) => {
      render(<ConditionBadge condition={condition} />);

      expect(screen.getByText(label)).toBeInTheDocument();
    },
  );

  it("uses a different style for each condition", () => {
    const { container } = render(
      <>
        <ConditionBadge condition="like_new" />
        <ConditionBadge condition="for_repair" />
      </>,
    );

    const [likeNew, forRepair] = container.querySelectorAll('[data-slot="chip"]');
    expect(likeNew?.className).not.toBe(forRepair?.className);
  });
});
