import { notFound } from "next/navigation";
import { isValidLocale, locales } from "@/i18n/config";

export function generateStaticParams() {
  return locales.map((lang) => ({ lang }));
}

export default async function LocaleLayout({ children, params }) {
  const { lang } = await params;

  if (!isValidLocale(lang)) {
    notFound();
  }

  return children;
}
