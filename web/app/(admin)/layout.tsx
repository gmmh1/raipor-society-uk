import { apiGet } from "@/lib/api";
import { PortalShell } from "@/components/PortalShell";

const tabs = [
  { href: "/admin/dashboard", label: "Dashboard" },
  { href: "/admin/membership", label: "Membership" },
  { href: "/admin/finance", label: "Finance" },
  { href: "/admin/governance", label: "Governance" },
];

type CurrentUser = {
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const user = await apiGet<CurrentUser>("/identity/me/");

  return (
    <PortalShell portalLabel="Admin Portal" tabs={tabs} user={user}>
      {children}
    </PortalShell>
  );
}
