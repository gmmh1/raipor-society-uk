export type OrgChartMember = {
  user_id: string;
  name: string;
  avatar_url: string;
  position: string;
  display_order: number;
};

type Tier = { position: string; display_order: number; members: OrgChartMember[] };

function groupIntoTiers(members: OrgChartMember[]): Tier[] {
  const sorted = [...members].sort((a, b) => a.display_order - b.display_order);
  const tiers: Tier[] = [];
  for (const member of sorted) {
    const lastTier = tiers[tiers.length - 1];
    if (lastTier && lastTier.position === member.position) {
      lastTier.members.push(member);
    } else {
      tiers.push({ position: member.position, display_order: member.display_order, members: [member] });
    }
  }
  return tiers;
}

/** Renders a committee roster as a top-to-bottom organisational chart: one row
 * per position rank (POSITION_DISPLAY_ORDER on the backend), connected by a
 * vertical line, with members sharing a rank shown side by side in that row. */
export function CommitteeOrgChart({
  members,
  renderActions,
}: {
  members: OrgChartMember[];
  renderActions?: (member: OrgChartMember) => React.ReactNode;
}) {
  const tiers = groupIntoTiers(members);

  return (
    <div className="org-chart">
      {tiers.map((tier, index) => (
        <div className="org-chart-tier" key={tier.position}>
          {index > 0 && <div className="org-chart-connector" aria-hidden="true" />}
          <span className="org-chart-tier-label">{tier.position}</span>
          <div className="org-chart-row">
            {tier.members.map((member) => (
              <article className="card org-chart-card" key={member.user_id}>
                {member.avatar_url ? (
                  <img src={member.avatar_url} alt="" />
                ) : (
                  <div className="avatar-placeholder" aria-hidden="true" />
                )}
                <h4>{member.name}</h4>
                {renderActions?.(member)}
              </article>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
