import Link from "next/link";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function SiteFooter({ lang }: { lang: Lang }) {
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <h3>Raipur Society UK</h3>
            <p style={{ color: "rgba(250,248,244,0.65)", maxWidth: "38ch" }}>{t("footer.about")}</p>
          </div>

          <div className="footer-links">
            <h3>{t("footer.explore")}</h3>
            <Link href="/about">{t("footer.aboutLink")}</Link>
            <Link href="/programs">{t("nav.programs")}</Link>
            <Link href="/events">{t("nav.events")}</Link>
            <Link href="/blog">{t("nav.blog")}</Link>
            <Link href="/donate">{t("nav.donate")}</Link>
          </div>

          <div className="footer-links">
            <h3>{t("footer.community")}</h3>
            <Link href="/contact">{t("footer.contactUs")}</Link>
            <Link href="/member/dashboard">{t("nav.memberSignIn")}</Link>
          </div>

          <div className="footer-links">
            <h3>{t("footer.legal")}</h3>
            <Link href="/privacy">{t("footer.privacyLink")}</Link>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Raipur Society UK. {t("footer.rights")}</span>
          <span>{t("footer.registered")}</span>
        </div>
      </div>
    </footer>
  );
}
