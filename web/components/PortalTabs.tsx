"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function PortalTabs({ tabs }: { tabs: { href: string; label: string }[] }) {
  const pathname = usePathname();

  return (
    <div className="portal-tabs">
      <div className="container portal-tabs-inner">
        {tabs.map((tab) => (
          <Link
            key={tab.href}
            href={tab.href}
            className={`portal-tab${pathname === tab.href ? " active" : ""}`}
          >
            {tab.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
