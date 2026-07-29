import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

export default async function ContactPage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("contact.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>{t("contact.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("contact.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid grid-2">
            <div className="card" style={{ padding: 40 }}>
              <h2>{t("contact.emailTitle")}</h2>
              <p style={{ marginTop: 10 }}>{t("contact.emailBody")}</p>
              <a
                href="mailto:hello@raipursociety.uk"
                className="btn btn-primary"
                style={{ marginTop: 22 }}
              >
                hello@raipursociety.uk
              </a>
            </div>

            <div className="card" style={{ padding: 40 }}>
              <h2>{t("contact.memberTitle")}</h2>
              <p style={{ marginTop: 10 }}>{t("contact.memberBody")}</p>
              <a
                href="/member/dashboard"
                className="btn btn-ghost"
                style={{ marginTop: 22 }}
              >
                {t("contact.memberSignIn")}
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
