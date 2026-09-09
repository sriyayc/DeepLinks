<script lang="ts">
  import { page } from "$app/state";
  import { onMount } from "svelte";

  let results: any[] = [];
  let query = "";

  onMount(async () => {
    query = page.url.searchParams.get("q") ?? "";
    const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();
    results = data.results;
  });
</script>

<p class="eyebrow">SEARCH</p>
<h1>Search results</h1>

<!-- Keep framework-safe rendering here. Create a separate lab route for reflected XSS. -->
<p class="search-query">Query: <strong>{query}</strong></p>

{#if results.length}
  <section class="grid">
    {#each results as result}
      <article class="card">
        <h2>{result.name}</h2>
        <p>₹{result.price}</p>
      </article>
    {/each}
  </section>
{:else}
  <p class="muted">No products found.</p>
{/if}
