import { apiGet } from "@/lib/api";
import { DownloadDocumentButton } from "@/components/member/DownloadDocumentButton";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type DocumentVersion = {
  id: string;
  version_number: number;
  original_filename: string;
  size_bytes: number;
};

type DocumentItem = {
  id: string;
  title: string;
  description: string;
  category: string;
  visibility: string;
  versions: DocumentVersion[];
};

export default async function MemberDocumentsPage() {
  const [documents, lang] = await Promise.all([apiGet<DocumentItem[]>("/documents/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberDocuments.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberDocuments.title")}</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        {t("memberDocuments.lede")}
      </p>

      <div className="grid grid-2" style={{ marginTop: 28 }}>
        {(documents ?? []).map((document) => {
          const latest = document.versions[0];
          return (
            <article className="card" key={document.id}>
              <span className="tag">{document.category}</span>
              <h3 style={{ marginTop: 14 }}>{document.title}</h3>
              {document.description && <p style={{ marginTop: 8 }}>{document.description}</p>}
              <div style={{ marginTop: 18 }}>
                {latest ? (
                  <DownloadDocumentButton documentId={document.id} versionId={latest.id} lang={lang} />
                ) : (
                  <span style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
                    {t("memberDocuments.noFile")}
                  </span>
                )}
              </div>
            </article>
          );
        })}
        {!documents?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            {t("memberDocuments.noneYet")}
          </div>
        )}
      </div>
    </div>
  );
}
