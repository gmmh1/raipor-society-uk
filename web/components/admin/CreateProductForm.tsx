"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";

export function CreateProductForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [inventory, setInventory] = useState("0");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const priceMinor = Math.round(Number(price) * 100);
    if (!priceMinor || priceMinor <= 0) {
      setError("Enter a valid price.");
      return;
    }
    setLoading(true);
    setError(null);

    const result = await callApi<{ detail?: string }>("/shop/products/", {
      body: {
        name,
        sku,
        description,
        price_minor: priceMinor,
        currency: "GBP",
        inventory_count: Number(inventory) || 0,
        is_active: true,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || "Couldn't create the product.");
      setLoading(false);
      return;
    }

    setName("");
    setSku("");
    setDescription("");
    setPrice("");
    setInventory("0");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>Add a product</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>Name</label>
          <input className="input" value={name} onChange={(event) => setName(event.target.value)} required />
        </div>
        <div className="field">
          <label>SKU</label>
          <input className="input" value={sku} onChange={(event) => setSku(event.target.value)} required />
        </div>
        <div className="field">
          <label>Price (GBP)</label>
          <input
            className="input"
            type="number"
            min="0.01"
            step="0.01"
            value={price}
            onChange={(event) => setPrice(event.target.value)}
            required
          />
        </div>
        <div className="field">
          <label>Stock</label>
          <input
            className="input"
            type="number"
            min="0"
            value={inventory}
            onChange={(event) => setInventory(event.target.value)}
          />
        </div>
      </div>
      <div className="field">
        <label>Description</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? "Adding…" : "Add product"}
      </button>
    </form>
  );
}
