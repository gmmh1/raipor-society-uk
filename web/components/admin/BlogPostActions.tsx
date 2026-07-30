"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function BlogPostActions({ postId, isPublished }: { postId: string; isPublished: boolean }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handlePublishToggle() {
    setLoading(true);
    await callApi(`/blog/posts/${postId}/publish/`, { body: { is_published: !isPublished } });
    setLoading(false);
    router.refresh();
  }

  async function handleDelete() {
    setLoading(true);
    await callApi(`/blog/posts/${postId}/delete/`);
    setLoading(false);
    router.refresh();
  }

  return (
    <div style={{ display: "flex", gap: 8 }}>
      <button type="button" className="btn btn-ghost" onClick={handlePublishToggle} disabled={loading}>
        {isPublished ? "Unpublish" : "Publish"}
      </button>
      <button type="button" className="btn btn-ghost" onClick={handleDelete} disabled={loading}>
        Delete
      </button>
    </div>
  );
}
