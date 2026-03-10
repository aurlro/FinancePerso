import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const CURRENCY_MAP: Record<string, { locale: string; currency: string }> = {
  EUR: { locale: "fr-FR", currency: "EUR" },
  USD: { locale: "en-US", currency: "USD" },
  GBP: { locale: "en-GB", currency: "GBP" },
  CHF: { locale: "fr-CH", currency: "CHF" },
};

export function formatCurrency(amount: number, currencyCode: string = "EUR"): string {
  const config = CURRENCY_MAP[currencyCode] || CURRENCY_MAP.EUR;
  return amount.toLocaleString(config.locale, {
    style: "currency",
    currency: config.currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
