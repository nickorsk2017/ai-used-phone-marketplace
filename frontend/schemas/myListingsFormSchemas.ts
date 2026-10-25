import { z } from "zod";
import { hasGuardrailViolations } from "@/utils/guardrails";
import { phoneConditionSchema } from "./phoneSchemas";

const WHATSAPP_PATTERN = /^\+[1-9]\d{6,14}$/;

export const userFormSchema = z.object({
  first_name: z.string().trim().min(1, "Fill in this field."),
  last_name: z.string().trim().min(1, "Fill in this field."),
  whatsapp: z
    .string()
    .transform((value) => value.replace(/[\s().-]/g, ""))
    .pipe(z.string().regex(WHATSAPP_PATTERN, "Enter the number in international format, for example +1 415 555 2671.")),
});

export type UserFormInput = z.input<typeof userFormSchema>;
export type UserFormValues = z.output<typeof userFormSchema>;

export const modelNameSchema = z.object({
  model_name: z.string().trim().min(1, "Fill in this field."),
});

export type ModelNameValues = z.infer<typeof modelNameSchema>;

const listingText = z
  .string()
  .trim()
  .refine((value) => !hasGuardrailViolations(value), "Remove card numbers, phone numbers and links. Buyers see your WhatsApp number separately.");

const positiveInteger = z
  .number({ error: "Enter a positive whole number." })
  .int("Enter a positive whole number.")
  .positive("Enter a positive whole number.");

export const listingFormSchema = z.object({
  description: listingText.pipe(z.string().min(1, "Fill in this field.")),
  camera_megapixels: positiveInteger,
  battery_capacity: positiveInteger,
  display_size: z
    .number({ error: "Enter a positive number." })
    .positive("Enter a positive number."),
  condition_note: listingText,
  condition: z.enum(phoneConditionSchema.options, { error: "Fill in this field." }),
  price: positiveInteger,
});

export type ListingFormInput = z.input<typeof listingFormSchema>;
export type ListingFormValues = z.output<typeof listingFormSchema>;
