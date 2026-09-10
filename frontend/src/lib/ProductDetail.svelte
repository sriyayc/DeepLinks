<script lang="ts">
  import { page } from "$app/stores";
  import { onMount } from "svelte";
  import ProductImage from "$lib/ProductImage.svelte";
  import { productPrice } from "$lib/productPrice";
  import { publicApiBaseUrl } from "$lib/api";

  type Product = {
    id: number;
    name: string;
    description: string;
    price: number;
    image?: string | null;
    category: string;
  };

  let product: Product | null = null;
  let loading = true;
  let error = "";

  onMount(async () => {
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/products/${$page.params.id}`);
      if (response.status === 404) {
        error = "Product not found.";
        return;
      }
      if (!response.ok) throw new Error("Product API failed");
      product = await response.json();
    } catch {
      error = "Could not load this product. Check that the shop API is running and try again.";
    } finally {
      loading = false;
    }
  });
</script>

<a href="/products">← Products</a>

{#if loading}
  <p>Loading...</p>
{:else if product}
  <section class="detail card">
    <ProductImage image={product.image} name={product.name} large />
    <div>
      <p class="eyebrow">PRODUCT #{product.id}</p>
      <span class="badge">{product.category}</span>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <h2>{productPrice(product)}</h2>
      <button class="button" disabled>Add to cart</button>
      <p class="muted small">Cart actions are intentionally not implemented in the base.</p>
    </div>
  </section>
{:else}
  <p role="alert">{error}</p>
{/if}
