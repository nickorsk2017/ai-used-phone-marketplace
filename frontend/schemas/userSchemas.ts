import { z } from "zod";

export const userSchema = z.object({
  id: z.string().min(1),
  whatsapp: z.string().min(1),
  first_name: z.string(),
  last_name: z.string(),
  created_at: z.string(),
});
