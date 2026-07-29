"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

const NEXT_STATUS: Record<string, string[]> = {
  pending: ["paid", "cancelled"],
  paid: ["fulfilled", "cancelled"],
  fulfilled: [],
  cancelled: [],
};

export function OrderTransitionForm({ orderId, status }: { orderId: string; status: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const options = NEXT_STATUS[status] ?? [];

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
          Mark {option}
        </button>
      ))}
    </div>
  );
}
