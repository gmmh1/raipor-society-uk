import Link from "next/link";
import { LogoutButton } from "@/components/LogoutButton";
import { PortalTabs } from "@/components/PortalTabs";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";
import { BrandMark } from "@/components/BrandMark";
import type { Lang } from "@/lib/i18n/config";

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
  lang,
  children,
}: {
  portalLabel: string;
  tabs: { href: string; label: string }[];
  user: CurrentUser | null;
  lang: Lang;
  children: React.ReactNode;
}) {
  const displayName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") || user?.username || "Member";

  return (
    <div className="portal-shell">
      <div className="portal-topbar">
        <div className="container portal-topbar-inner">
          <Link href="/" className="brand" style={{ color: "var(--chrome-text)" }}>
            <BrandMark size={30} />
            Raipur Society UK
            <span className="portal-label">· {portalLabel}</span>
          </Link>
          <div className="portal-user-group">
            <ThemeToggle dark />
            <LanguageSwitcher lang={lang} dark />
            <span className="portal-user-name">{displayName}</span>
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
