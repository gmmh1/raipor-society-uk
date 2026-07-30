import { apiGet } from "@/lib/api";
import { CreateProductForm } from "@/components/admin/CreateProductForm";
import { ProductDeactivateButton } from "@/components/admin/ProductDeactivateButton";
import { OrderTransitionForm } from "@/components/admin/OrderTransitionForm";
import { getLang } from "@/lib/i18n/server";
import { translate } from "@/lib/i18n/dictionary";

type Product = {
  id: string;
  name: string;
  sku: string;
  price_minor: number;
  currency: string;
  inventory_count: number;
  image_url: string;
  available_sizes: string;
};

type Order = {
  id: string;
  username: string;
  status: string;
  total_minor: number;
  currency: string;
  created_at: string;
};

type Paginated<T> = { count: number; results: T[] };

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toFixed(2)}`;
}

export default async function AdminShopPage() {
  const [products, orders, lang] = await Promise.all([
    apiGet<Product[]>("/shop/products/"),
    apiGet<Paginated<Order>>("/shop/orders/admin/"),
    getLang(),
  ]);
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);

  return (
    <div>
      <span className="eyebrow">{t("adminShop.eyebrow")}</span>
      <h1 style={{ marginTop: 10 }}>{t("adminShop.title")}</h1>

      <div style={{ marginTop: 24 }}>
        <CreateProductForm />
      </div>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th></th>
              <th>{t("adminShop.colProduct")}</th>
              <th>{t("adminShop.colSku")}</th>
              <th>{t("adminShop.colPrice")}</th>
              <th>{t("adminShop.colStock")}</th>
              <th>{t("adminShop.colSizes")}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(products ?? []).map((product) => (
              <tr key={product.id}>
                <td>
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt=""
                      style={{ width: 40, height: 40, objectFit: "cover", borderRadius: 8 }}
                    />
                  ) : (
                    "—"
                  )}
                </td>
                <td>{product.name}</td>
                <td>{product.sku}</td>
                <td>{money(product.price_minor, product.currency)}</td>
                <td>{product.inventory_count}</td>
                <td>{product.available_sizes || "—"}</td>
                <td>
                  <ProductDeactivateButton productId={product.id} />
                </td>
              </tr>
            ))}
            {!products?.length && (
              <tr>
                <td colSpan={6} style={{ color: "var(--muted)" }}>
                  {t("adminShop.noProducts")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <h2 style={{ marginTop: 40 }}>{t("adminShop.orders")}</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>{t("adminShop.colMember")}</th>
              <th>{t("adminCommon.date")}</th>
              <th>{t("adminCommon.status")}</th>
              <th>{t("adminShop.colTotal")}</th>
              <th>{t("adminCommon.action")}</th>
            </tr>
          </thead>
          <tbody>
            {(orders?.results ?? []).map((order) => (
              <tr key={order.id}>
                <td>{order.username}</td>
                <td>{new Date(order.created_at).toLocaleDateString(lang === "bn" ? "bn-BD" : "en-GB")}</td>
                <td>
                  <span className={`status-pill status-${order.status}`}>{order.status}</span>
                </td>
                <td>{money(order.total_minor, order.currency)}</td>
                <td>
                  <OrderTransitionForm orderId={order.id} status={order.status} />
                </td>
              </tr>
            ))}
            {!orders?.results?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  {t("adminShop.noOrders")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
