import { userSchema } from "@/schemas/userSchemas";
import { apiRequest } from "@/utils/apiClient";

export const UserService = {
  create(body: Api.CreateUserRequest): Promise<Api.Response<Entity.User>> {
    return apiRequest("/api/users", { method: "POST", body, schema: userSchema });
  },

  getById(id: string): Promise<Api.Response<Entity.User>> {
    return apiRequest(`/api/users/${encodeURIComponent(id)}`, { schema: userSchema });
  },

  update(id: string, body: Api.UpdateUserRequest): Promise<Api.Response<Entity.User>> {
    return apiRequest(`/api/users/${encodeURIComponent(id)}`, { method: "PUT", body, schema: userSchema });
  },
};
