"use client";

import { Avatar, Button } from "@heroui/react";

interface ProfileButtonProps {
  user: Entity.User;
  onPress: () => void;
}

function initialsOf(user: Entity.User): string {
  return `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
}

/** Opens the edit profile modal: docs/features/MY_LISTING.md#edit-profile-flow. */
export function ProfileButton({ user, onPress }: ProfileButtonProps) {
  const fullName = `${user.first_name} ${user.last_name}`.trim();

  return (
    <Button size="sm" variant="ghost" aria-label={`Edit profile ${fullName}`} onPress={onPress}>
      <Avatar size="sm">
        <Avatar.Fallback>{initialsOf(user)}</Avatar.Fallback>
      </Avatar>
      <span className="hidden max-w-40 truncate sm:inline">{fullName}</span>
    </Button>
  );
}
