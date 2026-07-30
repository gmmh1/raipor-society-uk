import { apiGet } from "@/lib/api";
import { PortalShell } from "@/components/PortalShell";
import { getLang } from "@/lib/i18n/server";

const tabs = [
  { href: "/admin/dashboard", label: "Dashboard" },
  { href: "/admin/membership", label: "Membership" },
  { href: "/admin/events", label: "Events" },
  { href: "/admin/shop", label: "Shop" },
  { href: "/admin/finance", label: "Finance" },
  { href: "/admin/governance", label: "Governance" },
  { href: "/admin/documents", label: "Documents" },
];

type CurrentUser = {
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const [user, lang] = await Promise.all([apiGet<CurrentUser>("/identity/me/"), getLang()]);

  return (
    <PortalShell portalLabel="Admin Portal" tabs={tabs} user={user} lang={lang}>
      {children}
    </PortalShell>
  );
}
