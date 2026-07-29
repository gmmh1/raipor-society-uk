import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const programs = ["culture", "youth", "welfare", "gatherings", "learning", "governance"] as const;

export default async function ProgramsPage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("programs.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>{t("programs.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("programs.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid grid-2">
            {programs.map((key) => (
              <article className="card" key={key}>
                <span className="tag">{t(`programs.${key}.tag` as Parameters<typeof translate>[1])}</span>
                <h3 style={{ marginTop: 14 }}>
                  {t(`programs.${key}.title` as Parameters<typeof translate>[1])}
                </h3>
                <p style={{ marginTop: 8 }}>
                  {t(`programs.${key}.copy` as Parameters<typeof translate>[1])}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
