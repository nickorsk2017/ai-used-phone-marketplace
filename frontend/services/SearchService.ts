import { searchResponseSchema } from "@/schemas/searchSchemas";
import { apiRequest, successResponse } from "@/utils/apiClient";

export const SEARCH_RESULTS_LIMIT = 20;

export const SearchService = {
  async search(prompt: string, signal?: AbortSignal): Promise<Api.Response<Api.SearchResponse>> {
    const body: Api.SearchRequest = { prompt };
    const response = await apiRequest("/api/search", { method: "POST", body, signal, schema: searchResponseSchema });
    if (!response.success) {
      return response;
    }
    return successResponse({ ...response.data, results: response.data.results.slice(0, SEARCH_RESULTS_LIMIT) });
  },
};
