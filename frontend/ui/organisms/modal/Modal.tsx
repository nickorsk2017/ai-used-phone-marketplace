"use client";

import { Modal as HeroModal } from "@heroui/react";
import { useMemo, type ComponentProps, type FormEventHandler, type ReactNode } from "react";

type ModalSize = ComponentProps<typeof HeroModal.Container>["size"];

interface ModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  title: string;
  subtitle?: string;
  size?: ModalSize;
  isDismissable?: boolean;
  hasCloseButton?: boolean;
  onSubmit?: FormEventHandler<HTMLFormElement>;
  footer?: ReactNode;
  children: ReactNode;
}

export function Modal({
  isOpen,
  onOpenChange,
  title,
  subtitle,
  size,
  isDismissable = true,
  hasCloseButton = true,
  onSubmit,
  footer,
  children,
}: ModalProps) {
  const contentJSX = useMemo(
    () => (
      <>
        <HeroModal.Header>
          <HeroModal.Heading>{title}</HeroModal.Heading>
          {subtitle ? <p className="text-sm text-muted">{subtitle}</p> : null}
        </HeroModal.Header>
        <HeroModal.Body className="flex flex-col gap-4">{children}</HeroModal.Body>
        {footer ? <HeroModal.Footer>{footer}</HeroModal.Footer> : null}
      </>
    ),
    [title, subtitle, children, footer],
  );

  const dialogContentJSX = useMemo(() => {
    if (!onSubmit) {
      return contentJSX;
    }
    return (
      <form onSubmit={onSubmit} noValidate>
        {contentJSX}
      </form>
    );
  }, [onSubmit, contentJSX]);

  return (
    <HeroModal isOpen={isOpen} onOpenChange={onOpenChange}>
      <HeroModal.Backdrop isDismissable={isDismissable}>
        <HeroModal.Container size={size} scroll="inside">
          <HeroModal.Dialog>
            {hasCloseButton ? <HeroModal.CloseTrigger aria-label="Close" /> : null}
            {dialogContentJSX}
          </HeroModal.Dialog>
        </HeroModal.Container>
      </HeroModal.Backdrop>
    </HeroModal>
  );
}
