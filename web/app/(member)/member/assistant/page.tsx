import { AssistantChat } from "@/components/member/AssistantChat";
import { getLang } from "@/lib/i18n/server";

export default async function AssistantPage() {
  const lang = await getLang();
  return <AssistantChat lang={lang} />;
}
