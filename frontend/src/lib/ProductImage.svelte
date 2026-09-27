<script lang="ts">
  export let image: string | null | undefined = undefined;
  export let name: string;
  export let large = false;

  // The starter database already uses these SVG paths. Resolve them here so
  // existing participant databases do not need to be reseeded for the artwork.
  const starterImages: Record<string, string> = {
    "/images/book.svg": "/images/book.png",
    "/images/kit.svg": "/images/kit.png",
    "/images/adapter.svg": "/images/adapter.png",
    "/images/laptop.svg": "/images/laptop.png",
  };

  let failedSource = "";
  $: source = image ? (starterImages[image] ?? image) : "";
</script>

<div class="product-image" class:large>
  {#if source && failedSource !== source}
    <img
      src={source}
      alt={name}
      width="1536"
      height="1024"
      loading={large ? "eager" : "lazy"}
      decoding="async"
      on:error={() => (failedSource = source)}
    />
  {:else}
    <span class="fallback">Image unavailable</span>
  {/if}
</div>

<style>
  .product-image,
  .product-image.large {
    width: 100%;
    height: auto;
    aspect-ratio: 3 / 2;
    overflow: hidden;
  }

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .fallback {
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: normal;
  }
</style>
