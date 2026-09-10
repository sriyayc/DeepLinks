<script lang="ts">
  import { pageHref } from "$lib/pagination";
  export let url: URL;
  export let currentPage: number;
  export let totalPages: number;
  export let label = "Product pages";
  export let reload = false;
</script>

  {#if totalPages > 1}
    <nav class="pagination" aria-label={label} data-sveltekit-reload={reload}>
      {#if currentPage > 1}
        <a class="page-link" href={pageHref(url, currentPage - 1)} rel="prev">← Previous</a>
      {:else}
        <button class="page-link" disabled>← Previous</button>
      {/if}

      {#each Array.from({ length: totalPages }, (_, i) => i + 1) as number}
        <a
          class="page-link"
          class:current={number === currentPage}
          href={pageHref(url, number)}
          aria-label={`Page ${number}`}
          aria-current={number === currentPage ? "page" : undefined}
        >{number}</a>
      {/each}

      {#if currentPage < totalPages}
        <a class="page-link" href={pageHref(url, currentPage + 1)} rel="next">Next →</a>
      {:else}
        <button class="page-link" disabled>Next →</button>
      {/if}
    </nav>
  {/if}

<style>
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 2rem;
  }

  .page-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 44px;
    min-height: 44px;
    box-sizing: border-box;
    padding: 0.6rem 0.9rem;
    border: 1px solid #30394a;
    border-radius: 9px;
    background: #10151f;
    color: #e8edf7;
    font: inherit;
  }

  a.page-link:hover,
  .current {
    background: #e8edf7;
    color: #0a0d13;
  }

  .page-link:focus-visible {
    outline: 2px solid #8ea1c1;
    outline-offset: 3px;
  }

  .page-link:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
</style>
