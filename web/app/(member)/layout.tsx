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

export default async function MemberLayout({ children }: { children: React.ReactNode }) {
  const [user, lang] = await Promise.all([apiGet<CurrentUser>("/identity/me/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const tabs = [
    { href: "/member/dashboard", label: t("portal.tab.dashboard") },
    { href: "/member/profile", label: t("portal.tab.profile") },
    { href: "/member/membership", label: t("portal.tab.membership") },
    { href: "/member/events", label: t("portal.tab.events") },
    { href: "/member/orders", label: t("portal.tab.orders") },
    { href: "/member/receipts", label: t("portal.tab.receipts") },
    { href: "/member/documents", label: t("portal.tab.documents") },
    { href: "/member/family", label: t("portal.tab.family") },
    { href: "/member/voting", label: t("portal.tab.voting") },
    { href: "/member/chat", label: t("portal.tab.chat") },
    { href: "/member/notifications", label: t("portal.tab.notifications") },
    { href: "/member/assistant", label: t("portal.tab.assistant") },
  ];

  return (
    <PortalShell portalLabel={t("portal.memberLabel")} tabs={tabs} user={user} lang={lang}>
      {children}
    </PortalShell>
  );
}
