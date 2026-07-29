const uses = [
  { title: "Community events", copy: "Venue, food, and logistics for gatherings open to the whole community." },
  { title: "Youth programs", copy: "Mentorship, classes, and activities for the society's younger members." },
  { title: "Welfare support", copy: "Practical help for members and families who need it most." },
];

export default function DonatePage() {
  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">Donate</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>
            Give what you can — it goes straight back into the community.
          </h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Every donation supports our events, youth programs, and welfare
            work. We're finalising online giving now — in the meantime, get
            in touch and we'll arrange it directly.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid grid-2" style={{ alignItems: "start" }}>
            <div className="card" style={{ padding: 40 }}>
              <span className="tag">Online giving</span>
              <h2 style={{ marginTop: 14 }}>Card & bank giving — coming soon</h2>
              <p style={{ marginTop: 10 }}>
                We're finishing setup on secure online donations. Want to
                give before then? Contact us and we'll take it from there.
              </p>
              <a href="/contact" className="btn btn-primary" style={{ marginTop: 22 }}>
                Contact us to give
              </a>
            </div>

            <div className="grid" style={{ gap: 16 }}>
              {uses.map((use) => (
                <article className="card" key={use.title}>
                  <h3>{use.title}</h3>
                  <p style={{ marginTop: 8 }}>{use.copy}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
