import { apiGet } from "@/lib/api";
import { CreateDocumentForm } from "@/components/admin/CreateDocumentForm";
import { UploadDocumentVersionForm } from "@/components/admin/UploadDocumentVersionForm";
import { ArchiveDocumentButton } from "@/components/admin/ArchiveDocumentButton";

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

export default async function AdminDocumentsPage() {
  const documents = await apiGet<DocumentItem[]>("/documents/");

  return (
    <div>
      <span className="eyebrow">Documents</span>
      <h1 style={{ marginTop: 10 }}>Document management</h1>

      <div style={{ marginTop: 24 }}>
        <CreateDocumentForm />
      </div>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(documents ?? []).map((document) => {
          const latest = document.versions[0];
          return (
            <article className="card" key={document.id}>
              <span className="tag">{document.category}</span>
              <span className="tag" style={{ marginLeft: 8 }}>
                {document.visibility}
              </span>
              <h3 style={{ marginTop: 14 }}>{document.title}</h3>
              {document.description && <p style={{ marginTop: 8 }}>{document.description}</p>}
              <p style={{ marginTop: 10, color: "var(--muted)", fontSize: "0.85rem" }}>
                {latest ? `Latest: ${latest.original_filename} (v${latest.version_number})` : "No file uploaded yet."}
              </p>
              <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
                <UploadDocumentVersionForm documentId={document.id} />
                <ArchiveDocumentButton documentId={document.id} />
              </div>
            </article>
          );
        })}
        {!documents?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No documents yet — add one above.
          </div>
        )}
      </div>
    </div>
  );
}
