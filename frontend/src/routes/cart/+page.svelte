<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import ProductImage from "$lib/ProductImage.svelte";
  import { publicApiBaseUrl } from "$lib/api";

  type CartItem = {
    product_id: number;
    name: string;
    price: number;
    image?: string | null;
    quantity: number;
    line_total: number;
  };

  let items: CartItem[] = [];
  let total = 0;
  let loading = true;
  let error = "";
  let shippingAddress = "";
  let checkingOut = false;

  const money = (value: number) => `₹${value.toLocaleString("en-IN")}`;

  async function loadCart() {
    error = "";
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/cart`, {
        credentials: "include",
      });
      if (response.status === 401) {
        error = "Log in with your participant link to use your cart.";
        return;
      }
      if (!response.ok) throw new Error("Cart request failed");
      const data = await response.json();
      items = data.items;
      total = data.total;
    } catch {
      error = "Could not load your cart. Try again.";
    } finally {
      loading = false;
    }
  }

  async function setQuantity(item: CartItem, quantity: number) {
    if (quantity < 1 || quantity > 99) return;
    const response = await fetch(`${publicApiBaseUrl}/api/cart/items/${item.product_id}`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quantity }),
    });
    if (response.ok) {
      const data = await response.json();
      items = data.items;
      total = data.total;
      window.dispatchEvent(new CustomEvent("cart-changed"));
    }
  }

  async function removeItem(productId: number) {
    const response = await fetch(`${publicApiBaseUrl}/api/cart/items/${productId}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (response.ok) {
      const data = await response.json();
      items = data.items;
      total = data.total;
      window.dispatchEvent(new CustomEvent("cart-changed"));
    }
  }

  async function checkout() {
    error = "";
    checkingOut = true;
    try {
      const response = await fetch(`${publicApiBaseUrl}/api/cart/checkout`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ shipping_address: shippingAddress }),
      });
      const data = await response.json();
      if (!response.ok) {
        error = data.detail ?? "Checkout failed";
        return;
      }
      window.dispatchEvent(new CustomEvent("cart-changed"));
      await goto(`/orders/${data.order_id}`);
    } catch {
      error = "Checkout failed. Try again.";
    } finally {
      checkingOut = false;
    }
  }

  onMount(loadCart);
</script>

<h1>My Cart</h1>

{#if loading}
  <p>Loading…</p>
{:else if error && items.length === 0}
  <div class="notice" role="alert">{error}</div>
{:else if items.length === 0}
  <div class="notice">
    Your cart is empty. <a href="/products"><strong>Browse products</strong></a>
  </div>
{:else}
  <section class="cart-list">
    {#each items as item (item.product_id)}
      <article class="card cart-item">
        <ProductImage image={item.image} name={item.name} />
        <div>
          <h2>{item.name}</h2>
          <p class="muted">{money(item.price)} each</p>
          <div class="quantity" aria-label={`Quantity for ${item.name}`}>
            <button on:click={() => setQuantity(item, item.quantity - 1)} disabled={item.quantity === 1}>−</button>
            <strong>{item.quantity}</strong>
            <button on:click={() => setQuantity(item, item.quantity + 1)} disabled={item.quantity === 99}>+</button>
          </div>
          <button class="remove" on:click={() => removeItem(item.product_id)}>Remove</button>
        </div>
        <strong class="line-total">{money(item.line_total)}</strong>
      </article>
    {/each}
  </section>

  <section class="card checkout">
    <div>
      <p class="eyebrow">ORDER TOTAL</p>
      <h2>{money(total)}</h2>
    </div>
    <form class="form" on:submit|preventDefault={checkout}>
      <label>
        Shipping address
        <input bind:value={shippingAddress} minlength="3" maxlength="255" required placeholder="Enter your shipping address" />
      </label>
      <button class="button" type="submit" disabled={checkingOut}>
        {checkingOut ? "Placing order…" : "Checkout"}
      </button>
    </form>
    {#if error}<div class="notice" role="alert">{error}</div>{/if}
  </section>
{/if}

<style>
  .cart-list {
    display: grid;
    gap: 1rem;
  }

  .cart-item {
    display: grid;
    grid-template-columns: 150px 1fr auto;
    gap: 1.25rem;
    align-items: center;
  }

  .cart-item :global(.product-image) {
    height: 110px;
  }

  .quantity {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .quantity button,
  .remove {
    border: 1px solid #39465b;
    background: #171e2b;
    color: #e8edf7;
    border-radius: 7px;
    cursor: pointer;
  }

  .quantity button {
    width: 2rem;
    height: 2rem;
  }

  .remove {
    margin-top: 0.8rem;
    padding: 0.4rem 0.65rem;
  }

  .line-total {
    font-size: 1.1rem;
  }

  .checkout {
    margin-top: 1.5rem;
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
  }

  .checkout h2 {
    font-size: 2rem;
  }

  @media (max-width: 750px) {
    .cart-item,
    .checkout {
      grid-template-columns: 1fr;
    }
  }
</style>
