<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  let loggedIn = false;
  let cartCount = 0;

  async function refresh() {
    try {
      const me = await fetch(`${publicApiBaseUrl}/api/me`, { credentials: "include" });
      loggedIn = me.ok;
      if (!loggedIn) {
        cartCount = 0;
        return;
      }
      const cart = await fetch(`${publicApiBaseUrl}/api/cart`, { credentials: "include" });
      if (cart.ok) {
        const data = await cart.json();
        cartCount = data.items.reduce(
          (total: number, item: { quantity: number }) => total + item.quantity,
          0,
        );
      }
    } catch {
      loggedIn = false;
      cartCount = 0;
    }
  }

  async function logout() {
    await fetch(`${publicApiBaseUrl}/api/logout`, {
      method: "POST",
      credentials: "include",
    });
    loggedIn = false;
    cartCount = 0;
    await goto("/products");
  }

  onMount(() => {
    refresh();
    window.addEventListener("cart-changed", refresh);
    window.addEventListener("auth-changed", refresh);
    return () => {
      window.removeEventListener("cart-changed", refresh);
      window.removeEventListener("auth-changed", refresh);
    };
  });
</script>

<div class="account-actions">
  <a class="cart-button" href="/cart">
    <span aria-hidden="true">🛒</span>
    <span>My Cart</span>
    {#if loggedIn && cartCount}<span class="cart-count">{cartCount}</span>{/if}
  </a>
  {#if loggedIn}
    <button class="account-button" on:click={logout}>Logout</button>
  {:else}
    <a class="account-button" href="/login">Login</a>
  {/if}
</div>

<style>
  .account-actions {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding-left: 1.1rem;
    border-left: 1px solid #30394a;
  }

  .cart-button,
  .account-button {
    min-height: 38px;
    box-sizing: border-box;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.45rem;
    padding: 0.55rem 0.8rem;
    font-weight: 750;
    white-space: nowrap;
  }

  .cart-button {
    background: #e8edf7;
    color: #0a0d13;
  }

  .account-button {
    border: 1px solid #46536a;
    background: #151c28;
    color: #e8edf7;
    font: inherit;
    cursor: pointer;
  }

  .cart-button:hover,
  .account-button:hover {
    transform: translateY(-1px);
    filter: brightness(1.08);
  }

  .cart-count {
    min-width: 1.2rem;
    height: 1.2rem;
    padding: 0 0.2rem;
    border-radius: 999px;
    display: inline-grid;
    place-items: center;
    background: #0a0d13;
    color: #fff;
    font-size: 0.72rem;
  }

  @media (max-width: 900px) {
    .account-actions {
      padding-left: 0;
      border-left: 0;
    }

    .cart-button span:nth-child(2) {
      display: none;
    }
  }
</style>
