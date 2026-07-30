import Link from "next/link";
import { apiGet } from "@/lib/api";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type OrderItem = {
  id: string;
  product_id: string;
  quantity: number;
  unit_price_minor: number;
  line_total_minor: number;
};

type Order = {
  id: string;
  status: string;
  total_minor: number;
  currency: string;
  items: OrderItem[];
  created_at: string;
};

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toFixed(2)}`;
}

export default async function MyOrdersPage({
  searchParams,
}: {
  searchParams: Promise<{ paid?: string }>;
}) {
  const [orders, params, lang] = await Promise.all([
    apiGet<Order[]>("/shop/orders/me/"),
    searchParams,
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("memberOrders.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("memberOrders.title")}</h1>

      {params.paid && (
        <p className="form-success" style={{ marginTop: 14 }}>
          {t("memberOrders.paidNotice")}
        </p>
      )}

      <div className="grid grid-2" style={{ marginTop: 24 }}>
        {(orders ?? []).map((order) => (
          <article className="card" key={order.id}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={`status-pill status-${order.status}`}>{order.status}</span>
              <span style={{ color: "var(--muted)", fontSize: "0.85rem" }}>
                {new Date(order.created_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")}
              </span>
            </div>
            <ul style={{ marginTop: 14, listStyle: "none", padding: 0, display: "grid", gap: 6 }}>
              {order.items.map((item) => (
                <li key={item.id} style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>× {item.quantity}</span>
                  <span>{money(item.line_total_minor, order.currency)}</span>
                </li>
              ))}
            </ul>
            <p style={{ marginTop: 12, fontWeight: 700 }}>
              {t("memberOrders.total")}: {money(order.total_minor, order.currency)}
            </p>
          </article>
        ))}
        {!orders?.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            {t("memberOrders.noneYet")} <Link href="/shop">{t("memberOrders.visitShop")}</Link>.
          </div>
        )}
      </div>
    </div>
  );
}
