import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <h3>Raipor Society UK</h3>
            <p style={{ color: "rgba(250,248,244,0.65)", maxWidth: "38ch" }}>
              A community bringing people together through culture, learning,
              and collective progress. Unity, Culture, Friendship, Progress —
              always forward together.
            </p>
          </div>

          <div className="footer-links">
            <h3>Explore</h3>
            <Link href="/about">About the society</Link>
            <Link href="/programs">Programs</Link>
            <Link href="/events">Events</Link>
            <Link href="/donate">Donate</Link>
          </div>

          <div className="footer-links">
            <h3>Community</h3>
            <Link href="/contact">Contact us</Link>
            <Link href="/member/dashboard">Member sign in</Link>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Raipor Society UK. All rights reserved.</span>
          <span>Registered community organisation, United Kingdom.</span>
        </div>
      </div>
    </footer>
  );
}
