import { apiGet } from "@/lib/api";
import { DownloadDocumentButton } from "@/components/member/DownloadDocumentButton";

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
  const documents = await apiGet<DocumentItem[]>("/documents/");

  return (
    <div>
      <span className="eyebrow">Documents</span>
      <h1 style={{ marginTop: 10 }}>Society documents</h1>
      <p className="lede" style={{ marginTop: 10 }}>
        Policies, minutes, and forms shared with members.
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
                  <DownloadDocumentButton documentId={document.id} versionId={latest.id} />
                ) : (
                  <span style={{ color: "var(--muted)", fontSize: "0.9rem" }}>
                    No file uploaded yet.
                  </span>
                )}
              </div>
            </article>
          );
        })}
        {!documents?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No documents shared with you yet.
          </div>
        )}
      </div>
    </div>
  );
}
