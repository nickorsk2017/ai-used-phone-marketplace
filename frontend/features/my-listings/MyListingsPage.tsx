"use client";

import { Button, EmptyState, Spinner } from "@heroui/react";
import { useEffect, useMemo, useState } from "react";
import { useMyListingsStore } from "@/stores/myListingsStore";
import { useSessionStore } from "@/stores/sessionStore";
import { PageContainer } from "@/ui/layouts/PageContainer";
import { Alert } from "@/ui/molecules/Alert";
import { AddPhoneModal } from "./AddPhoneModal";
import { AuthModal } from "./AuthModal";
import { DeletePhoneDialog } from "./DeletePhoneDialog";
import { MyListingsList } from "./MyListingsList";

export function MyListingsPage() {
  const sessionStatus = useSessionStore((state) => state.status);
  const initSession = useSessionStore((state) => state.init);
  const listingsStatus = useMyListingsStore((state) => state.status);
  const listings = useMyListingsStore((state) => state.listings);
  const loadListings = useMyListingsStore((state) => state.load);

  const [isUserModalDismissed, setUserModalDismissed] = useState(false);
  const [isAddModalOpen, setAddModalOpen] = useState(false);
  const [phoneToDelete, setPhoneToDelete] = useState<Entity.Phone | null>(null);

  useEffect(() => {
    void initSession();
  }, [initSession]);

  useEffect(() => {
    if (sessionStatus === "ready") {
      void loadListings();
    }
  }, [sessionStatus, loadListings]);

  const isReady = sessionStatus === "ready";
  const isUserModalOpen = sessionStatus === "anonymous" && !isUserModalDismissed;

  const addButtonJSX = useMemo(() => {
    if (!isReady) {
      return null;
    }
    return (
      <Button size="lg" onPress={() => setAddModalOpen(true)}>
        Add new phone
      </Button>
    );
  }, [isReady]);

  const sessionContentJSX = useMemo(() => {
    if (sessionStatus === "checking") {
      return (
        <div className="flex justify-center py-12">
          <Spinner aria-label="Loading" />
        </div>
      );
    }
    if (sessionStatus === "anonymous") {
      return (
        <EmptyState className="flex flex-col items-center gap-4 py-12">
          <p className="text-muted">Create a seller profile to add phones for sale.</p>
          <Button onPress={() => setUserModalDismissed(false)}>Create profile</Button>
        </EmptyState>
      );
    }
    if (sessionStatus === "error") {
      return (
        <Alert
          title="Could not load your profile."
          action={
            <Button size="sm" variant="danger-soft" onPress={() => void initSession()}>
              Try again
            </Button>
          }
        />
      );
    }
    if (sessionStatus === "ready") {
      return (
        <MyListingsList
          status={listingsStatus}
          listings={listings}
          onRetry={() => void loadListings()}
          onAdd={() => setAddModalOpen(true)}
          onDelete={setPhoneToDelete}
        />
      );
    }
    return null;
  }, [sessionStatus, listingsStatus, listings, initSession, loadListings]);

  return (
    <PageContainer>
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">My listings</h1>
          <p className="text-muted">Phones you sell. Buyers find them with the search and contact you on WhatsApp.</p>
        </div>
        {addButtonJSX}
      </header>

      {sessionContentJSX}

      <AuthModal
        isOpen={isUserModalOpen}
        onOpenChange={(isOpen) => setUserModalDismissed(!isOpen)}
      />
      <AddPhoneModal isOpen={isAddModalOpen} onOpenChange={setAddModalOpen} />
      <DeletePhoneDialog phone={phoneToDelete} onClose={() => setPhoneToDelete(null)} />
    </PageContainer>
  );
}
