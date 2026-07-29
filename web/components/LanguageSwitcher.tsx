"use client";

import { useRouter } from "next/navigation";
import { LANG_COOKIE, LANGUAGES, type Lang } from "@/lib/i18n/config";

export function LanguageSwitcher({ lang, dark = false }: { lang: Lang; dark?: boolean }) {
  const router = useRouter();

  function setLang(next: Lang) {
    if (next === lang) return;
    document.cookie = `${LANG_COOKIE}=${next}; path=/; max-age=${60 * 60 * 24 * 365}`;
    router.refresh();
  }

  return (
    <div
      role="group"
      aria-label="Language"
      style={{ display: "flex", gap: 4, alignItems: "center" }}
    >
      {LANGUAGES.map((option) => (
        <button
          key={option.code}
          type="button"
          onClick={() => setLang(option.code)}
          aria-pressed={lang === option.code}
          style={{
            border: "1px solid",
            borderColor: dark ? "rgba(250,248,244,0.35)" : "var(--line)",
            background:
              lang === option.code ? (dark ? "rgba(250,248,244,0.15)" : "var(--ink)") : "transparent",
            color:
              lang === option.code
                ? dark
                  ? "var(--paper)"
                  : "var(--paper)"
                : dark
                  ? "rgba(250,248,244,0.75)"
                  : "var(--ink)",
            borderRadius: 999,
            padding: "5px 12px",
            fontSize: "0.8rem",
            fontWeight: 700,
            cursor: "pointer",
            lineHeight: 1,
          }}
        >
          {option.nativeLabel}
        </button>
      ))}
    </div>
  );
}
