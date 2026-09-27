import { browser } from "$app/environment";
import { get, writable } from "svelte/store";

export type CartProduct = {
  id: number;
  name: string;
  price: number;
};

export type CartItem = CartProduct & {
  quantity: number;
};

const STORAGE_KEY = "cybercart-cart";

export const cart = writable<CartItem[]>([]);

let initialized = false;

export function initializeCart() {
  if (!browser || initialized) return;

  initialized = true;
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) cart.set(JSON.parse(saved));
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }

  cart.subscribe((items) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  });
}

export function addToCart(product: CartProduct) {
  const items = get(cart);
  const existing = items.find((item) => item.id === product.id);

  if (existing) {
    cart.set(
      items.map((item) =>
        item.id === product.id
          ? { ...item, quantity: Math.min(item.quantity + 1, 99) }
          : item,
      ),
    );
    return;
  }

  cart.set([...items, { ...product, quantity: 1 }]);
}

export function setQuantity(productId: number, quantity: number) {
  if (quantity < 1) {
    removeFromCart(productId);
    return;
  }

  cart.update((items) =>
    items.map((item) =>
      item.id === productId
        ? { ...item, quantity: Math.min(Math.floor(quantity), 99) }
        : item,
    ),
  );
}

export function removeFromCart(productId: number) {
  cart.update((items) => items.filter((item) => item.id !== productId));
}

export function clearCart() {
  cart.set([]);
}
