import { apiGet } from "@/lib/api";
import { MembershipTransitionForm } from "@/components/admin/MembershipTransitionForm";
import { LinkGuardianForm } from "@/components/admin/LinkGuardianForm";

type MembershipRow = {
  id: string;
  username: string;
  email: string;
  is_minor: boolean;
  status: string;
  tier: string | null;
  expires_at: string | null;
};

type Paginated<T> = { count: number; results: T[] };

export default async function AdminMembershipPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; status?: string }>;
}) {
  const params = await searchParams;
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.status) query.set("status", params.status);

  const page = await apiGet<Paginated<MembershipRow>>(
    `/membership/admin/${query.toString() ? `?${query.toString()}` : ""}`
  );

  return (
    <div>
      <span className="eyebrow">Membership</span>
      <h1 style={{ marginTop: 10 }}>Membership administration</h1>

      <div style={{ marginTop: 24 }}>
        <LinkGuardianForm />
      </div>

      <form method="GET" className="card" style={{ marginTop: 24, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <input
          className="input"
          style={{ marginTop: 0, flex: 1, minWidth: 220 }}
          name="q"
          placeholder="Search by name, username, or email"
          defaultValue={params.q}
        />
        <select className="select" style={{ marginTop: 0, width: 180 }} name="status" defaultValue={params.status ?? ""}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
          <option value="expired">Expired</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <button type="submit" className="btn btn-ghost">
          Filter
        </button>
      </form>

      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Member</th>
              <th>Status</th>
              <th>Tier</th>
              <th>Expires</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(page?.results ?? []).map((member) => (
              <tr key={member.id}>
                <td>
                  {member.username}
                  {member.is_minor && (
                    <span className="tag" style={{ marginLeft: 8 }}>
                      Minor
                    </span>
                  )}
                  <br />
                  <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>{member.email}</span>
                </td>
                <td>
                  <span className={`status-pill status-${member.status}`}>{member.status}</span>
                </td>
                <td>{member.tier ?? "—"}</td>
                <td>
                  {member.expires_at
                    ? new Date(member.expires_at).toLocaleDateString("en-GB")
                    : "—"}
                </td>
                <td>
                  <MembershipTransitionForm membershipId={member.id} />
                </td>
              </tr>
            ))}
            {!page?.results?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  No members match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      {page && <p style={{ marginTop: 14, color: "var(--muted)" }}>{page.count} total members</p>}
    </div>
  );
}
