import { apiGet } from "@/lib/api";
import { VoteForm } from "@/components/member/VoteForm";

type Poll = {
  id: string;
  title: string;
  description: string;
  position: string;
  status: "upcoming" | "open" | "closed";
  has_voted: boolean;
  quorum: number;
  options: { id: string; text: string; image_url: string }[];
};

export default async function MemberVotingPage() {
  const polls = await apiGet<Poll[]>("/voting/polls/");

  return (
    <div>
      <span className="eyebrow">Voting</span>
      <h1 style={{ marginTop: 10 }}>Polls and elections</h1>

      <div className="grid grid-2" style={{ marginTop: 28 }}>
        {(polls ?? []).map((poll) => (
          <article className="card" key={poll.id}>
            <span className={`status-pill status-${poll.status}`}>{poll.status}</span>
            {poll.position && (
              <span className="tag" style={{ marginLeft: 8 }}>
                Electing: {poll.position}
              </span>
            )}
            <h3 style={{ marginTop: 14 }}>{poll.title}</h3>
            {poll.description && <p style={{ marginTop: 8 }}>{poll.description}</p>}

            {poll.status === "open" && !poll.has_voted && (
              <VoteForm pollId={poll.id} options={poll.options} />
            )}
            {poll.status === "open" && poll.has_voted && (
              <p style={{ marginTop: 16, color: "var(--success)", fontWeight: 700 }}>
                ✓ Your vote has been recorded
              </p>
            )}
            {poll.status === "upcoming" && (
              <p style={{ marginTop: 16, color: "var(--muted)" }}>Voting hasn't opened yet.</p>
            )}
            {poll.status === "closed" && (
              <p style={{ marginTop: 16, color: "var(--muted)" }}>
                This poll has closed. Results are available from the committee.
              </p>
            )}
          </article>
        ))}
        {!polls?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No polls published yet.
          </div>
        )}
      </div>
    </div>
  );
}
