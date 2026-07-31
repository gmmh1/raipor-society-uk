import { apiGet } from "@/lib/api";
import { CreatePollForm } from "@/components/admin/CreatePollForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Poll = {
  id: string;
  title: string;
  position: string;
  status: "upcoming" | "open" | "closed";
  voting_method: "plurality" | "ranked_choice";
  quorum: number;
};

type RankedRoundCandidate = {
  option_id: string;
  text: string;
  votes: number;
  status: "Hopeful" | "Elected" | "Rejected";
};

type Results = {
  voting_method: "plurality" | "ranked_choice";
  ballot_count: number;
  quorum: number;
  quorum_met: boolean;
  options: { id: string; text: string; image_url: string; vote_count: number }[];
  rounds?: { round_number: number; candidates: RankedRoundCandidate[] }[];
  winner_option_ids?: string[];
};

function RankedResultsRounds({
  results,
  t,
}: {
  results: Results;
  t: (key: Parameters<typeof translate>[1]) => string;
}) {
  const imageByOptionId = new Map(results.options.map((option) => [option.id, option.image_url]));
  const winnerIds = new Set(results.winner_option_ids ?? []);

  if (!results.rounds?.length) {
    return (
      <p style={{ marginTop: 12, color: "var(--muted)" }}>{t("adminGovernance.noBallotsYet")}</p>
    );
  }

  return (
    <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 18 }}>
      {results.rounds.map((round) => (
        <div key={round.round_number}>
          <span style={{ fontSize: "0.8rem", color: "var(--muted)", fontWeight: 700 }}>
            {t("adminGovernance.round")} {round.round_number}
          </span>
          <div style={{ marginTop: 6, display: "flex", flexDirection: "column", gap: 6 }}>
            {round.candidates.map((candidate) => (
              <div
                key={candidate.option_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 10,
                  opacity: candidate.status === "Rejected" ? 0.5 : 1,
                }}
              >
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  {imageByOptionId.get(candidate.option_id) && (
                    <img
                      src={imageByOptionId.get(candidate.option_id)}
                      alt=""
                      style={{ width: 24, height: 24, borderRadius: "50%", objectFit: "cover" }}
                    />
                  )}
                  {candidate.text}
                  {winnerIds.has(candidate.option_id) && (
                    <span className="tag">{t("adminGovernance.winner")}</span>
                  )}
                </span>
                <strong>
                  {candidate.votes}{" "}
                  <span style={{ fontWeight: 400, color: "var(--muted)", fontSize: "0.8rem" }}>
                    ({t(`adminGovernance.candidateStatus${candidate.status}` as Parameters<typeof translate>[1])})
                  </span>
                </strong>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default async function AdminGovernancePage() {
  const [polls, lang] = await Promise.all([apiGet<Poll[]>("/voting/polls/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
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
      <span className="eyebrow">{t("adminGovernance.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminGovernance.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreatePollForm lang={lang} />
      </div>

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(polls ?? []).map((poll) => {
          const results = resultsByPoll.get(poll.id);
          return (
            <article className="card" key={poll.id}>
              <span className={`status-pill status-${poll.status}`}>{poll.status}</span>
              {poll.position && (
                <span className="tag" style={{ marginLeft: 8 }}>
                  {t("adminGovernance.electing")}: {poll.position}
                </span>
              )}
              <h3 style={{ marginTop: 14 }}>{poll.title}</h3>
              {results && (
                <>
                  <p style={{ marginTop: 8 }}>
                    {results.ballot_count} {t("adminGovernance.ballotsCast")} · {t("adminGovernance.quorum")}{" "}
                    {results.quorum} · {results.quorum_met ? t("adminGovernance.met") : t("adminGovernance.notMet")}
                  </p>
                  {results.voting_method === "ranked_choice" ? (
                    <RankedResultsRounds results={results} t={t} />
                  ) : (
                    <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
                      {results.options.map((option) => (
                        <div
                          key={option.id}
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
                  )}
                </>
              )}
            </article>
          );
        })}
        {!polls?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            {t("adminGovernance.noneYet")}
          </div>
        )}
      </div>
    </div>
  );
}
