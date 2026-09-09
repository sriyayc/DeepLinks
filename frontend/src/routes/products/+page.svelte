<script lang="ts">
  import { onMount } from "svelte";

  type Product = {
    id: number;
    name: string;
    description: string;
    price: number;
    image?: string;
  };

  let products: Product[] = [];
  let loading = true;

  onMount(async () => {
    const res = await fetch("http://localhost:8000/api/products");
    products = await res.json();
    loading = false;
  });
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
        <a class="button" href={`/product/${product.id}`}>View product</a>
      </article>
    {/each}
  </section>
{/if}
