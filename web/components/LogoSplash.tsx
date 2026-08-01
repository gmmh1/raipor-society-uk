"use client";

import { useEffect, useState } from "react";

const SEEN_KEY = "rsu-splash-seen";
const FULL_DURATION_MS = 2400;
const REDUCED_DURATION_MS = 500;

/** Plays once per browser tab: the logo drops in like a football, bounces,
 * then shrinks away into a goal net with motion streaks converging from all
 * four edges, revealing the site underneath. */
export function LogoSplash() {
  const [visible, setVisible] = useState(false);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (sessionStorage.getItem(SEEN_KEY)) return;
    sessionStorage.setItem(SEEN_KEY, "1");

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    setReduced(prefersReduced);
    setVisible(true);

    const timer = setTimeout(
      () => setVisible(false),
      prefersReduced ? REDUCED_DURATION_MS : FULL_DURATION_MS
    );
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div
      className={`logo-splash${reduced ? " logo-splash-reduced" : ""}`}
      onClick={() => setVisible(false)}
      role="presentation"
    >
      <div className="logo-splash-streak logo-splash-streak-top" />
      <div className="logo-splash-streak logo-splash-streak-bottom" />
      <div className="logo-splash-streak logo-splash-streak-left" />
      <div className="logo-splash-streak logo-splash-streak-right" />
      <div className="logo-splash-net" />
      <img src="/logo.jpg" alt="" className="logo-splash-ball" />
    </div>
  );
}
