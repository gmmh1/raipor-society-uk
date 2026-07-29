const programs = [
  {
    tag: "Culture",
    title: "Festivals & celebrations",
    copy: "Seasonal gatherings and cultural festivals that bring the whole community together to celebrate shared heritage, food, music, and tradition.",
  },
  {
    tag: "Youth",
    title: "Youth & education",
    copy: "Mentorship, language classes, and structured activities that help younger members build confidence, skills, and a sense of belonging.",
  },
  {
    tag: "Welfare",
    title: "Community welfare",
    copy: "Practical, everyday support for members and families — from newcomers settling in to elders who need a helping hand.",
  },
  {
    tag: "Gatherings",
    title: "Regular meet-ups",
    copy: "Ongoing social and interest-based gatherings that keep the community connected between the big annual events.",
  },
  {
    tag: "Learning",
    title: "Workshops & skills",
    copy: "Practical sessions run by and for members, sharing skills that help people and the wider community grow.",
  },
  {
    tag: "Governance",
    title: "Community voice",
    copy: "Open member voting and committee elections, so the direction of the society is always set by its members.",
  },
];

export default function ProgramsPage() {
  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">Programs</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>
            Community life, all year round.
          </h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Our programs exist to bring people together and help them grow —
            through culture, youth work, welfare, and shared learning.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
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
    </main>
  );
}
