import { successResponse } from "@/utils/apiClient";
import { clearUserId, getUserId, setUserId } from "@/utils/session";
import { UserService } from "./UserService";

const USER_NOT_FOUND_STATUS = 404;

export const AuthService = {
  async getCurrentUser(): Promise<Api.Response<Entity.User | null>> {
    const userId = getUserId();
    if (!userId) {
      return successResponse(null);
    }
    const response = await UserService.getById(userId);
    if (!response.success && response.status === USER_NOT_FOUND_STATUS) {
      clearUserId();
      return successResponse(null);
    }
    return response;
  },

  async register(body: Api.CreateUserRequest): Promise<Api.Response<Entity.User>> {
    const response = await UserService.create(body);
    if (response.success) {
      setUserId(response.data.id);
    }
    return response;
  },
};
