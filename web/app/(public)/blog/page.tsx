import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type BlogPost = {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  cover_image_url: string;
  author_name: string;
  published_at: string;
};

async function getPosts(): Promise<BlogPost[]> {
  try {
    const res = await fetch(`${API_BASE}/blog/posts/`, { cache: "no-store" });
    if (!res.ok) return [];
    return (await res.json()) as BlogPost[];
  } catch {
    return [];
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default async function BlogPage() {
  const posts = await getPosts();

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">News</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>Stories from the society.</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Updates, recaps, and announcements from across the community.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid grid-2">
            {posts.map((post) => (
              <Link href={`/blog/${post.slug}`} className="card" key={post.id}>
                {post.cover_image_url && (
                  <img
                    src={post.cover_image_url}
                    alt=""
                    style={{
                      width: "100%",
                      aspectRatio: "16 / 9",
                      objectFit: "cover",
                      borderRadius: "var(--radius-sm)",
                      marginBottom: 14,
                    }}
                  />
                )}
                <span className="tag">{formatDate(post.published_at)}</span>
                <h3 style={{ marginTop: 14 }}>{post.title}</h3>
                {post.excerpt && <p style={{ marginTop: 8 }}>{post.excerpt}</p>}
                {post.author_name && (
                  <p style={{ marginTop: 10, fontSize: "0.85rem", color: "var(--muted)" }}>
                    By {post.author_name}
                  </p>
                )}
              </Link>
            ))}
            {!posts.length && (
              <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
                No news posted yet — check back soon.
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
