<script lang="ts">
  export let query = "";
  export let safe = false;
</script>

<!-- Full document navigation also makes script-tag reflection reproducible. -->
<form action="/search" method="GET" role="search" data-sveltekit-reload>
  <label for="product-query">Search products</label>
  <div class="search-controls">
    <input id="product-query" name="q" type="search" value={query} placeholder="Try Python, headphones, or laptop" />
    {#if safe}<input type="hidden" name="safe" value="true" />{/if}
    <button class="button" type="submit">Search</button>
  </div>
</form>

<style>
  form { margin: 1.5rem 0 2rem; }
  label { margin-bottom: 0.5rem; }
  .search-controls { display: flex; gap: 0.75rem; }
  input[type="search"] { flex: 1; min-width: 0; }
  button { flex-shrink: 0; font: inherit; font-weight: 750; }
  @media (max-width: 420px) {
    .search-controls { flex-direction: column; }
  }
</style>
