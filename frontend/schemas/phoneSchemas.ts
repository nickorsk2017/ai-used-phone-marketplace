import { z } from "zod";

export const phoneOsSchema = z.enum(["ios", "android"]);

export const phoneConditionSchema = z.enum(["like_new", "average", "for_repair"]);

export const phoneDescriptionSchema = z.object({
  model_code: z.string(),
  model_name: z.string().min(1),
  os: phoneOsSchema,
  camera_megapixels: z.number().int().positive(),
  battery_capacity: z.number().int().positive(),
  display_size: z.coerce.number().positive(),
  description: z.string(),
});

export const phoneSchema = phoneDescriptionSchema.extend({
  id: z.string().min(1),
  condition: phoneConditionSchema,
  condition_note: z.string(),
  price: z.number().int().positive(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const phoneContactSchema = z.object({
  whatsapp: z.string().min(1),
  first_name: z.string(),
  last_name: z.string(),
});

export const myListingsResponseSchema = z.object({
  listings: z.array(phoneSchema),
});
