import Link from "next/link";
import { LogoutButton } from "@/components/LogoutButton";
import { PortalTabs } from "@/components/PortalTabs";

type CurrentUser = {
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export function PortalShell({
  portalLabel,
  tabs,
  user,
  children,
}: {
  portalLabel: string;
  tabs: { href: string; label: string }[];
  user: CurrentUser | null;
  children: React.ReactNode;
}) {
  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username || "Member";

  return (
    <div className="portal-shell">
      <div className="portal-topbar">
        <div className="container portal-topbar-inner">
          <Link href="/" className="brand" style={{ color: "var(--paper)" }}>
            <span className="brand-mark" aria-hidden="true">
              R
            </span>
            Raipor Society UK
            <span style={{ opacity: 0.6, fontFamily: "var(--font-body)", fontSize: "0.85rem" }}>
              · {portalLabel}
            </span>
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <span style={{ fontSize: "0.9rem", opacity: 0.85 }}>{displayName}</span>
            <LogoutButton />
          </div>
        </div>
      </div>

      <PortalTabs tabs={tabs} />

      <main className="portal-main">
        <div className="container">{children}</div>
      </main>
    </div>
  );
}
