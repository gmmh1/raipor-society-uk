import Link from "next/link";

const pillars = [
  {
    title: "Unity",
    copy: "One community across generations and backgrounds, gathered around shared roots and a shared future.",
  },
  {
    title: "Culture",
    copy: "Festivals, food, language, and tradition, kept alive and passed on through everyday community life.",
  },
  {
    title: "Friendship",
    copy: "A place to belong — new arrivals, long-time members, young people, and elders, all welcome at the table.",
  },
  {
    title: "Progress",
    copy: "Learning, mentorship, and mutual support that help every member and the community grow together.",
  },
];

const programs = [
  {
    tag: "Culture",
    title: "Festivals & celebrations",
    copy: "Seasonal gatherings and cultural festivals that bring the community together to celebrate shared heritage.",
  },
  {
    tag: "Youth",
    title: "Youth & education",
    copy: "Mentorship, language classes, and activities that help younger members build confidence and connection.",
  },
  {
    tag: "Welfare",
    title: "Community welfare",
    copy: "Practical support for members and families navigating new challenges, from newcomers to elders.",
  },
  {
    tag: "Gatherings",
    title: "Regular meet-ups",
    copy: "Ongoing social and interest gatherings that keep the community connected between big events.",
  },
];

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <div className="container hero-inner">
          <span className="eyebrow">Registered community organisation · United Kingdom</span>
          <h1>
            Unity, culture, and <em>progress</em> — together.
          </h1>
          <p>
            Raipor Society UK brings people together through events, learning,
            and collaboration — celebrating our diversity while building
            strong bonds, encouraging personal growth, and working toward a
            better future for the whole community.
          </p>
          <div className="hero-actions">
            <Link href="/contact" className="btn btn-primary">
              Join the community
            </Link>
            <Link href="/programs" className="btn btn-ghost-dark">
              See our programs
            </Link>
          </div>
        </div>
      </section>

      <div className="weave-divider" aria-hidden="true" />

      <section className="section">
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">What we stand for</span>
            <h2>Four ideas hold everything we do together.</h2>
          </div>
          <div className="grid grid-4">
            {pillars.map((pillar) => (
              <article className="pillar" key={pillar.title}>
                <span className="pillar-index" aria-hidden="true">
                  {pillar.title.slice(0, 1)}
                </span>
                <h3>{pillar.title}</h3>
                <p>{pillar.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div className="section-head">
            <span className="eyebrow">Get involved</span>
            <h2>Programs built around the community's real needs.</h2>
          </div>
          <div className="grid grid-2">
            {programs.map((program) => (
              <article className="card" key={program.title}>
                <span className="tag">{program.tag}</span>
                <h3 style={{ marginTop: 14 }}>{program.title}</h3>
                <p style={{ marginTop: 8 }}>{program.copy}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <div
            className="card"
            style={{
              background: "var(--ink)",
              border: "none",
              padding: "48px",
              display: "flex",
              flexWrap: "wrap",
              gap: 24,
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ maxWidth: 480 }}>
              <h2 style={{ color: "var(--paper)" }}>
                Every member makes this community stronger.
              </h2>
              <p style={{ color: "rgba(250,248,244,0.75)", marginTop: 10 }}>
                Whether you're joining an event, becoming a member, or
                supporting our work, there's a place for you here.
              </p>
            </div>
            <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
              <Link href="/contact" className="btn btn-primary">
                Get in touch
              </Link>
              <Link href="/donate" className="btn btn-ghost-dark">
                Ways to give
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
