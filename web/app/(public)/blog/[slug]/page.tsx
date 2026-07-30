import Link from "next/link";
import { notFound } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type BlogPost = {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  body: string;
  cover_image_url: string;
  author_name: string;
  published_at: string;
};

async function getPost(slug: string): Promise<BlogPost | null> {
  try {
    const res = await fetch(`${API_BASE}/blog/posts/${slug}/`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as BlogPost;
  } catch {
    return null;
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);

  if (!post) {
    notFound();
  }

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container" style={{ maxWidth: 760 }}>
          <Link href="/blog" className="eyebrow">
            ← News
          </Link>
          <h1 style={{ marginTop: 16 }}>{post.title}</h1>
          <p style={{ marginTop: 12, color: "var(--muted)" }}>
            {formatDate(post.published_at)}
            {post.author_name ? ` · By ${post.author_name}` : ""}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container" style={{ maxWidth: 760 }}>
          {post.cover_image_url && (
            <img
              src={post.cover_image_url}
              alt=""
              style={{
                width: "100%",
                aspectRatio: "16 / 9",
                objectFit: "cover",
                borderRadius: "var(--radius)",
                marginBottom: 32,
              }}
            />
          )}
          <div style={{ whiteSpace: "pre-wrap", color: "var(--ink-soft)", lineHeight: 1.75 }}>
            {post.body}
          </div>
        </div>
      </section>
    </main>
  );
}
