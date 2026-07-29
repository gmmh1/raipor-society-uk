import { DonateForm } from "@/components/DonateForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const uses = ["events", "youth", "welfare"] as const;

export default async function DonatePage({
  searchParams,
}: {
  searchParams: Promise<{ thanks?: string }>;
}) {
  const [params, lang] = await Promise.all([searchParams, getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("donate.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>{t("donate.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            {t("donate.lede")}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {params.thanks && (
            <p className="form-success" style={{ marginBottom: 20 }}>
              {t("donate.thanks")}
            </p>
          )}
          <div className="grid grid-2" style={{ alignItems: "start" }}>
            <div className="card" style={{ padding: 40 }}>
              <span className="tag">{t("donate.giveOnline")}</span>
              <h2 style={{ marginTop: 14 }}>{t("donate.makeADonation")}</h2>
              <DonateForm />
            </div>

            <div className="grid" style={{ gap: 16 }}>
              {uses.map((key) => (
                <article className="card" key={key}>
                  <h3>{t(`donate.use.${key}.title` as Parameters<typeof translate>[1])}</h3>
                  <p style={{ marginTop: 8 }}>
                    {t(`donate.use.${key}.copy` as Parameters<typeof translate>[1])}
                  </p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
