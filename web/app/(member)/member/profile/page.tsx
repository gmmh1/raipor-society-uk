import { apiGet } from "@/lib/api";
import { ProfileForm } from "@/components/member/ProfileForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type MyProfile = {
  position: string;
  avatar_url: string;
  bio: string;
  public_consent: boolean;
  phone_number: string;
};

export default async function MemberProfilePage() {
  const [profile, lang] = await Promise.all([
    apiGet<MyProfile>("/membership/profile/me/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberProfile.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberProfile.title")}</h1>
      <p style={{ marginTop: 10, maxWidth: "60ch" }}>{t("memberProfile.intro")}</p>

      <div style={{ marginTop: 24 }}>
        <ProfileForm
          initial={{
            avatarUrl: profile?.avatar_url ?? "",
            bio: profile?.bio ?? "",
            publicConsent: profile?.public_consent ?? false,
            phoneNumber: profile?.phone_number ?? "",
          }}
          position={profile?.position ?? ""}
          lang={lang}
        />
      </div>
    </div>
  );
}
