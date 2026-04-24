"use client";

import type { ReactNode } from "react";
import { QueryProvider } from "./query-provider";
import { I18nProvider } from "./i18n-provider";
import { BootAuth } from "./boot-auth";

export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <QueryProvider>
      <BootAuth>
        <I18nProvider>{children}</I18nProvider>
      </BootAuth>
    </QueryProvider>
  );
}