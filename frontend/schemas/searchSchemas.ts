import { z } from "zod";
import { phoneSchema } from "./phoneSchemas";

export const searchResponseSchema = z.object({
  results: z.array(phoneSchema),
});
