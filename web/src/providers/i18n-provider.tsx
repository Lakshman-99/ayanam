"use client";

import { type ReactNode, useEffect } from "react";
import { I18nextProvider } from "react-i18next";
import { i18n } from "@/lib/i18n/config";
import { useMe } from "@/features/auth/hooks/use-auth";

export function I18nProvider({ children }: { children: ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      <LanguageSync />
      {children}
    </I18nextProvider>
  );
}

function LanguageSync() {
  const { data: user } = useMe();
  useEffect(() => {
    if (user?.language && i18n.language !== user.language) {
      i18n.changeLanguage(user.language);
    }
  }, [user?.language]);
  return null;
}