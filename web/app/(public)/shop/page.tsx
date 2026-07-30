import { ShopBrowser } from "@/components/shop/ShopBrowser";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

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

async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${API_BASE}/shop/products/`, { cache: "no-store" });
    if (!res.ok) return [];
    return (await res.json()) as Product[];
  } catch {
    return [];
  }
}

export default async function ShopPage() {
  const products = await getProducts();

  return (
    <main>
      <section className="section" style={{ paddingBottom: 0 }}>
        <div className="container">
          <span className="eyebrow">Shop</span>
          <h1 style={{ marginTop: 16, maxWidth: "18ch" }}>Society merchandise</h1>
          <p className="lede" style={{ marginTop: 18 }}>
            Every purchase supports the society's programs and events. Sign in to check out.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <ShopBrowser products={products} />
        </div>
      </section>
    </main>
  );
}
