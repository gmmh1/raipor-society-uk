import { apiGet } from "@/lib/api";
import { PortalShell } from "@/components/PortalShell";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type CurrentUser = {
  username: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const [user, lang] = await Promise.all([apiGet<CurrentUser>("/identity/me/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const tabs = [
    { href: "/admin/dashboard", label: t("portal.tab.dashboard") },
    { href: "/admin/membership", label: t("portal.tab.membership") },
    { href: "/admin/committees", label: t("portal.tab.committees") },
    { href: "/admin/events", label: t("portal.tab.events") },
    { href: "/admin/blog", label: t("portal.tab.news") },
    { href: "/admin/timeline", label: t("portal.tab.timeline") },
    { href: "/admin/shop", label: t("portal.tab.shop") },
    { href: "/admin/finance", label: t("portal.tab.finance") },
    { href: "/admin/governance", label: t("portal.tab.governance") },
    { href: "/admin/documents", label: t("portal.tab.documents") },
  ];

  return (
    <PortalShell portalLabel={t("portal.adminLabel")} tabs={tabs} user={user} lang={lang}>
      {children}
    </PortalShell>
  );
}
