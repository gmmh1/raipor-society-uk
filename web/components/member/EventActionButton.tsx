"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function RegisterButton({ eventId }: { eventId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRegister() {
    setLoading(true);
    setError(null);
    const result = await callApi<{ detail?: string }>("/events/register/", {
      body: { event_id: eventId },
    });
    if (!result.ok) {
      setError(result.data?.detail || "Couldn't register for this event.");
      setLoading(false);
      return;
    }
    router.refresh();
  }

  return (
    <div>
      <button type="button" className="btn btn-primary" onClick={handleRegister} disabled={loading}>
        {loading ? "Registering…" : "Register"}
      </button>
      {error && <p className="form-error">{error}</p>}
    </div>
  );
}

export function CancelRegistrationButton({ registrationId }: { registrationId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleCancel() {
    setLoading(true);
    await callApi(`/events/registrations/${registrationId}/cancel/`);
    router.refresh();
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={handleCancel} disabled={loading}>
      {loading ? "Cancelling…" : "Cancel registration"}
    </button>
  );
}
