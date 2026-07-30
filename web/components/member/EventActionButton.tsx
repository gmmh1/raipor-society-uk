"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function RegisterButton({ eventId, lang }: { eventId: string; lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRegister() {
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>("/events/register/", {
      body: { event_id: eventId },
    });
    if (!result.ok) {
      setError(result.data?.detail || t("memberActions.registerError"));
      setLoading(false);
      return;
    }
    router.refresh();
  }

  return (
    <div>
      <button type="button" className="btn btn-primary" onClick={handleRegister} disabled={loading}>
        {loading ? t("memberActions.registering") : t("memberActions.register")}
      </button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}

export function CancelRegistrationButton({
  registrationId,
  lang,
}: {
  registrationId: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);

  async function handleCancel() {
    setLoading(true);
    await callApi(`/events/registrations/${registrationId}/cancel/`);
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleCancel} disabled={loading}>
      {loading ? t("memberActions.cancelling") : t("memberActions.cancelRegistration")}
    </button>
  );
}
