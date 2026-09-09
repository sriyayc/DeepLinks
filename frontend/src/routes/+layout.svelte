<script lang="ts">
  import "../styles.css";
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
  </div>
</nav>

<main class="container">
  <slot />
</main>
