import { apiGet } from "@/lib/api";
import { ChatPanel } from "@/components/member/ChatPanel";

type Channel = { id: string; name: string; channel_type: string };

export default async function ChatPage() {
  const channels = await apiGet<Channel[]>("/chat/channels/me/");

  return (
    <div>
      <span className="eyebrow">Chat</span>
      <h1 style={{ marginTop: 10 }}>Conversations</h1>
      <ChatPanel channels={channels ?? []} />
    </div>
  );
}
