import { apiGet } from "@/lib/api";
import { PortalShell } from "@/components/PortalShell";

const tabs = [
  { href: "/member/dashboard", label: "Dashboard" },
  { href: "/member/membership", label: "Membership" },
  { href: "/member/events", label: "Events" },
  { href: "/member/documents", label: "Documents" },
  { href: "/member/voting", label: "Voting" },
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
  const user = await apiGet<CurrentUser>("/identity/me/");

  return (
    <PortalShell portalLabel="Member Portal" tabs={tabs} user={user}>
      {children}
    </PortalShell>
  );
}
