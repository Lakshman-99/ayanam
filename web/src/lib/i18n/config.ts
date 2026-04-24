"use client";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import enCommon from "./locales/en/common.json";
import enAuth from "./locales/en/auth.json";
import taCommon from "./locales/ta/common.json";
import taAuth from "./locales/ta/auth.json";

export const SUPPORTED_LANGUAGES = ["en", "ta"] as const;
export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export const DEFAULT_NAMESPACE = "common";
export const NAMESPACES = ["common", "auth"] as const;

if (!i18n.isInitialized) {
  i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
      fallbackLng: "en",
      supportedLngs: SUPPORTED_LANGUAGES,
      defaultNS: DEFAULT_NAMESPACE,
      ns: NAMESPACES,
      resources: {
        en: { common: enCommon, auth: enAuth },
        ta: { common: taCommon, auth: taAuth },
      },
      interpolation: {
        escapeValue: false, // React already escapes
      },
      detection: {
        // Priority order: user-set cookie → browser setting
        order: ["cookie", "navigator"],
        caches: ["cookie"],
        lookupCookie: "aynam_lang",
        cookieMinutes: 60 * 24 * 365, // 1 year
      },
      react: {
        useSuspense: false, // avoids SSR edge cases
      },
    });
}

export { i18n };