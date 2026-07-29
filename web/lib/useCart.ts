"use client";

import { useCallback, useEffect, useState } from "react";

export type CartItem = {
  productId: string;
  name: string;
  priceMinor: number;
  currency: string;
  quantity: number;
};

const STORAGE_KEY = "raipor_cart";

function readCart(): CartItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as CartItem[]) : [];
  } catch {
    return [];
  }
}

function writeCart(items: CartItem[]) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function useCart() {
  const [items, setItems] = useState<CartItem[]>([]);

  useEffect(() => {
    setItems(readCart());
  }, []);

  const addItem = useCallback((product: Omit<CartItem, "quantity">, quantity: number) => {
    setItems((current) => {
      const existing = current.find((item) => item.productId === product.productId);
      const next = existing
        ? current.map((item) =>
            item.productId === product.productId
              ? { ...item, quantity: item.quantity + quantity }
              : item
          )
        : [...current, { ...product, quantity }];
      writeCart(next);
      return next;
    });
  }, []);

  const removeItem = useCallback((productId: string) => {
    setItems((current) => {
      const next = current.filter((item) => item.productId !== productId);
      writeCart(next);
      return next;
    });
  }, []);

  const clear = useCallback(() => {
    setItems([]);
    writeCart([]);
  }, []);

  const totalMinor = items.reduce((sum, item) => sum + item.priceMinor * item.quantity, 0);

  return { items, addItem, removeItem, clear, totalMinor };
}
