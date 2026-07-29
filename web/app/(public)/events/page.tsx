import Link from "next/link";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

export default async function EventsPage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("events.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>{t("events.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("events.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div
            className="card"
            style={{
              textAlign: "center",
              padding: "56px 32px",
              maxWidth: 640,
              margin: "0 auto",
            }}
          >
            <span className="tag">{t("events.comingSoon")}</span>
            <h2 style={{ marginTop: 16 }}>{t("events.noneTitle")}</h2>
            <p style={{ marginTop: 10, marginInline: "auto" }}>{t("events.noneBody")}</p>
            <Link href="/contact" className="btn btn-primary" style={{ marginTop: 24 }}>
              {t("events.cta")}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
