import { defaultLocale, isValidLocale } from "@/i18n/config";

const dictionaries = {
  en: () => import("@/dictionaries/en.json").then((module) => module.default),
  ta: () => import("@/dictionaries/ta.json").then((module) => module.default),
};

export async function getDictionary(locale) {
  const safeLocale = isValidLocale(locale) ? locale : defaultLocale;
  return dictionaries[safeLocale]();
}
