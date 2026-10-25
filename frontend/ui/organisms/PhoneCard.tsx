import { Card, Chip } from "@heroui/react";
import NextLink from "next/link";
import type { ReactNode } from "react";
import { CONDITION_CHIP_COLORS, CONDITION_LABELS, OS_LABELS } from "@/config/phone";
import { phoneDetailsPath } from "@/utils/routes";
import { formatPriceUsd } from "@/utils/format";
import { buildPhoneSpecs } from "@/utils/phoneSpecs";
import { SpecList } from "@/ui/molecules/SpecList";

interface PhoneCardProps {
  phone: Entity.Phone;
  /** Controls placed above the card link, for example a Delete button. */
  actions?: ReactNode;
}

export function PhoneCard({ phone, actions }: PhoneCardProps) {
  const conditionNoteJSX = phone.condition_note ? (
    <p className="line-clamp-2 text-sm text-muted">{phone.condition_note}</p>
  ) : null;

  return (
    <Card
      className="h-full transition-shadow focus-within:ring-2 focus-within:ring-focus hover:shadow-overlay"
    >
      <Card.Header className="gap-1">
        <div className="flex items-start justify-between gap-3">
          <Card.Title className="text-base">
            <NextLink
              href={phoneDetailsPath(phone.id)}
              className="outline-none after:absolute after:inset-0"
            >
              {phone.model_name}
            </NextLink>
          </Card.Title>
          <span className="text-lg font-semibold whitespace-nowrap">
            {formatPriceUsd(phone.price)}
          </span>
        </div>
        <Card.Description>{OS_LABELS[phone.os]}</Card.Description>
      </Card.Header>
      <Card.Content className="gap-3">
        <SpecList specs={buildPhoneSpecs(phone)} className="grid-cols-3 gap-2" />
        {conditionNoteJSX}
      </Card.Content>
      <Card.Footer className="justify-between gap-3">
        <Chip color={CONDITION_CHIP_COLORS[phone.condition]} variant="soft" size="sm">
          {CONDITION_LABELS[phone.condition]}
        </Chip>
        {actions ? <div className="relative z-10 flex gap-2">{actions}</div> : null}
      </Card.Footer>
    </Card>
  );
}
