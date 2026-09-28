<script lang="ts">
  import "../styles.css";
  import AuthControls from "$lib/AuthControls.svelte";
  import ChatWidget from "$lib/ChatWidget.svelte";
</script>

<svelte:head>
  <title>CyberCart</title>
  <meta
    name="description"
    content="CyberCart deep-link security workshop"
  />
</svelte:head>

<nav class="nav">
  <a class="brand" href="/">CyberCart</a>

  <div class="navlinks">
    <div class="primary-links">
      <a href="/products">Products</a>
      <a href="/search">Search</a>
      <a href="/orders">Orders</a>
      <a href="/agent">AI Agent</a>
      <a href="/lab">Workshop</a>
    </div>

    <AuthControls />
  </div>
</nav>

<main class="container">
  <slot />
</main>

<ChatWidget />