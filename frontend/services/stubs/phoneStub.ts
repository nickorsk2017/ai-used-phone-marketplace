/**
 * Temporary stub of `GET /api/phones/{id}` and `GET /api/phones/{id}/contact`,
 * used while the Backend is not implemented. Enabled by `NEXT_PUBLIC_API_STUB=true`.
 * Remove this file together with the flag once the Backend endpoints exist.
 */
const STUB_PHONES: Entity.Phone[] = [
  {
    id: "3f6b8f2e-6a1d-4c7e-9b2a-1d5e8c4f7a01",
    model_code: "A2483",
    model_name: "iPhone 13 Pro",
    os: "ios",
    camera_megapixels: 12,
    battery_capacity: 3095,
    display_size: 6.1,
    description:
      "iPhone 13 Pro has a 6.1-inch Super Retina XDR display with ProMotion up to 120 Hz, the A15 Bionic chip and a triple 12 MP camera system with telephoto, wide and ultra wide lenses. It supports 5G, MagSafe charging and Face ID. The stainless steel frame and Ceramic Shield front make it durable for daily use.",
    condition: "like_new",
    condition_note: "Used with a case and a screen protector from day one. No scratches. Battery health 91%. Original box and cable.",
    price: 520,
    created_at: "2026-10-20T14:12:00Z",
    updated_at: "2026-10-20T14:12:00Z",
  },
  {
    id: "8c2d4e6f-1b3a-4d5c-8e7f-2a9b0c1d3e02",
    model_code: "SM-S911U",
    model_name: "Samsung Galaxy S23",
    os: "android",
    camera_megapixels: 50,
    battery_capacity: 3900,
    display_size: 6.1,
    description:
      "Samsung Galaxy S23 has a 6.1-inch Dynamic AMOLED 2X display with a 120 Hz refresh rate, the Snapdragon 8 Gen 2 for Galaxy chip and a 50 MP main camera with optical image stabilization. It has IP68 water resistance, wireless charging and Gorilla Glass Victus 2 on both sides.",
    condition: "average",
    condition_note: "There are scuffs on the frame and a light scratch on the back glass. The screen has no scratches.",
    price: 380,
    created_at: "2026-10-22T09:40:00Z",
    updated_at: "2026-10-23T18:05:00Z",
  },
  {
    id: "d1e2f3a4-5b6c-4d7e-8f90-a1b2c3d4e503",
    model_code: "GA04848-US",
    model_name: "Google Pixel 7",
    os: "android",
    camera_megapixels: 50,
    battery_capacity: 4355,
    display_size: 6.3,
    description:
      "Google Pixel 7 has a 6.3-inch OLED display with a 90 Hz refresh rate, the Google Tensor G2 chip and a 50 MP main camera with Night Sight and Real Tone. It receives Android updates directly from Google and supports wireless charging.",
    condition: "for_repair",
    condition_note: "The screen is cracked in the bottom corner, touch works. The battery holds a charge for about half a day.",
    price: 120,
    created_at: "2026-10-24T11:20:00Z",
    updated_at: "2026-10-24T11:20:00Z",
  },
];

const STUB_CONTACTS: Record<string, Entity.PhoneContact> = {
  "3f6b8f2e-6a1d-4c7e-9b2a-1d5e8c4f7a01": { whatsapp: "+14155552671", first_name: "Emily", last_name: "Carter" },
  "8c2d4e6f-1b3a-4d5c-8e7f-2a9b0c1d3e02": { whatsapp: "+13125550148", first_name: "Daniel", last_name: "Reyes" },
  "d1e2f3a4-5b6c-4d7e-8f90-a1b2c3d4e503": { whatsapp: "+12065550193", first_name: "Olivia", last_name: "Brooks" },
};

export const STUB_PHONE_IDS = STUB_PHONES.map((phone) => phone.id);

export function getStubPhone(id: string): Entity.Phone | null {
  return STUB_PHONES.find((phone) => phone.id === id) ?? null;
}

export function getStubContact(id: string): Entity.PhoneContact | null {
  return STUB_CONTACTS[id] ?? null;
}
