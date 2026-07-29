import { TopNav } from "@/components/TopNav";
import { SiteFooter } from "@/components/SiteFooter";
import { getLang } from "@/lib/i18n/server";

export default async function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const lang = await getLang();

  return (
    <div className="site-shell">
      <TopNav lang={lang} />
      <div className="site-content">{children}</div>
      <SiteFooter lang={lang} />
    </div>
  );
}
