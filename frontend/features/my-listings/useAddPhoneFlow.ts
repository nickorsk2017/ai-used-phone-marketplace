import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { PhoneService } from "@/services/PhoneService";
import { useMyListingsStore } from "@/stores/myListingsStore";
import {
  listingFormSchema,
  modelNameSchema,
  type ListingFormInput,
  type ListingFormValues,
  type ModelNameValues,
} from "@/schemas/myListingsFormSchemas";

export type SaveError = "rejected" | "rate_limited" | "failed" | null;

export type GenerateError = "rate_limited" | "failed" | null;

const VALIDATION_ERROR_STATUS = 422;

const RATE_LIMIT_STATUS = 429;

const EMPTY_LISTING: ListingFormInput = {
  description: "",
  camera_megapixels: Number.NaN,
  battery_capacity: Number.NaN,
  display_size: Number.NaN,
  condition_note: "",
  condition: undefined as unknown as Entity.PhoneCondition,
  price: Number.NaN,
};

export function useAddPhoneFlow(onOpenChange: (isOpen: boolean) => void) {
  const addListing = useMyListingsStore((state) => state.add);
  const [generated, setGenerated] = useState<Entity.PhoneDescription | null>(null);
  const [generateError, setGenerateError] = useState<GenerateError>(null);
  const [saveError, setSaveError] = useState<SaveError>(null);

  const modelForm = useForm<ModelNameValues>({
    resolver: zodResolver(modelNameSchema),
    defaultValues: { model_name: "" },
  });
  const listingForm = useForm<ListingFormInput, unknown, ListingFormValues>({
    resolver: zodResolver(listingFormSchema),
    defaultValues: EMPTY_LISTING,
  });

  const resetAll = () => {
    modelForm.reset({ model_name: "" });
    listingForm.reset(EMPTY_LISTING);
    setGenerated(null);
    setGenerateError(null);
    setSaveError(null);
  };

  const changeOpen = (isOpen: boolean) => {
    if (!isOpen) {
      resetAll();
    }
    onOpenChange(isOpen);
  };

  const clearGenerated = () => setGenerated(null);

  const generate = modelForm.handleSubmit(async ({ model_name }) => {
    setGenerateError(null);
    setSaveError(null);
    const response = await PhoneService.generateDescription(model_name);
    if (!response.success) {
      setGenerated(null);
      if (response.status === VALIDATION_ERROR_STATUS) {
        modelForm.setError("model_name", { message: "Model not found. Check that the model really exists." });
      } else {
        setGenerateError(response.status === RATE_LIMIT_STATUS ? "rate_limited" : "failed");
      }
      return;
    }
    const description = response.data;
    setGenerated(description);
    listingForm.reset({
      ...EMPTY_LISTING,
      description: description.description,
      camera_megapixels: description.camera_megapixels,
      battery_capacity: description.battery_capacity,
      display_size: description.display_size,
    });
  });

  const publish = listingForm.handleSubmit(async (values) => {
    if (!generated) {
      return;
    }
    setSaveError(null);
    const response = await addListing({
      model_code: generated.model_code,
      model_name: generated.model_name,
      os: generated.os,
      ...values,
    });
    if (response.success) {
      changeOpen(false);
      return;
    }
    if (response.status === VALIDATION_ERROR_STATUS) {
      setSaveError("rejected");
    } else {
      setSaveError(response.status === RATE_LIMIT_STATUS ? "rate_limited" : "failed");
    }
  });

  return {
    modelForm,
    listingForm,
    generated,
    generateError,
    saveError,
    changeOpen,
    clearGenerated,
    generate,
    publish,
  };
}
