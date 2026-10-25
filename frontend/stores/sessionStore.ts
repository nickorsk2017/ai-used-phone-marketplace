import { create } from "zustand";
import { AuthService } from "@/services/AuthService";
import { UserService } from "@/services/UserService";
import { errorResponse } from "@/utils/apiClient";

export type SessionStatus = "checking" | "anonymous" | "ready" | "error";

const NO_USER_STATUS = 401;

let pendingInit: Promise<void> | null = null;

async function loadSession(set: (state: Pick<SessionState, "status" | "user">) => void): Promise<void> {
  set({ status: "checking", user: null });
  const response = await AuthService.getCurrentUser();
  if (!response.success) {
    set({ status: "error", user: null });
    return;
  }
  set(response.data ? { status: "ready", user: response.data } : { status: "anonymous", user: null });
}

interface SessionState {
  status: SessionStatus;
  user: Entity.User | null;
  init: () => Promise<void>;
  register: (body: Api.CreateUserRequest) => Promise<Api.Response<Entity.User>>;
  updateProfile: (body: Api.UpdateUserRequest) => Promise<Api.Response<Entity.User>>;
}

/** Browser session flow: docs/backend/AUTH.md#session-flow. */
export const useSessionStore = create<SessionState>((set, get) => ({
  status: "checking",
  user: null,

  /** The page and the header call it together: one request is shared. */
  init: () => {
    pendingInit ??= loadSession(set).finally(() => {
      pendingInit = null;
    });
    return pendingInit;
  },

  register: async (body) => {
    const response = await AuthService.register(body);
    if (response.success) {
      set({ status: "ready", user: response.data });
    }
    return response;
  },

  /** Edit profile flow: docs/features/MY_LISTING.md#edit-profile-flow. */
  updateProfile: async (body) => {
    const currentUser = get().user;
    if (!currentUser) {
      return errorResponse(NO_USER_STATUS, "No user in the session");
    }
    const response = await UserService.update(currentUser.id, body);
    if (response.success) {
      set({ user: response.data });
    }
    return response;
  },
}));
