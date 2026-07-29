export default function ContactPage() {
  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">Contact</span>
          <h1 style={{ marginTop: 16, maxWidth: "16ch" }}>
            We'd love to hear from you.
          </h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Questions about membership, events, or how to get involved —
            reach out and a member of the committee will get back to you.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="grid grid-2">
            <div className="card" style={{ padding: 40 }}>
              <h2>Email us</h2>
              <p style={{ marginTop: 10 }}>
                The quickest way to reach the committee directly.
              </p>
              <a
                href="mailto:hello@raipursociety.uk"
                className="btn btn-primary"
                style={{ marginTop: 22 }}
              >
                hello@raipursociety.uk
              </a>
            </div>

            <div className="card" style={{ padding: 40 }}>
              <h2>Already a member?</h2>
              <p style={{ marginTop: 10 }}>
                Sign in to the member portal for events, documents, and
                voting.
              </p>
              <a
                href="/member/dashboard"
                className="btn btn-ghost"
                style={{ marginTop: 22 }}
              >
                Member sign in
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
