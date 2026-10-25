import { searchResponseSchema } from "@/schemas/searchSchemas";
import { apiRequest, successResponse } from "@/utils/apiClient";

export const SEARCH_RESULTS_LIMIT = 20;

export const SearchService = {
  async search(prompt: string, signal?: AbortSignal): Promise<Api.Response<Entity.Phone[]>> {
    const body: Api.SearchRequest = { prompt };
    const response = await apiRequest("/api/search", { method: "POST", body, signal, schema: searchResponseSchema });
    return response.success ? successResponse(response.data.results.slice(0, SEARCH_RESULTS_LIMIT)) : response;
  },
};
