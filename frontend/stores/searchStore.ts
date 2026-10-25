import { create } from "zustand";
import { SearchService } from "@/services/SearchService";

export type SearchStatus = "idle" | "loading" | "success" | "error";

interface SearchState {
  prompt: string;
  status: SearchStatus;
  results: Entity.Phone[];
  search: (prompt: string) => Promise<void>;
  reset: () => void;
}

let activeController: AbortController | null = null;

export const useSearchStore = create<SearchState>((set) => ({
  prompt: "",
  status: "idle",
  results: [],

  search: async (prompt) => {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;

    set({ prompt, status: "loading" });
    const response = await SearchService.search(prompt, controller.signal);
    if (activeController !== controller) {
      return;
    }
    activeController = null;
    set(response.success ? { status: "success", results: response.data } : { status: "error", results: [] });
  },

  reset: () => {
    activeController?.abort();
    activeController = null;
    set({ prompt: "", status: "idle", results: [] });
  },
}));
