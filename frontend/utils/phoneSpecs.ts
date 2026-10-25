import { formatInteger } from "./format";

export interface Spec {
  label: string;
  value: string;
}

export function buildPhoneSpecs(phone: Entity.Phone): Spec[] {
  return [
    { label: "Camera", value: `${formatInteger(phone.camera_megapixels)} MP` },
    { label: "Battery", value: `${formatInteger(phone.battery_capacity)} mAh` },
    { label: "Display", value: `${phone.display_size}"` },
  ];
}
