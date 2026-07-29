import Link from "next/link";
import { apiGet } from "@/lib/api";

type Membership = {
  status: string;
  tier: string | null;
  expires_at: string | null;
};

type EventRegistration = {
  status: string;
  event: { title: string; starts_at: string };
};

type Notification = {
  status: string;
};

export default async function MemberDashboardPage() {
  const [membership, registrations, notifications] = await Promise.all([
    apiGet<Membership>("/membership/me/"),
    apiGet<EventRegistration[]>("/events/registrations/me/"),
    apiGet<Notification[]>("/notifications/me/"),
  ]);

  const upcoming = (registrations ?? []).filter(
    (registration) =>
      registration.status === "registered" || registration.status === "waitlisted"
  );

  return (
    <div>
      <span className="eyebrow">Member portal</span>
      <h1 style={{ marginTop: 10 }}>Welcome back.</h1>

      <div className="grid grid-4" style={{ marginTop: 32 }}>
        <div className="card stat">
          <span className="stat-label">Membership</span>
          <span className={`status-pill status-${membership?.status ?? "pending"}`}>
            {membership?.status ?? "Unknown"}
          </span>
        </div>
        <div className="card stat">
          <span className="stat-value">{upcoming.length}</span>
          <span className="stat-label">Upcoming events</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{notifications?.length ?? 0}</span>
          <span className="stat-label">Notifications</span>
        </div>
        <div className="card stat">
          <span className="stat-value">
            {membership?.expires_at
              ? new Date(membership.expires_at).toLocaleDateString("en-GB")
              : "—"}
          </span>
          <span className="stat-label">Renews on</span>
        </div>
      </div>

      <div className="grid grid-2" style={{ marginTop: 20 }}>
        <Link href="/member/events" className="card">
          <h3>Events</h3>
          <p style={{ marginTop: 6 }}>Register for gatherings and view your history.</p>
        </Link>
        <Link href="/member/documents" className="card">
          <h3>Documents</h3>
          <p style={{ marginTop: 6 }}>Policies and society documents shared with members.</p>
        </Link>
        <Link href="/member/voting" className="card">
          <h3>Voting</h3>
          <p style={{ marginTop: 6 }}>Take part in open polls and committee decisions.</p>
        </Link>
        <Link href="/member/assistant" className="card">
          <h3>Ask the assistant</h3>
          <p style={{ marginTop: 6 }}>Get answers grounded in the society's own documents.</p>
        </Link>
      </div>
    </div>
  );
}
