"use client";

import Link from "next/link";
import { useState } from "react";

const links = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/programs", label: "Programs" },
  { href: "/events", label: "Events" },
  { href: "/contact", label: "Contact" },
];

export function TopNav() {
  const [open, setOpen] = useState(false);

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
            <Link href="/member/dashboard" className="btn btn-ghost nav-member-link">
              Member sign in
            </Link>
            <Link href="/donate" className="btn btn-primary">
              Donate
            </Link>
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
          <Link href="/member/dashboard" onClick={() => setOpen(false)}>
            Member sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
