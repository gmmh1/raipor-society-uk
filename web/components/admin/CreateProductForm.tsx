"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { callApi } from "@/lib/clientApi";
import { ImageUploadField } from "@/components/admin/ImageUploadField";
import { translate } from "@/lib/i18n/dictionary";
import type { Lang } from "@/lib/i18n/config";

export function CreateProductForm({ lang }: { lang: Lang }) {
  const router = useRouter();
  const t = (key: Parameters<typeof translate>[1]) => translate(lang, key);
  const [name, setName] = useState("");
  const [sku, setSku] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [inventory, setInventory] = useState("0");
  const [imageUrl, setImageUrl] = useState("");
  const [sizes, setSizes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const priceMinor = Math.round(Number(price) * 100);
    if (!priceMinor || priceMinor <= 0) {
      setError(t("adminShop.priceError"));
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
        image_url: imageUrl,
        available_sizes: sizes,
        is_active: true,
      },
    });

    if (!result.ok) {
      setError(result.data?.detail || t("adminShop.createError"));
      setLoading(false);
      return;
    }

    setName("");
    setSku("");
    setDescription("");
    setPrice("");
    setInventory("0");
    setImageUrl("");
    setSizes("");
    setLoading(false);
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h3>{t("adminShop.addProduct")}</h3>
      <div className="grid grid-2" style={{ marginTop: 14 }}>
        <div className="field">
          <label>{t("adminShop.name")}</label>
          <input className="input" value={name} onChange={(event) => setName(event.target.value)} required />
        </div>
        <div className="field">
          <label>{t("adminShop.colSku")}</label>
          <input className="input" value={sku} onChange={(event) => setSku(event.target.value)} required />
        </div>
        <div className="field">
          <label>{t("adminShop.priceLabel")}</label>
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
          <label>{t("adminShop.stockLabel")}</label>
          <input
            className="input"
            type="number"
            min="0"
            value={inventory}
            onChange={(event) => setInventory(event.target.value)}
          />
        </div>
        <div className="field">
          <label>{t("adminShop.sizesLabel")}</label>
          <input
            className="input"
            placeholder="S,M,L,XL"
            value={sizes}
            onChange={(event) => setSizes(event.target.value)}
          />
        </div>
      </div>
      <ImageUploadField label={t("adminShop.productPhoto")} value={imageUrl} onChange={setImageUrl} lang={lang} />
      <div className="field">
        <label>{t("adminCommon.description")}</label>
        <textarea
          className="textarea"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn-primary" style={{ marginTop: 18 }} disabled={loading}>
        {loading ? t("adminShop.adding") : t("adminShop.addButton")}
      </button>
    </form>
  );
}
