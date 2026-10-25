const usdFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const integerFormatter = new Intl.NumberFormat("en-US");

export function formatPriceUsd(price: number): string {
  return usdFormatter.format(price);
}

export function formatInteger(value: number): string {
  return integerFormatter.format(value);
}
