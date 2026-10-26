import { create } from "zustand";
import { SearchService } from "@/services/SearchService";

export type SearchStatus = "idle" | "loading" | "success" | "error";

export type SearchError = "rejected" | "rate_limited" | "failed";

const VALIDATION_ERROR_STATUS = 422;
const RATE_LIMIT_STATUS = 429;

function toSearchError(status: number): SearchError {
  if (status === VALIDATION_ERROR_STATUS) {
    return "rejected";
  }
  return status === RATE_LIMIT_STATUS ? "rate_limited" : "failed";
}

interface SearchState {
  prompt: string;
  status: SearchStatus;
  results: Entity.Phone[];
  clarification: string | null;
  error: SearchError | null;
  search: (prompt: string) => Promise<void>;
  reset: () => void;
}

let activeController: AbortController | null = null;

export const useSearchStore = create<SearchState>((set) => ({
  prompt: "",
  status: "idle",
  results: [],
  clarification: null,
  error: null,

  search: async (prompt) => {
    activeController?.abort();
    const controller = new AbortController();
    activeController = controller;

    set({ prompt, status: "loading", error: null });
    const response = await SearchService.search(prompt, controller.signal);
    if (activeController !== controller) {
      return;
    }
    activeController = null;
    set(
      response.success
        ? {
            status: "success",
            results: response.data.results,
            clarification: response.data.clarification ?? null,
            error: null,
          }
        : { status: "error", results: [], clarification: null, error: toSearchError(response.status) },
    );
  },

  reset: () => {
    activeController?.abort();
    activeController = null;
    set({ prompt: "", status: "idle", results: [], clarification: null, error: null });
  },
}));
