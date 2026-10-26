"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@heroui/react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useSessionStore } from "@/stores/sessionStore";
import { Alert } from "@/ui/molecules/Alert";
import { TextField } from "@/ui/molecules/forms/TextField";
import { Modal } from "@/ui/organisms/modal/Modal";
import { userFormSchema, type UserFormInput, type UserFormValues } from "@/schemas/myListingsFormSchemas";

interface AuthModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  /** Edit mode for this user: docs/features/MY_LISTING.md#edit-profile-flow. Without it the modal creates a user. */
  user?: Entity.User | null;
}

function toFormValues(user: Entity.User | null | undefined): UserFormInput {
  return {
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    whatsapp: user?.whatsapp ?? "",
  };
}

export function AuthModal({ isOpen, onOpenChange, user }: AuthModalProps) {
  const register = useSessionStore((state) => state.register);
  const updateProfile = useSessionStore((state) => state.updateProfile);
  const isEditMode = Boolean(user);
  const [submitFailed, setSubmitFailed] = useState(false);
  const { control, handleSubmit, formState, reset } = useForm<UserFormInput, unknown, UserFormValues>({
    resolver: zodResolver(userFormSchema),
    defaultValues: toFormValues(user),
  });

  useEffect(() => {
    if (isOpen) {
      reset(toFormValues(user));
    }
  }, [isOpen, user, reset]);

  const changeOpen = (nextIsOpen: boolean) => {
    if (!nextIsOpen) {
      setSubmitFailed(false);
    }
    onOpenChange(nextIsOpen);
  };

  const submit = handleSubmit(async (values) => {
    setSubmitFailed(false);
    const response = isEditMode ? await updateProfile(values) : await register(values);
    if (response.success) {
      onOpenChange(false);
    } else {
      setSubmitFailed(true);
    }
  });

  const submitErrorJSX = useMemo(() => {
    if (!submitFailed) {
      return null;
    }
    if (isEditMode) {
      return <Alert title="Could not save the profile. Please try again." />;
    }
    return <Alert title="Could not create the profile. Please try again." />;
  }, [submitFailed, isEditMode]);

  const footerJSX = useMemo(
    () => (
      <Button type="submit" isPending={formState.isSubmitting} fullWidth>
        {isEditMode ? "Save" : "Continue"}
      </Button>
    ),
    [formState.isSubmitting, isEditMode],
  );

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={changeOpen}
      title={isEditMode ? "Edit your seller profile" : "Create your seller profile"}
      subtitle="Buyers see your name and WhatsApp number when they click Deal. No registration is needed."
      size="md"
      hasCloseButton={isEditMode}
      onSubmit={submit}
      footer={footerJSX}
    >
      <TextField control={control} name="first_name" label="First name" autoComplete="given-name" />
      <TextField control={control} name="last_name" label="Last name" autoComplete="family-name" />
      <TextField
        control={control}
        name="whatsapp"
        label="WhatsApp number"
        type="tel"
        autoComplete="tel"
        description="International format, for example +1 415 555 2671."
      />
      {submitErrorJSX}
    </Modal>
  );
}
