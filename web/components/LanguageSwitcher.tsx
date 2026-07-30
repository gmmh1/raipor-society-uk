"use client";

import { LANG_COOKIE, LANGUAGES, type Lang } from "@/lib/i18n/config";

export function LanguageSwitcher({ lang, dark = false }: { lang: Lang; dark?: boolean }) {
  const other = LANGUAGES.find((option) => option.code !== lang) ?? LANGUAGES[0];

  function toggle() {
    document.cookie = `${LANG_COOKIE}=${other.code}; path=/; max-age=${60 * 60 * 24 * 365}`;
    // router.refresh() alone leaves the Next.js Router Cache serving the
    // previous language's RSC payload for this URL — a full reload forces a
    // genuine new request, which the server (confirmed via curl) renders
    // correctly for the new cookie value every time.
    window.location.reload();
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className={`lang-toggle${dark ? " lang-toggle-dark" : ""}`}
      aria-label={`Switch language to ${other.label}`}
    >
      <span aria-hidden="true">🌐</span>
      {other.nativeLabel}
    </button>
  );
}
