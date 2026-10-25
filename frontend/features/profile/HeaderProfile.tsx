"use client";

import { useEffect, useMemo, useState } from "react";
import { AuthModal } from "@/features/my-listings/AuthModal";
import { useSessionStore } from "@/stores/sessionStore";
import { ProfileButton } from "./ProfileButton";

/** User avatar and name in AppHeader: docs/features/MY_LISTING.md#edit-profile-flow. */
export function HeaderProfile() {
  const status = useSessionStore((state) => state.status);
  const user = useSessionStore((state) => state.user);
  const initSession = useSessionStore((state) => state.init);
  const [isProfileModalOpen, setProfileModalOpen] = useState(false);

  useEffect(() => {
    if (status === "checking") {
      void initSession();
    }
  }, [status, initSession]);

  const profileJSX = useMemo(() => {
    if (status !== "ready" || !user) {
      return null;
    }
    return (
      <>
        <ProfileButton user={user} onPress={() => setProfileModalOpen(true)} />
        <AuthModal user={user} isOpen={isProfileModalOpen} onOpenChange={setProfileModalOpen} />
      </>
    );
  }, [status, user, isProfileModalOpen]);

  return profileJSX;
}
