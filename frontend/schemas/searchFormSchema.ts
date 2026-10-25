import { z } from "zod";

export const searchFormSchema = z.object({
  prompt: z.string().trim().min(1),
});

export type SearchFormValues = z.infer<typeof searchFormSchema>;
