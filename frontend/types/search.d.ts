declare namespace Api {
  interface SearchRequest {
    prompt: string;
  }

  type SearchResponse = import("zod").infer<typeof import("@/schemas/searchSchemas").searchResponseSchema>;
}
