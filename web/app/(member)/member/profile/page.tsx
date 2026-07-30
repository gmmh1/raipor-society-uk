import { apiGet } from "@/lib/api";
import { ProfileForm } from "@/components/member/ProfileForm";

type MyProfile = {
  position: string;
  avatar_url: string;
  bio: string;
  public_consent: boolean;
  phone_number: string;
};

export default async function MemberProfilePage() {
  const profile = await apiGet<MyProfile>("/membership/profile/me/");

  return (
    <div>
      <span className="eyebrow">Profile</span>
      <h1 style={{ marginTop: 10 }}>Your public profile</h1>
      <p style={{ marginTop: 10, maxWidth: "60ch" }}>
        Nothing here is shown on the public website unless you turn on "Show my profile
        publicly" below. Committee positions are set by an admin, not self-declared.
      </p>

      <div style={{ marginTop: 24 }}>
        <ProfileForm
          initial={{
            avatarUrl: profile?.avatar_url ?? "",
            bio: profile?.bio ?? "",
            publicConsent: profile?.public_consent ?? false,
            phoneNumber: profile?.phone_number ?? "",
          }}
          position={profile?.position ?? ""}
        />
      </div>
    </div>
  );
}
