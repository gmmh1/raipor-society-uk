import Link from "next/link";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

const LAST_UPDATED = "31 July 2026";

export default async function PrivacyPolicyPage() {
  const lang = await getLang();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">{t("privacy.eyebrow")}</span>
          <h1 style={{ marginTop: 16, maxWidth: "24ch" }}>{t("privacy.title")}</h1>
          <p className="lede" style={{ marginTop: 18 }}>{t("privacy.lede")}</p>
          <p style={{ marginTop: 10, color: "var(--muted)", fontSize: "0.9rem" }}>
            {t("privacy.lastUpdated")} {LAST_UPDATED}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container" style={{ maxWidth: "72ch" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
            <div>
              <h2>1. Who we are</h2>
              <p style={{ marginTop: 10 }}>
                Raipur Society UK ("we", "us", "the Society") is a UK charitable community
                organisation. We are the data controller for the personal data described in this
                policy. This platform is entirely self-hosted on infrastructure we operate — we do
                not sell, rent, or hand your data to advertising or analytics companies.
              </p>
              <p style={{ marginTop: 10 }}>
                Questions or requests about your data can be sent to{" "}
                <a href="mailto:hello@raipursociety.uk">hello@raipursociety.uk</a>.
              </p>
            </div>

            <div>
              <h2>2. What we collect, and why</h2>
              <p style={{ marginTop: 10 }}>
                When you join, we ask for your name, date of birth, phone number, email, and a
                profile photo. Date of birth lets us apply the right safeguarding rules for
                members under 18 (see §5); phone number and photo are used for member
                identification — for example, so your photo can appear if you stand as a candidate
                in a committee election, or so an admin can verify who they're speaking to. These
                are visible to committee admins and volunteers running the platform, not published
                or made browsable to other members unless you separately opt in on your profile
                page (see below on the public About Us page). All of this is required to create an
                account — without it, we can't verify who you are or run the Society safely.
              </p>
              <p style={{ marginTop: 10 }}>
                Depending on how you use the platform, we may also hold: your membership status,
                tier and payment/dues history; event registrations and attendance; shop orders;
                documents you upload; messages you send in the Society's chat; your voting
                participation (see §4 — never your vote choice); and questions you ask our AI
                assistant (used only to answer from the Society's own documents, and never sent to
                an outside AI provider to train a model). If you choose to appear on the public
                "About Us" page, you separately opt in per field (name, photo, bio, contact
                details) — nothing about you is shown publicly unless you turn that on yourself.
              </p>
            </div>

            <div>
              <h2>3. Our legal basis</h2>
              <p style={{ marginTop: 10 }}>
                We process membership, event, and financial data under <em>contract</em> (running
                your membership) and <em>legal obligation</em> (UK charity accounting and audit
                requirements). Anything you opt into — a public profile, marketing-style
                communications — is processed under your <em>consent</em>, which you can withdraw
                at any time from your profile page.
              </p>
            </div>

            <div>
              <h2>4. Voting is deliberately anonymous</h2>
              <p style={{ marginTop: 10 }}>
                When you vote in an election or poll, we record two separate, unlinked things: a
                receipt that you voted (so we can prevent double-voting and check quorum) and an
                anonymous tally of the choice itself. There is no record anywhere — not even one
                only staff can see — connecting your identity to how you voted.
              </p>
            </div>

            <div>
              <h2>5. Members under 18</h2>
              <p style={{ marginTop: 10 }}>
                A member's account isn't activated as a minor's independent membership without a
                parent or legal guardian confirming consent through their own account first. We
                keep a record of who consented and when, for safeguarding accountability.
              </p>
            </div>

            <div>
              <h2>6. How long we keep it</h2>
              <p style={{ marginTop: 10 }}>
                Financial records (payments, dues, receipts) are kept for the period UK charities
                are required to retain accounts — currently at least 6 years — even if you erase
                your account in the meantime, but with your identifying details removed (see §7).
                Other personal data is kept for as long as your membership is active, plus a
                reasonable period afterwards in case of disputes, and is deleted or anonymised
                sooner on request.
              </p>
            </div>

            <div>
              <h2>7. Your rights</h2>
              <p style={{ marginTop: 10 }}>Under UK GDPR, you have the right to:</p>
              <ul style={{ marginTop: 10, paddingLeft: 20, display: "flex", flexDirection: "column", gap: 6 }}>
                <li><strong>Access</strong> the personal data we hold about you.</li>
                <li><strong>Correct</strong> anything inaccurate — most of this you can edit yourself from your profile page.</li>
                <li>
                  <strong>Erase</strong> your personal data. Ask a committee admin, and we
                  permanently scrub your name, email, phone, date of birth, and photo, and disable
                  the account. Where we're legally required to keep a financial or voting-integrity
                  record, that record stays but is no longer linked to an identifiable you.
                </li>
                <li><strong>Restrict or object</strong> to certain processing, e.g. opting your profile back out of the public About Us page at any time.</li>
                <li><strong>Receive a copy</strong> of your data in a portable format on request.</li>
                <li>
                  <strong>Complain</strong> to the UK Information Commissioner's Office (
                  <a href="https://ico.org.uk" target="_blank" rel="noreferrer">ico.org.uk</a>
                  ) if you believe we've mishandled your data.
                </li>
              </ul>
            </div>

            <div>
              <h2>8. Where your data lives</h2>
              <p style={{ marginTop: 10 }}>
                Everything is stored on infrastructure we run ourselves: our database and our own
                object storage for uploaded photos and documents. We don't use third-party
                analytics or advertising trackers. A small number of messages — account emails, and
                for members who opt in, WhatsApp or browser push notifications — pass through the
                relevant delivery provider (email, WhatsApp Business, or your browser's push
                service) purely to deliver that one message to you.
              </p>
            </div>

            <div>
              <h2>9. Cookies</h2>
              <p style={{ marginTop: 10 }}>
                We use one essential, httpOnly session cookie to keep you signed in. It isn't used
                for tracking or advertising, and isn't shared with any third party.
              </p>
            </div>

            <div>
              <h2>10. Changes to this policy</h2>
              <p style={{ marginTop: 10 }}>
                If we make a material change to how we handle your data, we'll update the date at
                the top of this page and, for significant changes, notify members directly.
              </p>
            </div>

            <p style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
              {t("privacy.translationNote")}
            </p>

            <Link href="/contact" className="btn btn-ghost" style={{ alignSelf: "flex-start" }}>
              {t("privacy.contactCta")}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
