"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark";

function getStoredTheme(): Theme | null {
  if (typeof window === "undefined") return null;
  const stored = window.localStorage.getItem("theme");
  return stored === "light" || stored === "dark" ? stored : null;
}

function applyTheme(theme: Theme | null) {
  if (theme) {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("theme", theme);
  } else {
    document.documentElement.removeAttribute("data-theme");
    window.localStorage.removeItem("theme");
  }
}

export function ThemeToggle({ dark = false }: { dark?: boolean }) {
  const [theme, setTheme] = useState<Theme | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTheme(getStoredTheme());
    setMounted(true);
  }, []);

  function toggle() {
    const systemPrefersDark =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    const isDark = theme ? theme === "dark" : systemPrefersDark;
    const next: Theme = isDark ? "light" : "dark";
    applyTheme(next);
    setTheme(next);
  }

  if (!mounted) {
    // Avoids a hydration mismatch: the server doesn't know the visitor's
    // stored preference, so render nothing until the client effect runs.
    return <span className={`theme-toggle${dark ? " theme-toggle-dark" : ""}`} aria-hidden="true" />;
  }

  const systemPrefersDark =
    typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = theme ? theme === "dark" : systemPrefersDark;

  return (
    <button
      type="button"
      onClick={toggle}
      className={`theme-toggle${dark ? " theme-toggle-dark" : ""}`}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
    >
      <span aria-hidden="true">{isDark ? "☀️" : "🌙"}</span>
    </button>
  );
}
