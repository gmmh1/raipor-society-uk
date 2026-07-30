import { apiGet } from "@/lib/api";
import { CreateBlogPostForm } from "@/components/admin/CreateBlogPostForm";
import { BlogPostActions } from "@/components/admin/BlogPostActions";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type BlogPost = {
  id: string;
  title: string;
  author_name: string;
  is_published: boolean;
  published_at: string | null;
  created_at: string;
};

type Paginated<T> = { count: number; results: T[] };

export default async function AdminBlogPage() {
  const [page, lang] = await Promise.all([
    apiGet<Paginated<BlogPost>>("/blog/posts/admin/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  function formatDate(value: string | null) {
    if (!value) return "—";
    return new Date(value).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <div>
      <span className="eyebrow">{t("adminBlog.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminBlog.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreateBlogPostForm />
      </div>

      <h2 style={{ marginTop: 40 }}>{t("adminBlog.allPosts")}</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("adminBlog.colTitle")}</th>
              <th>{t("adminBlog.colAuthor")}</th>
              <th>{t("adminCommon.status")}</th>
              <th>{t("adminBlog.colPublished")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(page?.results ?? []).map((post) => (
              <tr key={post.id}>
                <td>{post.title}</td>
                <td>{post.author_name || "—"}</td>
                <td>
                  <span className={`status-pill status-${post.is_published ? "active" : "pending"}`}>
                    {post.is_published ? t("adminCommon.published") : t("adminCommon.draft")}
                  </span>
                </td>
                <td>{formatDate(post.published_at)}</td>
                <td>
                  <BlogPostActions postId={post.id} isPublished={post.is_published} />
                </td>
              </tr>
            ))}
            {!page?.results?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  {t("adminBlog.noneYet")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
