<script lang="ts">
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  let orders: any[] = [];
  let error = "";

  onMount(async () => {
    const res = await fetch(`${publicApiBaseUrl}/api/orders`, {
      credentials: "include",
    });

    if (res.ok) orders = await res.json();
    else error = (await res.json()).detail ?? "Could not load orders";
  });
</script>

<h1>My Orders</h1>

{#if error}
  <div class="notice">{error} <a href="/login">Login</a></div>
{:else}
  <section class="grid">
    {#each orders as order}
      <a class="card link-card" href={`/orders/${order.id}`}>
        <p class="eyebrow">ORDER #{order.id}</p>
        <h2>₹{order.total}</h2>
        <p>{order.status}</p>
      </a>
    {/each}
  </section>
{/if}