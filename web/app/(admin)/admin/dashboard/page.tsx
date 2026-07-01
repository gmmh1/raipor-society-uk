export default function AdminDashboardPage() {
  return (
    <main className="page-shell">
      <span className="badge">Admin Portal</span>
      <h1>Operations Dashboard</h1>
      <section className="grid grid-2">
        <article className="card">
          <h2>Governance</h2>
          <p>Election setup, polls, and audit visibility.</p>
        </article>
        <article className="card">
          <h2>Finance</h2>
          <p>Ledger controls, reconciliation, and receipts.</p>
        </article>
        <article className="card">
          <h2>Membership</h2>
          <p>Approvals, roles, and safeguarding controls.</p>
        </article>
        <article className="card">
          <h2>Analytics</h2>
          <p>Membership growth, events, donations, engagement.</p>
        </article>
      </section>
    </main>
  );
}
