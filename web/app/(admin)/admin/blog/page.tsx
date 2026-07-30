import { apiGet } from "@/lib/api";
import { CreateBlogPostForm } from "@/components/admin/CreateBlogPostForm";
import { BlogPostActions } from "@/components/admin/BlogPostActions";

type BlogPost = {
  id: string;
  title: string;
  author_name: string;
  is_published: boolean;
  published_at: string | null;
  created_at: string;
};

type Paginated<T> = { count: number; results: T[] };

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

export default async function AdminBlogPage() {
  const page = await apiGet<Paginated<BlogPost>>("/blog/posts/admin/");

  return (
    <div>
      <span className="eyebrow">News</span>
      <h1 style={{ marginTop: 10 }}>Blog & news administration</h1>

      <div style={{ marginTop: 24 }}>
        <CreateBlogPostForm />
      </div>

      <h2 style={{ marginTop: 40 }}>All posts</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Author</th>
              <th>Status</th>
              <th>Published</th>
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
                    {post.is_published ? "published" : "draft"}
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
                  No posts yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
