<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { cart, initializeCart } from "$lib/cart";
  import "../styles.css";

  let username = "";
  let loggingOut = false;

  $: cartCount = $cart.reduce((count, item) => count + item.quantity, 0);

  onMount(async () => {
    initializeCart();
    try {
      const res = await fetch("http://localhost:8000/api/me", { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        username = data.display_name;
      }
    } catch {}
  });

  async function logout() {
    loggingOut = true;
    try {
      await fetch("http://localhost:8000/api/logout", {
        method: "POST",
        credentials: "include",
      });
    } finally {
      username = "";
      loggingOut = false;
      goto("/");
    }
  }
</script>

<svelte:head>
  <title>CyberCart</title>
  <meta name="description" content="CyberCart deep-link security workshop" />
</svelte:head>

<nav class="nav">
  <a class="brand" href="/">CyberCart</a>
  <div class="navlinks">
    <a href="/products">Products</a>
    <a href="/cart">My Cart{cartCount ? ` (${cartCount})` : ""}</a>
    <a href="/orders">Orders</a>
    <a href="/agent">AI Agent</a>
    <a href="/lab">Workshop</a>
    {#if username}
      <!-- username shows here - CSRF attack renames this, making the impact obvious -->
      <span class="user-name">{username}</span>
      <button class="nav-action" on:click={logout} disabled={loggingOut}>
        {loggingOut ? "Logging out..." : "Logout"}
      </button>
    {:else}
      <a href="/login" style="color: #aab4c6;">Login</a>
    {/if}
  </div>
</nav>

<main class="container">
  <slot />
</main>
