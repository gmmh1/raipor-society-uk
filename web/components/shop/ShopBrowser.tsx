"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { useCart } from "@/lib/useCart";

type Product = {
  id: string;
  name: string;
  description: string;
  price_minor: number;
  currency: string;
  inventory_count: number;
  image_url: string;
  available_sizes: string;
};

function money(minor: number, currency: string) {
  return `${currency} ${(minor / 100).toFixed(2)}`;
}

function sizesOf(product: Product): string[] {
  return product.available_sizes
    ? product.available_sizes.split(",").map((size) => size.trim()).filter(Boolean)
    : [];
}

export function ShopBrowser({ products }: { products: Product[] }) {
  const router = useRouter();
  const { items, addItem, removeItem, clear, totalMinor } = useCart();
  const [checkingOut, setCheckingOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSizes, setSelectedSizes] = useState<Record<string, string>>({});

  async function handleCheckout(provider: "stripe" | "paypal") {
    if (!items.length) return;
    setCheckingOut(true);
    setError(null);

    const orderResult = await callApi<{ id: string; detail?: string }>("/shop/orders/", {
      body: {
        items: items.map((item) => ({
          product_id: item.productId,
          quantity: item.quantity,
          size: item.size ?? "",
        })),
      },
    });

    if (orderResult.status === 401) {
      router.push("/login?next=/shop");
      return;
    }
    if (!orderResult.ok || !orderResult.data?.id) {
      setError(orderResult.data?.detail || "Couldn't create the order.");
      setCheckingOut(false);
      return;
    }

    const origin = window.location.origin;
    const checkoutResult = await callApi<{ redirect_url: string; detail?: string }>(
      `/shop/orders/${orderResult.data.id}/checkout/`,
      {
        body: {
          provider,
          success_url: `${origin}/member/orders?paid=1`,
          cancel_url: `${origin}/shop`,
        },
      }
    );

    if (!checkoutResult.ok || !checkoutResult.data?.redirect_url) {
      setError(checkoutResult.data?.detail || "Couldn't start checkout.");
      setCheckingOut(false);
      return;
    }

    clear();
    window.location.href = checkoutResult.data.redirect_url;
  }

  return (
    <div className="grid grid-2" style={{ marginTop: 28, alignItems: "start" }}>
      <div className="grid grid-2" style={{ gridColumn: "1 / -1" }}>
        {products.map((product) => {
          const sizes = sizesOf(product);
          const selectedSize = selectedSizes[product.id] ?? sizes[0] ?? "";

          return (
            <article className="card" key={product.id}>
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name}
                  style={{
                    width: "100%",
                    aspectRatio: "4 / 3",
                    objectFit: "cover",
                    borderRadius: "var(--radius-sm)",
                    marginBottom: 14,
                  }}
                />
              )}
              <h3>{product.name}</h3>
              {product.description && <p style={{ marginTop: 8 }}>{product.description}</p>}

              {sizes.length > 0 && (
                <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
                  {sizes.map((size) => (
                    <button
                      key={size}
                      type="button"
                      className="btn btn-ghost"
                      style={{
                        padding: "6px 14px",
                        minHeight: "auto",
                        fontSize: "0.85rem",
                        background: size === selectedSize ? "var(--ink)" : undefined,
                        color: size === selectedSize ? "var(--paper)" : undefined,
                      }}
                      onClick={() => setSelectedSizes((current) => ({ ...current, [product.id]: size }))}
                    >
                      {size}
                    </button>
                  ))}
                </div>
              )}

              <div
                style={{
                  marginTop: 16,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong>{money(product.price_minor, product.currency)}</strong>
                <button
                  type="button"
                  className="btn btn-ghost"
                  disabled={product.inventory_count < 1}
                  onClick={() =>
                    addItem(
                      {
                        productId: product.id,
                        name: sizes.length ? `${product.name} (${selectedSize})` : product.name,
                        priceMinor: product.price_minor,
                        currency: product.currency,
                        size: selectedSize,
                      },
                      1
                    )
                  }
                >
                  {product.inventory_count < 1 ? "Out of stock" : "Add to cart"}
                </button>
              </div>
            </article>
          );
        })}
        {!products.length && (
          <div className="empty-state card" style={{ gridColumn: "1 / -1" }}>
            No products available right now.
          </div>
        )}
      </div>

      <div className="card" style={{ gridColumn: "1 / -1", marginTop: 8 }}>
        <h3>Your cart</h3>
        {items.length ? (
          <>
            <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 10 }}>
              {items.map((item) => (
                <div
                  key={`${item.productId}-${item.size ?? ""}`}
                  style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}
                >
                  <span>
                    {item.quantity} × {item.name}
                  </span>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span>{money(item.priceMinor * item.quantity, item.currency)}</span>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      onClick={() => removeItem(item.productId, item.size)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <p style={{ marginTop: 16, fontWeight: 700 }}>
              Total: {money(totalMinor, items[0]?.currency ?? "GBP")}
            </p>
            {error && <p className="form-error">{error}</p>}
            <div style={{ display: "flex", gap: 12, marginTop: 14, flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn btn-primary"
                disabled={checkingOut}
                onClick={() => handleCheckout("stripe")}
              >
                {checkingOut ? "Redirecting…" : "Checkout with card"}
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={checkingOut}
                onClick={() => handleCheckout("paypal")}
              >
                Checkout with PayPal
              </button>
            </div>
          </>
        ) : (
          <p style={{ marginTop: 10, color: "var(--muted)" }}>Your cart is empty.</p>
        )}
      </div>
    </div>
  );
}
