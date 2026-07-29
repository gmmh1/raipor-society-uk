export type Lang = "en" | "bn";

export const LANG_COOKIE = "raipor_lang";
export const DEFAULT_LANG: Lang = "en";
export const LANGUAGES: { code: Lang; label: string; nativeLabel: string }[] = [
  { code: "en", label: "English", nativeLabel: "English" },
  { code: "bn", label: "Bangla", nativeLabel: "বাংলা" },
];

export function isLang(value: string | undefined): value is Lang {
  return value === "en" || value === "bn";
}
