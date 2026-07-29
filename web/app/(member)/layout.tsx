import { apiGet } from "@/lib/api";
import { PortalShell } from "@/components/PortalShell";
import { getLang } from "@/lib/i18n/server";

const tabs = [
  { href: "/member/dashboard", label: "Dashboard" },
  { href: "/member/membership", label: "Membership" },
  { href: "/member/events", label: "Events" },
  { href: "/member/orders", label: "Orders" },
  { href: "/member/receipts", label: "Receipts" },
  { href: "/member/documents", label: "Documents" },
  { href: "/member/family", label: "Family" },
  { href: "/member/voting", label: "Voting" },
  { href: "/member/chat", label: "Chat" },
  { href: "/member/notifications", label: "Notifications" },
  { href: "/member/assistant", label: "Assistant" },
];

type CurrentUser = {
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export default async function MemberLayout({ children }: { children: React.ReactNode }) {
  const [user, lang] = await Promise.all([apiGet<CurrentUser>("/identity/me/"), getLang()]);

  return (
    <PortalShell portalLabel="Member Portal" tabs={tabs} user={user} lang={lang}>
      {children}
    </PortalShell>
  );
}
