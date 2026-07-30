"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function BlogPostActions({
  postId,
  isPublished,
  lang,
}: {
  postId: string;
  isPublished: boolean;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
        {isPublished ? t("adminBlog.unpublish") : t("adminBlog.publish")}
      </button>
      <button type="button" className="btn btn-ghost" onClick={handleDelete} disabled={loading}>
        {t("adminCommon.delete")}
      </button>
    </div>
  );
}
