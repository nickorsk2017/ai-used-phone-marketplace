import { successResponse } from "@/utils/apiClient";
import { UserService } from "./UserService";

const NO_SESSION_STATUS = 401;

/** Browser session: docs/backend/AUTH.md#session-flow. The Backend owns the session cookie. */
export const AuthService = {
  /** `null` when there is no valid session. */
  async getCurrentUser(): Promise<Api.Response<Entity.User | null>> {
    const response = await UserService.getCurrent();
    if (!response.success && response.status === NO_SESSION_STATUS) {
      return successResponse(null);
    }
    return response;
  },

  /** The Backend sets the session cookie on success. */
  register(body: Api.CreateUserRequest): Promise<Api.Response<Entity.User>> {
    return UserService.create(body);
  },
};
