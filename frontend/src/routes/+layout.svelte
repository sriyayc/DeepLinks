<script lang="ts">
  import { onMount } from "svelte";
  import "../styles.css";

  let username = "";

  onMount(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/me", { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        username = data.display_name;
      }
    } catch {}
  });
</script>

<svelte:head>
  <title>CyberCart</title>
  <meta name="description" content="CyberCart deep-link security workshop" />
</svelte:head>

<nav class="nav">
  <a class="brand" href="/">CyberCart</a>
  <div class="navlinks">
    <a href="/products">Products</a>
    <a href="/orders">Orders</a>
    <a href="/agent">AI Agent</a>
    <a href="/lab">Workshop</a>
    {#if username}
      <!-- username shows here — CSRF attack renames this, making the impact obvious -->
      <span style="color: #e8edf7; border: 1px solid #3b4658; border-radius: 6px; padding: 0.2rem 0.6rem; font-size: 0.85rem;">
        👤 {username}
      </span>
    {:else}
      <a href="/login" style="color: #aab4c6;">Login</a>
    {/if}
  </div>
</nav>

<main class="container">
  <slot />
</main>
