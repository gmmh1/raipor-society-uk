import { RegisterForm } from "@/components/RegisterForm";
import { getLang } from "@/lib/i18n/server";

export default async function RegisterPage() {
  const lang = await getLang();
  return <RegisterForm lang={lang} />;
}
