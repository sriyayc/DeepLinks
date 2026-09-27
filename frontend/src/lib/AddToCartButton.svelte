<script lang="ts">
  import { publicApiBaseUrl } from "$lib/api";

  export let productId: number;

  let pending = false;
  let message = "";
  let failed = false;

  async function addToCart() {
    pending = true;
    message = "";
    failed = false;
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/cart/items`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });
      if (response.status === 401) {
        failed = true;
        message = "Log in with your participant link first.";
        return;
      }
      if (!response.ok) throw new Error("Could not add item");
      message = "Added to cart";
      window.dispatchEvent(new CustomEvent("cart-changed"));
    } catch {
      failed = true;
      message = "Could not add this item. Try again.";
    } finally {
      pending = false;
    }
  }
</script>

<button class="button" on:click={addToCart} disabled={pending}>
  {pending ? "Adding…" : "Add to cart"}
</button>
{#if message}
  <span class:cart-error={failed} class="cart-message" role="status">{message}</span>
{/if}

<style>
  .cart-message {
    display: block;
    margin-top: 0.55rem;
    color: #8fd7aa;
    font-size: 0.85rem;
  }

  .cart-error {
    color: #ffadad;
  }
</style>
