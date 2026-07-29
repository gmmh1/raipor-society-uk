import { apiGet } from "@/lib/api";
import { CreateProductForm } from "@/components/admin/CreateProductForm";
import { ProductDeactivateButton } from "@/components/admin/ProductDeactivateButton";
import { OrderTransitionForm } from "@/components/admin/OrderTransitionForm";

type Product = {
  id: string;
  name: string;
  sku: string;
  price_minor: number;
  currency: string;
  inventory_count: number;
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
  const [products, orders] = await Promise.all([
    apiGet<Product[]>("/shop/products/"),
    apiGet<Paginated<Order>>("/shop/orders/admin/"),
  ]);

  return (
    <div>
      <span className="eyebrow">Shop</span>
      <h1 style={{ marginTop: 10 }}>Shop administration</h1>

      <div style={{ marginTop: 24 }}>
        <CreateProductForm />
      </div>

      <div className="card" style={{ marginTop: 24, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Product</th>
              <th>SKU</th>
              <th>Price</th>
              <th>Stock</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(products ?? []).map((product) => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.sku}</td>
                <td>{money(product.price_minor, product.currency)}</td>
                <td>{product.inventory_count}</td>
                <td>
                  <ProductDeactivateButton productId={product.id} />
                </td>
              </tr>
            ))}
            {!products?.length && (
              <tr>
                <td colSpan={5} style={{ color: "var(--muted)" }}>
                  No active products.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <h2 style={{ marginTop: 40 }}>Orders</h2>
      <div className="card" style={{ marginTop: 20, overflowX: "auto" }}>
        <table className="table">
          <thead>
            <tr>
              <th>Member</th>
              <th>Date</th>
              <th>Status</th>
              <th>Total</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {(orders?.results ?? []).map((order) => (
              <tr key={order.id}>
                <td>{order.username}</td>
                <td>{new Date(order.created_at).toLocaleDateString("en-GB")}</td>
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
                  No orders yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
