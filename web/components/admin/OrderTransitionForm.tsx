"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

const NEXT_STATUS: Record<string, string[]> = {
  pending: ["paid", "cancelled"],
  paid: ["fulfilled", "cancelled"],
  fulfilled: [],
  cancelled: [],
};

export function OrderTransitionForm({
  orderId,
  status,
  lang,
}: {
  orderId: string;
  status: string;
  lang: Lang;
}) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [loading, setLoading] = useState(false);
  const options = NEXT_STATUS[status] ?? [];
  const optionLabels: Record<string, string> = {
    paid: t("adminShop.markPaid"),
    cancelled: t("adminShop.markCancelled"),
    fulfilled: t("adminShop.markFulfilled"),
  };

  async function handleTransition(toStatus: string) {
    setLoading(true);
    await callApi("/shop/orders/transitions/", { body: { order_id: orderId, to_status: toStatus } });
    router.refresh();
  }

  if (!options.length) return null;

  return (
    <div style={{ display: "flex", gap: 8 }}>
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className="btn btn-ghost"
          disabled={loading}
          onClick={() => handleTransition(option)}
        >
          {optionLabels[option] ?? option}
        </button>
      ))}
    </div>
  );
}
