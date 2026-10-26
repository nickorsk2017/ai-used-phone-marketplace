import { userSchema } from "@/schemas/userSchemas";
import { apiRequest } from "@/utils/apiClient";

/** User of the session cookie: docs/backend/API.md. */
export const UserService = {
  create(body: Api.CreateUserRequest): Promise<Api.Response<Entity.User>> {
    return apiRequest("/api/users", { method: "POST", body, schema: userSchema });
  },

  getCurrent(): Promise<Api.Response<Entity.User>> {
    return apiRequest("/api/users/me", { schema: userSchema });
  },

  updateCurrent(body: Api.UpdateUserRequest): Promise<Api.Response<Entity.User>> {
    return apiRequest("/api/users/me", { method: "PUT", body, schema: userSchema });
  },
};
