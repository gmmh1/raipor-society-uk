"use client";

import Link from "next/link";
import { useState } from "react";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";
import { LanguageSwitcher } from "@/components/LanguageSwitcher";
import { ThemeToggle } from "@/components/ThemeToggle";

export function TopNav({ lang }: { lang: Lang }) {
  const [open, setOpen] = useState(false);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  const links = [
    { href: "/", label: t("nav.home") },
    { href: "/about", label: t("nav.about") },
    { href: "/programs", label: t("nav.programs") },
    { href: "/events", label: t("nav.events") },
    { href: "/shop", label: t("nav.shop") },
    { href: "/contact", label: t("nav.contact") },
  ];

  return (
    <div className="nav-wrap">
      <div className="container">
        <nav className="nav">
          <Link href="/" className="brand" onClick={() => setOpen(false)}>
            <span className="brand-mark" aria-hidden="true">
              R
            </span>
            Raipor Society UK
          </Link>

          <div className="nav-links">
            {links.map((link) => (
              <Link key={link.href} href={link.href}>
                {link.label}
              </Link>
            ))}
          </div>

          <div className="nav-cta">
            <div className="nav-auth">
              <ThemeToggle />
              <LanguageSwitcher lang={lang} />
              <Link href="/login" className="btn btn-ghost">
                {t("nav.signIn")}
              </Link>
              <Link href="/register" className="btn btn-primary">
                {t("nav.join")}
              </Link>
            </div>
            <button
              type="button"
              className="nav-toggle"
              aria-label={open ? "Close menu" : "Open menu"}
              aria-expanded={open}
              onClick={() => setOpen((value) => !value)}
            >
              {open ? "✕" : "☰"}
            </button>
          </div>
        </nav>

        <div className={`mobile-panel${open ? " open" : ""}`}>
          {links.map((link) => (
            <Link key={link.href} href={link.href} onClick={() => setOpen(false)}>
              {link.label}
            </Link>
          ))}
          <Link href="/donate" onClick={() => setOpen(false)}>
            {t("nav.donate")}
          </Link>
          <Link href="/login" onClick={() => setOpen(false)}>
            {t("nav.signIn")}
          </Link>
          <Link href="/register" onClick={() => setOpen(false)}>
            {t("nav.join")}
          </Link>
          <div className="mobile-panel-lang" style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <ThemeToggle />
            <LanguageSwitcher lang={lang} />
          </div>
        </div>
      </div>
    </div>
  );
}
