<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/stores";
  import ProductImage from "$lib/ProductImage.svelte";
  import Pagination from "$lib/Pagination.svelte";
  import SearchForm from "$lib/SearchForm.svelte";
  import { productPrice } from "$lib/productPrice";
  import { paginate } from "$lib/pagination";
  import { publicApiBaseUrl } from "$lib/api";
  import AddToCartButton from "$lib/AddToCartButton.svelte";

  type Product = {
    id: number;
    name: string;
    description: string;
    price: number;
    image?: string | null;
    category: string;
  };

  let products: Product[] = [];
  let loading = true;
  let error = "";

  const categories = ["Books", "Electronics", "Accessories"];
  $: requestedCategory = $page.url.searchParams.get("category") ?? "All";
  $: selectedCategory = categories.includes(requestedCategory) ? requestedCategory : "All";
  $: filteredProducts = selectedCategory === "All"
    ? products
    : products.filter((product) => product.category === selectedCategory);
  $: pagination = paginate(filteredProducts, $page.url.searchParams.get("page"));

  function categoryHref(category: string) {
    const params = new URLSearchParams($page.url.searchParams);
    params.delete("page");
    if (category === "All") params.delete("category");
    else params.set("category", category);
    const query = params.toString();
    return query ? `/products?${query}` : "/products";
  }

  onMount(async () => {
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/products`);
      if (!res.ok) throw new Error("Could not load products");
      const data: Product[] = await res.json();
      products = data.sort((a, b) => a.id - b.id);
    } catch {
      error = "Could not load products. Please check that the shop API is running and try again.";
    } finally {
      loading = false;
    }
  });
</script>

<h1>Products</h1>
<p class="muted">Everything here is fictional workshop data.</p>
<SearchForm />

<nav class="filters" aria-label="Product categories">
  {#each ["All", ...categories] as category}
    <a
      class="filter"
      class:active={category === selectedCategory}
      aria-current={category === selectedCategory ? "page" : undefined}
      href={categoryHref(category)}
    >{category}</a>
  {/each}
</nav>

{#if loading}
  <p>Loading...</p>
{:else if error}
  <p role="alert">{error}</p>
  <a class="button" href={$page.url.pathname + $page.url.search} data-sveltekit-reload>Try again</a>
{:else if filteredProducts.length === 0}
  <p class="muted">No products found in this category.</p>
{:else}
  <p class="muted" role="status">
    Showing {pagination.first}–{pagination.last} of {filteredProducts.length} {selectedCategory === "All" ? "products" : selectedCategory.toLowerCase()}
  </p>
  <section class="grid">
    {#each pagination.items as product (product.id)}
      <article class="card product">
        <ProductImage image={product.image} name={product.name} />
        <div>
          <span class="badge">{product.category}</span>
          <h2>{product.name}</h2>
          <p>{product.description}</p>
          <strong>{productPrice(product)}</strong>
        </div>
        <div class="product-actions">
          <a class="button secondary" href={`/products/${product.id}`}>View product</a>
          <AddToCartButton productId={product.id} />
        </div>
      </article>
    {/each}
  </section>

  <Pagination url={$page.url} currentPage={pagination.currentPage} totalPages={pagination.totalPages} />
{/if}

<style>
  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0 0 1.5rem;
  }

  .filter {
    padding: 0.55rem 0.85rem;
    border: 1px solid #30394a;
    border-radius: 999px;
    color: #aab4c6;
  }

  .filter:hover,
  .filter.active {
    border-color: #e8edf7;
    background: #e8edf7;
    color: #0a0d13;
  }

  .product-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    align-items: flex-start;
  }

  .product-actions :global(.button.secondary) {
    margin-left: 0;
  }
</style>
