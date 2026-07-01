export default function MemberDashboardPage() {
  return (
    <main className="page-shell">
      <span className="badge">Member Portal</span>
      <h1>Member Dashboard</h1>
      <section className="grid grid-2">
        <article className="card">
          <h2>Membership Status</h2>
          <p>Renewals, profile, family account linkage.</p>
        </article>
        <article className="card">
          <h2>Upcoming Events</h2>
          <p>Registrations and QR attendance records.</p>
        </article>
        <article className="card">
          <h2>Notifications</h2>
          <p>Announcements and reminders from committee channels.</p>
        </article>
        <article className="card">
          <h2>AI Assistant</h2>
          <p>Permission-scoped Q&A with citations to official documents.</p>
        </article>
      </section>
    </main>
  );
}
