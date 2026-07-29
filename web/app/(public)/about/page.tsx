import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const values = ["open", "member", "lasting"] as const;

export default async function AboutPage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("about.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>{t("about.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("about.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{t("about.workEyebrow")}</span>
            <h2>{t("about.workTitle")}</h2>
          </div>
          <div className="grid grid-2">
            {values.map((key) => (
              <article className="card" key={key}>
                <h3>{t(`about.value.${key}.title` as Parameters<typeof translate>[1])}</h3>
                <p style={{ marginTop: 8 }}>
                  {t(`about.value.${key}.copy` as Parameters<typeof translate>[1])}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="card" style={{ padding: 40 }}>
            <span className="eyebrow">{t("about.governanceEyebrow")}</span>
            <h2 style={{ marginTop: 14 }}>{t("about.governanceTitle")}</h2>
            <p style={{ marginTop: 12, maxWidth: "60ch" }}>{t("about.governanceBody")}</p>
          </div>
        </div>
      </section>
    </main>
  );
}
