import { notFound } from "next/navigation";
import ClientShell from "@/features/astrology/shell/client-shell";
import { isValidLocale } from "@/i18n/config";
import { getDictionary } from "@/i18n/get-dictionary";

export default async function LocalePage({ params }) {
  const { lang } = await params;

  if (!isValidLocale(lang)) {
    notFound();
  }

  const dict = await getDictionary(lang);

  return <ClientShell dict={dict} currentLang={lang} />;
}
