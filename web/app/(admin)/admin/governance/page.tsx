import { apiGet } from "@/lib/api";
import { CreatePollForm } from "@/components/admin/CreatePollForm";

type Poll = {
  id: string;
  title: string;
  position: string;
  status: "upcoming" | "open" | "closed";
  quorum: number;
};

type Results = {
  ballot_count: number;
  quorum: number;
  quorum_met: boolean;
  options: { text: string; image_url: string; vote_count: number }[];
};

export default async function AdminGovernancePage() {
  const polls = await apiGet<Poll[]>("/voting/polls/");
  const resultsByPoll = new Map<string, Results>();

  if (polls?.length) {
    const results = await Promise.all(
      polls.map((poll) => apiGet<Results>(`/voting/polls/${poll.id}/results/`))
    );
    polls.forEach((poll, index) => {
      if (results[index]) resultsByPoll.set(poll.id, results[index] as Results);
    });
  }

  return (
    <div>
      <span className="eyebrow">Governance</span>
      <h1 style={{ marginTop: 10 }}>Elections and polls</h1>

      <div style={{ marginTop: 24 }}>
        <CreatePollForm />
      </div>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(polls ?? []).map((poll) => {
          const results = resultsByPoll.get(poll.id);
          return (
            <article className="card" key={poll.id}>
              <span className={`status-pill status-${poll.status}`}>{poll.status}</span>
              {poll.position && (
                <span className="tag" style={{ marginLeft: 8 }}>
                  Electing: {poll.position}
                </span>
              )}
              <h3 style={{ marginTop: 14 }}>{poll.title}</h3>
              {results && (
                <>
                  <p style={{ marginTop: 8 }}>
                    {results.ballot_count} ballots cast · quorum {results.quorum} ·{" "}
                    {results.quorum_met ? "met" : "not met"}
                  </p>
                  <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                    {results.options.map((option) => (
                      <div
                        key={option.text}
                        style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          {option.image_url && (
                            <img
                              src={option.image_url}
                              alt=""
                              style={{ width: 24, height: 24, borderRadius: "50%", objectFit: "cover" }}
                            />
                          )}
                          {option.text}
                        </span>
                        <strong>{option.vote_count}</strong>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </article>
          );
        })}
        {!polls?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No polls created yet.
          </div>
        )}
      </div>
    </div>
  );
}
