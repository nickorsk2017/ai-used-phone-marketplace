import {
  myListingsResponseSchema,
  phoneContactSchema,
  phoneDescriptionSchema,
  phoneSchema,
} from "@/schemas/phoneSchemas";
import { apiRequest, successResponse } from "@/utils/apiClient";

function phonePath(id: string): string {
  return `/api/phones/${encodeURIComponent(id)}`;
}

export const PhoneService = {
  async getById(id: string): Promise<Api.Response<Entity.Phone | null>> {
    const response = await apiRequest(phonePath(id), { schema: phoneSchema });
    if (!response.success && response.status === 404) {
      return successResponse(null);
    }
    return response;
  },

  async getContact(id: string): Promise<Api.Response<Entity.PhoneContact>> {
    return apiRequest(`${phonePath(id)}/contact`, { schema: phoneContactSchema });
  },

  async getMyListings(): Promise<Api.Response<Entity.Phone[]>> {
    const response = await apiRequest("/api/my-listings", { schema: myListingsResponseSchema });
    return response.success ? successResponse(response.data.listings) : response;
  },

  generateDescription(modelName: string): Promise<Api.Response<Entity.PhoneDescription>> {
    return apiRequest("/api/phones/description", {
      method: "POST",
      body: { model_name: modelName },
      schema: phoneDescriptionSchema,
    });
  },

  create(body: Api.CreatePhoneRequest): Promise<Api.Response<Entity.Phone>> {
    return apiRequest("/api/phones", { method: "POST", body, schema: phoneSchema });
  },

  delete(id: string): Promise<Api.Response<void>> {
    return apiRequest(phonePath(id), { method: "DELETE" });
  },
};
