import { getDictionary } from "@/i18n/get-dictionary";
import LoginView from "@/features/auth/views/login-view";

export default async function LoginPage({ params }) {
  const { lang } = await params;
  const dict = await getDictionary(lang);

  return <LoginView dict={dict} lang={lang} />;
}
