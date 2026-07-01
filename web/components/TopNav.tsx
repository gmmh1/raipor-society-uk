import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/programs", label: "Programs" },
  { href: "/events", label: "Events" },
  { href: "/donate", label: "Donate" },
  { href: "/contact", label: "Contact" },
  { href: "/member/dashboard", label: "Member" },
  { href: "/admin/dashboard", label: "Admin" },
];

export function TopNav() {
  return (
    <header className="page-shell" style={{ paddingBottom: 0 }}>
      <nav
        className="card"
        style={{ display: "flex", flexWrap: "wrap", gap: 12 }}
      >
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            style={{ fontWeight: 600, color: "#0f766e" }}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
