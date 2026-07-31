import { apiGet } from "@/lib/api";
import { VoteForm } from "@/components/member/VoteForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Poll = {
  id: string;
  title: string;
  description: string;
  position: string;
  status: "upcoming" | "open" | "closed";
  voting_method: "plurality" | "ranked_choice";
  has_voted: boolean;
  quorum: number;
  options: { id: string; text: string; image_url: string }[];
};

export default async function MemberVotingPage() {
  const [polls, lang] = await Promise.all([apiGet<Poll[]>("/voting/polls/"), getLang()]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberVoting.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberVoting.title")}</h1>

      <div className="grid grid-2" style={{ marginTop: 28 }}>
        {(polls ?? []).map((poll) => (
          <article className="card" key={poll.id}>
            <span className={`status-pill status-${poll.status}`}>{poll.status}</span>
            {poll.position && (
              <span className="tag" style={{ marginLeft: 8 }}>
                {t("memberVoting.electing")}: {poll.position}
              </span>
            )}
            <h3 style={{ marginTop: 14 }}>{poll.title}</h3>
            {poll.description && <p style={{ marginTop: 8 }}>{poll.description}</p>}

            {poll.status === "open" && !poll.has_voted && (
              <VoteForm
                pollId={poll.id}
                options={poll.options}
                votingMethod={poll.voting_method}
                lang={lang}
              />
            )}
            {poll.status === "open" && poll.has_voted && (
              <p style={{ marginTop: 16, color: "var(--success)", fontWeight: 700 }}>
                {t("memberVoting.voteRecorded")}
              </p>
            )}
            {poll.status === "upcoming" && (
              <p style={{ marginTop: 16, color: "var(--muted)" }}>{t("memberVoting.notOpenYet")}</p>
            )}
            {poll.status === "closed" && (
              <p style={{ marginTop: 16, color: "var(--muted)" }}>{t("memberVoting.closedNotice")}</p>
            )}
          </article>
        ))}
        {!polls?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            {t("memberVoting.noneYet")}
          </div>
        )}
      </div>
    </div>
  );
}
