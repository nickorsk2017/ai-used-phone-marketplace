import { create } from "zustand";
import { PhoneService } from "@/services/PhoneService";

export type MyListingsStatus = "idle" | "loading" | "ready" | "error";

interface MyListingsState {
  status: MyListingsStatus;
  listings: Entity.Phone[];
  load: () => Promise<void>;
  add: (body: Api.CreatePhoneRequest) => Promise<Api.Response<Entity.Phone>>;
  remove: (id: string) => Promise<Api.Response<void>>;
}

export const useMyListingsStore = create<MyListingsState>((set) => ({
  status: "idle",
  listings: [],

  load: async () => {
    set({ status: "loading" });
    const response = await PhoneService.getMyListings();
    set(response.success ? { status: "ready", listings: response.data } : { status: "error", listings: [] });
  },

  add: async (body) => {
    const response = await PhoneService.create(body);
    if (!response.success) {
      return response;
    }
    const created = response.data;
    const reloaded = await PhoneService.getMyListings();
    set((state) =>
      reloaded.success
        ? { status: "ready", listings: reloaded.data }
        : { listings: [created, ...state.listings.filter((listing) => listing.id !== created.id)] },
    );
    return response;
  },

  remove: async (id) => {
    const response = await PhoneService.delete(id);
    if (response.success) {
      set((state) => ({ listings: state.listings.filter((listing) => listing.id !== id) }));
    }
    return response;
  },
}));
