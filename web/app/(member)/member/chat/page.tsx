import { apiGet } from "@/lib/api";
import { ChatPanel } from "@/components/member/ChatPanel";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Channel = { id: string; name: string; channel_type: string };

export default async function ChatPage() {
  const [channels, lang] = await Promise.all([
    apiGet<Channel[]>("/chat/channels/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberChat.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberChat.title")}</h1>
      <ChatPanel channels={channels ?? []} lang={lang} />
    </div>
  );
}
