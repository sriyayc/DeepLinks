/** Display-only price for the fictional bundle; keep the database price numeric. */
export function productPrice(product: { name: string; price: number }): string {
  if (product.name === "iPhone Trio") return "₹ (you can't afford lol)";
  return `₹${product.price}`;
}
