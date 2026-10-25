import { testPhoneDescription } from "./testPhoneDescription";

export const testListing: Entity.Phone = {
  ...testPhoneDescription,
  id: "p-1",
  condition: "average",
  condition_note: "Light scratches",
  price: 450,
  created_at: "2026-10-01T10:00:00Z",
  updated_at: "2026-10-01T10:00:00Z",
};
