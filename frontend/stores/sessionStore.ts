import { create } from "zustand";
import { AuthService } from "@/services/AuthService";

export type SessionStatus = "checking" | "anonymous" | "ready" | "error";

interface SessionState {
  status: SessionStatus;
  user: Entity.User | null;
  init: () => Promise<void>;
  register: (body: Api.CreateUserRequest) => Promise<Api.Response<Entity.User>>;
}

/** Browser session flow: docs/backend/AUTH.md#session-flow. */
export const useSessionStore = create<SessionState>((set) => ({
  status: "checking",
  user: null,

  init: async () => {
    set({ status: "checking" });
    const response = await AuthService.getCurrentUser();
    if (!response.success) {
      set({ status: "error", user: null });
      return;
    }
    set(response.data ? { status: "ready", user: response.data } : { status: "anonymous", user: null });
  },

  register: async (body) => {
    const response = await AuthService.register(body);
    if (response.success) {
      set({ status: "ready", user: response.data });
    }
    return response;
  },
}));
