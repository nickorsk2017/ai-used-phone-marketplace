"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@heroui/react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useSessionStore } from "@/stores/sessionStore";
import { Alert } from "@/ui/molecules/Alert";
import { TextField } from "@/ui/molecules/forms/TextField";
import { Modal } from "@/ui/organisms/modal/Modal";
import { userFormSchema, type UserFormInput, type UserFormValues } from "@/schemas/myListingsFormSchemas";

interface AuthModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
}

export function AuthModal({ isOpen, onOpenChange }: AuthModalProps) {
  const register = useSessionStore((state) => state.register);
  const [submitFailed, setSubmitFailed] = useState(false);
  const { control, handleSubmit, formState } = useForm<UserFormInput, unknown, UserFormValues>({
    resolver: zodResolver(userFormSchema),
    defaultValues: { first_name: "", last_name: "", whatsapp: "" },
  });

  const submit = handleSubmit(async (values) => {
    setSubmitFailed(false);
    const response = await register(values);
    if (response.success) {
      onOpenChange(false);
    } else {
      setSubmitFailed(true);
    }
  });

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={onOpenChange}
      title="Create your seller profile"
      subtitle="Buyers see your name and WhatsApp number when they click Deal. No registration is needed."
      size="md"
      hasCloseButton={false}
      onSubmit={submit}
      footer={
        <Button type="submit" isPending={formState.isSubmitting} fullWidth>
          Continue
        </Button>
      }
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
      {submitFailed ? <Alert title="Could not create the profile. Please try again." /> : null}
    </Modal>
  );
}
