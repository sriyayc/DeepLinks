<script lang="ts">
  import { page } from "$app/state";
  import { onMount } from "svelte";

  let product: any = null;

  onMount(async () => {
    const id = page.params.id;
    const res = await fetch(`http://localhost:8000/api/products/${id}`);
    if (res.ok) product = await res.json();
  });
</script>

{#if product}
  <a href="/products">← Products</a>
  <section class="detail card">
    <div class="product-image large">CYBER</div>
    <div>
      <p class="eyebrow">PRODUCT #{product.id}</p>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <h2>₹{product.price}</h2>
      <button class="button" disabled>Add to cart</button>
      <p class="muted small">Cart actions are intentionally not implemented in the base.</p>
    </div>
  </section>
{:else}
  <p>Product not found.</p>
{/if}
