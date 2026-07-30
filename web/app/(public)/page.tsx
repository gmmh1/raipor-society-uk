import Link from "next/link";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const pillars = ["unity", "culture", "friendship", "progress"] as const;
const programs = ["culture", "youth", "welfare", "gatherings"] as const;

export default async function HomePage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="hero">
        <div className="container hero-inner">
          <span className="eyebrow">{t("home.eyebrow")}</span>
          <h1>
            {t("home.heroTitlePre")} <em>{t("home.heroTitleEm")}</em> {t("home.heroTitlePost")}
          </h1>
          <p>{t("home.heroBody")}</p>
          <div className="hero-actions">
            <Link href="/register" className="btn btn-primary">
              {t("home.joinCta")}
            </Link>
            <Link href="/programs" className="btn btn-ghost-dark">
              {t("home.programsCta")}
            </Link>
          </div>
        </div>
      </section>

      <div className="weave-divider" aria-hidden="true" />

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{t("home.pillarsEyebrow")}</span>
            <h2>{t("home.pillarsTitle")}</h2>
          </div>
          <div className="grid grid-4">
            {pillars.map((key) => (
              <article className="pillar" key={key}>
                <span className="pillar-index" aria-hidden="true">
                  {t(`home.pillar.${key}.title` as Parameters<typeof translate>[1]).slice(0, 1)}
                </span>
                <h3>{t(`home.pillar.${key}.title` as Parameters<typeof translate>[1])}</h3>
                <p>{t(`home.pillar.${key}.copy` as Parameters<typeof translate>[1])}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">{t("home.programsEyebrow")}</span>
            <h2>{t("home.programsTitle")}</h2>
          </div>
          <div className="grid grid-2">
            {programs.map((key) => (
              <article className="card" key={key}>
                <span className="tag">{t(`home.program.${key}.tag` as Parameters<typeof translate>[1])}</span>
                <h3 style={{ marginTop: 14 }}>
                  {t(`home.program.${key}.title` as Parameters<typeof translate>[1])}
                </h3>
                <p style={{ marginTop: 8 }}>
                  {t(`home.program.${key}.copy` as Parameters<typeof translate>[1])}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="cta-banner">
            <div style={{ maxWidth: 480, position: "relative" }}>
              <h2 style={{ color: "var(--chrome-text)" }}>{t("home.ctaTitle")}</h2>
              <p style={{ color: "rgba(250,248,244,0.75)", marginTop: 10 }}>{t("home.ctaBody")}</p>
            </div>
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap", position: "relative" }}>
              <Link href="/contact" className="btn btn-primary">
                {t("home.ctaContact")}
              </Link>
              <Link href="/donate" className="btn btn-ghost-dark">
                {t("home.ctaDonate")}
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
