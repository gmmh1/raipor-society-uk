const values = [
  {
    title: "Open to everyone",
    copy: "Every event, program, and welfare service is open to the whole community, regardless of age or background.",
  },
  {
    title: "Run by members",
    copy: "Decisions are made through open governance and member voting — this is a community organisation run for its members, by its members.",
  },
  {
    title: "Built to last",
    copy: "We invest in people, not just events — mentorship, safeguarding, and steady, patient community-building.",
  },
];

export default function AboutPage() {
  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">About us</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>
            A community, established for the long run.
          </h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Raipor Society UK is a community organisation bringing people
            together through events, learning, and collaboration —
            celebrating our diversity while building strong bonds and
            encouraging personal growth and collective development for a
            better future. Always forward, together.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">How we work</span>
            <h2>What guides the society day to day.</h2>
          </div>
          <div className="grid grid-2">
            {values.map((value) => (
              <article className="card" key={value.title}>
                <h3>{value.title}</h3>
                <p style={{ marginTop: 8 }}>{value.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="card" style={{ padding: 40 }}>
            <span className="eyebrow">Governance</span>
            <h2 style={{ marginTop: 14 }}>Member-led, transparently run.</h2>
            <p style={{ marginTop: 12, maxWidth: "60ch" }}>
              Membership status, committee roles, and community votes are all
              handled through the society's own member portal, with an
              auditable record behind every decision — because trust is
              something we build in the open, not something we ask for.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}
