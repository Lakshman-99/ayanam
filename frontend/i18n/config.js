export const locales = ["en", "ta"];
export const defaultLocale = "en";

export function isValidLocale(value) {
  return locales.includes(value);
}
