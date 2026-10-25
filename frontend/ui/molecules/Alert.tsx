import { Alert as HeroAlert } from "@heroui/react";
import type { ComponentProps, ReactNode } from "react";

interface AlertProps {
  title: string;
  status?: ComponentProps<typeof HeroAlert>["status"];
  action?: ReactNode;
}

export function Alert({ title, status = "danger", action }: AlertProps) {
  return (
    <HeroAlert status={status} role="alert">
      <HeroAlert.Indicator />
      <HeroAlert.Content>
        <HeroAlert.Title>{title}</HeroAlert.Title>
      </HeroAlert.Content>
      {action}
    </HeroAlert>
  );
}
