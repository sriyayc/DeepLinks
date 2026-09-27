<script lang="ts">
  import { onMount } from "svelte";
  import { addToCart } from "$lib/cart";

  type Product = {
    id: number;
    name: string;
    description: string;
    price: number;
    image?: string;
  };

  let products: Product[] = [];
  let loading = true;
  let addedProductId: number | null = null;

  onMount(async () => {
    const res = await fetch("http://localhost:8000/api/products");
    products = await res.json();
    loading = false;
  });

  function add(product: Product) {
    addToCart({ id: product.id, name: product.name, price: product.price });
    addedProductId = product.id;
    setTimeout(() => {
      if (addedProductId === product.id) addedProductId = null;
    }, 1200);
  }
</script>

<h1>Products</h1>
<p class="muted">Everything here is fictional workshop data.</p>

{#if loading}
  <p>Loading...</p>
{:else}
  <section class="grid">
    {#each products as product}
      <article class="card product">
        <div class="product-image">CYBER</div>
        <div>
          <h2>{product.name}</h2>
          <p>{product.description}</p>
          <strong>₹{product.price}</strong>
        </div>
        <div class="product-actions">
          <a class="button secondary" href={`/product/${product.id}`}>View product</a>
          <button class="button" on:click={() => add(product)}>
            {addedProductId === product.id ? "Added" : "Add to cart"}
          </button>
        </div>
      </article>
    {/each}
  </section>
{/if}
