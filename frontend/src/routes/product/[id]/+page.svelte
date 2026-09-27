<script lang="ts">
  import { page } from "$app/state";
  import { onMount } from "svelte";
  import { addToCart } from "$lib/cart";

  let product: any = null;
  let added = false;

  onMount(async () => {
    const id = page.params.id;
    const res = await fetch(`http://localhost:8000/api/products/${id}`);
    if (res.ok) product = await res.json();
  });

  function add() {
    addToCart({ id: product.id, name: product.name, price: product.price });
    added = true;
    setTimeout(() => (added = false), 1500);
  }
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
      <button class="button" on:click={add}>{added ? "Added" : "Add to cart"}</button>
      <a class="button secondary" href="/cart">View cart</a>
    </div>
  </section>
{:else}
  <p>Product not found.</p>
{/if}
