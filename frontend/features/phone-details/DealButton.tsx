"use client";

import { Button, Skeleton } from "@heroui/react";
import { useCallback, useMemo, useRef, useState } from "react";
import { PhoneService } from "@/services/PhoneService";
import { Alert } from "@/ui/molecules/Alert";
import { Modal } from "@/ui/organisms/modal/Modal";

type ContactState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; contact: Entity.PhoneContact }
  | { status: "error" };

type CopyState = "idle" | "copied" | "error";

interface DealButtonProps {
  phoneId: string;
}

export function DealButton({ phoneId }: DealButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [contactState, setContactState] = useState<ContactState>({ status: "idle" });
  const [copyState, setCopyState] = useState<CopyState>("idle");
  const requestId = useRef(0);

  const loadContact = useCallback(async () => {
    const current = ++requestId.current;
    setContactState({ status: "loading" });
    const response = await PhoneService.getContact(phoneId);
    if (current !== requestId.current) {
      return;
    }
    setContactState(response.success ? { status: "ready", contact: response.data } : { status: "error" });
  }, [phoneId]);

  const open = () => {
    setCopyState("idle");
    setIsOpen(true);
    if (contactState.status !== "ready" && contactState.status !== "loading") {
      void loadContact();
    }
  };

  const copy = useCallback(async (whatsapp: string) => {
    try {
      await navigator.clipboard.writeText(whatsapp);
      setCopyState("copied");
    } catch {
      setCopyState("error");
    }
  }, []);

  const retryButtonJSX = useMemo(() => {
    if (contactState.status !== "error") {
      return null;
    }
    return (
      <Button variant="secondary" onPress={() => void loadContact()}>
        Try again
      </Button>
    );
  }, [contactState.status, loadContact]);

  const copyButtonJSX = useMemo(() => {
    if (contactState.status !== "ready") {
      return null;
    }
    return (
      <Button onPress={() => void copy(contactState.contact.whatsapp)}>
        {copyState === "copied" ? "Copied" : "Copy WhatsApp number"}
      </Button>
    );
  }, [contactState, copyState, copy]);

  return (
    <>
      <Button size="lg" onPress={open} className="w-full sm:w-auto">
        Deal
      </Button>
      <Modal
        isOpen={isOpen}
        onOpenChange={setIsOpen}
        title="Contact the seller"
        footer={
          <>
            {retryButtonJSX}
            {copyButtonJSX}
          </>
        }
      >
        <p className="text-sm text-muted">Write to the seller on WhatsApp to agree on the deal.</p>
        <ContactBody state={contactState} copyState={copyState} />
      </Modal>
    </>
  );
}

function ContactBody({ state, copyState }: { state: ContactState; copyState: CopyState }) {
  if (state.status === "error") {
    return <Alert title="Could not load the contact. Please try again." />;
  }

  if (state.status !== "ready") {
    return (
      <div className="flex flex-col gap-3" aria-busy="true">
        <Skeleton className="h-4 w-1/3 rounded-lg" />
        <Skeleton className="h-7 w-2/3 rounded-lg" />
      </div>
    );
  }

  const { contact } = state;
  return (
    <div className="flex flex-col gap-3">
      <dl className="flex flex-col gap-3 text-foreground">
        <div className="flex flex-col gap-1">
          <dt className="text-xs text-muted">Seller</dt>
          <dd className="font-medium">{`${contact.first_name} ${contact.last_name}`}</dd>
        </div>
        <div className="flex flex-col gap-1">
          <dt className="text-xs text-muted">WhatsApp number</dt>
          <dd className="text-2xl font-semibold tabular-nums select-all">{contact.whatsapp}</dd>
        </div>
      </dl>
      <p role="status" className="text-sm text-danger">
        {copyState === "error" ? "Could not copy the number. Copy it manually." : null}
      </p>
    </div>
  );
}
