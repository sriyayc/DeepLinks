<script lang="ts">
  import { page } from "$app/stores";
  import type { PageData } from "./$types";
  import SearchForm from "$lib/SearchForm.svelte";
  import ProductImage from "$lib/ProductImage.svelte";
  import Pagination from "$lib/Pagination.svelte";
  import { productPrice } from "$lib/productPrice";
  import { paginate } from "$lib/pagination";

  export let data: PageData;

  $: pagination = paginate(data.results, $page.url.searchParams.get("page"));
</script>

<svelte:head><title>Search — CyberCart</title></svelte:head>

<p class="eyebrow">SEARCH</p>
<h1>Find your next product</h1>
<SearchForm query={data.query} safe={data.safe} />

{#if data.query}
  <div class="query-reflection">
    <span class="muted">You searched for:</span>
    {#if data.safe}
      <div class="query-value">{data.query}</div>
    {:else}
      <!-- INTENTIONAL REFLECTED XSS: this is the sole unescaped query sink.
           The full server-rendered response permits script-tag demos too.
           Fix: use the escaped Svelte expression in the branch above. -->
      <div class="query-value">{@html data.query}</div>
    {/if}
  </div>
{/if}

{#if data.error}
  <p role="alert">{data.error}</p>
  <a class="button" href={$page.url.pathname + $page.url.search} data-sveltekit-reload>Try again</a>
{:else if data.results.length === 0}
  <p class="muted" role="status">No products found. Try another product name.</p>
  <a class="button" href="/products">Browse all products</a>
{:else}
  <p class="muted" role="status">Showing {pagination.first}–{pagination.last} of {data.results.length} results</p>
  <section class="grid" aria-label="Search results">
    {#each pagination.items as product (product.id)}
      <article class="card product">
        <ProductImage image={product.image} name={product.name} />
        <div>
          <span class="badge">{product.category}</span>
          <h2>{product.name}</h2>
          <p>{product.description}</p>
          <strong>{productPrice(product)}</strong>
        </div>
        <a class="button" href={`/products/${product.id}`}>View product</a>
      </article>
    {/each}
  </section>
  <Pagination url={$page.url} currentPage={pagination.currentPage} totalPages={pagination.totalPages} label="Search result pages" reload />
{/if}

<style>
  .query-reflection { margin: 1.5rem 0; }
  .query-value { margin-top: 0.5rem; overflow-wrap: anywhere; }
</style>
