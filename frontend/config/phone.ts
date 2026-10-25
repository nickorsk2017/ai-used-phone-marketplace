export const CONDITION_LABELS: Record<Entity.PhoneCondition, string> = {
  like_new: "Like new",
  average: "Average condition",
  for_repair: "For repair",
};

export const CONDITION_CHIP_COLORS: Record<
  Entity.PhoneCondition,
  "success" | "default" | "warning"
> = {
  like_new: "success",
  average: "default",
  for_repair: "warning",
};

export const OS_LABELS: Record<Entity.PhoneOs, string> = {
  ios: "iOS",
  android: "Android",
};
