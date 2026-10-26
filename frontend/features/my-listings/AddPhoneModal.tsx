"use client";

import { Button } from "@heroui/react";
import { useMemo } from "react";
import { CONDITION_LABELS, OS_LABELS } from "@/config/phone";
import { Alert } from "@/ui/molecules/Alert";
import { NumberField } from "@/ui/molecules/forms/NumberField";
import { Select } from "@/ui/molecules/forms/Select";
import { TextField } from "@/ui/molecules/forms/TextField";
import { Modal } from "@/ui/organisms/modal/Modal";
import { useAddPhoneFlow } from "./useAddPhoneFlow";

interface AddPhoneModalProps {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
}

const LISTING_FORM_ID = "add-phone-form";

const CONDITION_OPTIONS = (Object.keys(CONDITION_LABELS) as Entity.PhoneCondition[]).map((condition) => ({
  id: condition,
  label: CONDITION_LABELS[condition],
}));

export function AddPhoneModal({ isOpen, onOpenChange }: AddPhoneModalProps) {
  const { modelForm, listingForm, generated, generateError, saveError, changeOpen, clearGenerated, generate, publish } =
    useAddPhoneFlow(onOpenChange);
  const listingControl = listingForm.control;

  const saveErrorJSX = useMemo(() => {
    if (!saveError) {
      return null;
    }
    if (saveError === "rejected") {
      return <Alert title="The listing was not accepted. The description and the condition note may only describe the phone model and its condition. Phone numbers, websites and other contact details are not allowed." />;
    }
    if (saveError === "rate_limited") {
      return <Alert title="Too many requests. Wait 10 seconds and try again." />;
    }
    return <Alert title="The listing was not saved. Please try again." />;
  }, [saveError]);

  const generateErrorJSX = useMemo(() => {
    if (!generateError) {
      return null;
    }
    if (generateError === "rate_limited") {
      return <Alert title="Too many requests. Wait 10 seconds and try again." />;
    }
    return <Alert title="Something went wrong. Please try again later." />;
  }, [generateError]);

  const listingFormJSX = useMemo(() => {
    if (!generated) {
      return null;
    }
    return (
      <form id={LISTING_FORM_ID} onSubmit={publish} noValidate className="flex flex-col gap-4">
        <dl className="grid grid-cols-2 gap-3 rounded-xl bg-surface-secondary p-3">
          <div>
            <dt className="text-xs text-muted">Model name</dt>
            <dd className="font-medium text-foreground">{generated.model_name}</dd>
          </div>
          <div>
            <dt className="text-xs text-muted">OS</dt>
            <dd className="font-medium text-foreground">{OS_LABELS[generated.os]}</dd>
          </div>
        </dl>

        <TextField control={listingControl} name="description" label="Description" rows={5} />

        <div className="grid gap-4 sm:grid-cols-3">
          <NumberField control={listingControl} name="camera_megapixels" label="Camera, MP" />
          <NumberField control={listingControl} name="battery_capacity" label="Battery, mAh" />
          <NumberField control={listingControl} name="display_size" label="Display, inches" fractionDigits={2} />
        </div>

        <TextField
          control={listingControl}
          name="condition_note"
          label="Condition note"
          placeholder="There are scuffs and scratches"
          rows={3}
          autoFocus
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            control={listingControl}
            name="condition"
            label="Condition"
            placeholder="Select the condition"
            options={CONDITION_OPTIONS}
          />
          <NumberField control={listingControl} name="price" label="Price, USD" currency="USD" />
        </div>

        {saveErrorJSX}
      </form>
    );
  }, [generated, publish, listingControl, saveErrorJSX]);

  return (
    <Modal
      isOpen={isOpen}
      onOpenChange={changeOpen}
      title="Add new phone"
      size="lg"
      isDismissable={false}
      footer={
        <>
          <Button variant="tertiary" onPress={() => changeOpen(false)}>
            Cancel
          </Button>
          <Button
            type="submit"
            form={LISTING_FORM_ID}
            isDisabled={!generated}
            isPending={listingForm.formState.isSubmitting}
          >
            Publish
          </Button>
        </>
      }
    >
      <form onSubmit={generate} noValidate className="flex flex-col gap-3 sm:flex-row sm:items-start">
        <div className="flex-1">
          <TextField
            control={modelForm.control}
            name="model_name"
            label="Model name"
            placeholder="iPhone 13 Pro"
            description="AI generates the model description and the specifications. Review them before publishing."
            autoFocus
            onValueChange={clearGenerated}
          />
        </div>
        <Button
          type="submit"
          variant={generated ? "secondary" : "primary"}
          isPending={modelForm.formState.isSubmitting}
          className="sm:mt-6"
        >
          Generate description
        </Button>
      </form>

      {generateErrorJSX}

      {listingFormJSX}
    </Modal>
  );
}
