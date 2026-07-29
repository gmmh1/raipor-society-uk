import Link from "next/link";

export default function EventsPage() {
  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">Events</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>
            Where the community gathers.
          </h1>
          <p className="lede" style={{ marginTop: 18 }}>
            From seasonal festivals to regular meet-ups, this is where we'll
            publish everything happening across the society.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div
            className="card"
            style={{
              textAlign: "center",
              padding: "56px 32px",
              maxWidth: 640,
              margin: "0 auto",
            }}
          >
            <span className="tag">Coming soon</span>
            <h2 style={{ marginTop: 16 }}>No events published yet</h2>
            <p style={{ marginTop: 10, marginInline: "auto" }}>
              We're setting up our events calendar. Get in touch to be added
              to our updates list, and you'll hear about gatherings as soon
              as they're scheduled.
            </p>
            <Link
              href="/contact"
              className="btn btn-primary"
              style={{ marginTop: 24 }}
            >
              Get event updates
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
