<script lang="ts">
  import { page } from "$app/state";
  import { onMount } from "svelte";

  let order: any = null;
  let error = "";

  onMount(async () => {
    const raw = localStorage.getItem("cybercart_user");
    if (!raw) {
      error = "Please log in first.";
      return;
    }

    const user = JSON.parse(raw);
    const res = await fetch(
      `http://localhost:8000/api/orders/${page.params.id}`,
      { headers: {"X-User-ID": String(user.id)} }
    );

    if (res.ok) order = await res.json();
    else error = (await res.json()).detail ?? "Order not found";
  });
</script>

<a href="/orders">← Orders</a>

{#if error}
  <div class="notice">{error}</div>
{:else if order}
  <section class="card detail">
    <div>
      <p class="eyebrow">ORDER #{order.id}</p>
      <h1>₹{order.total}</h1>
      <p>Status: {order.status}</p>
      <p>Shipping: {order.shipping_address}</p>
    </div>
    <div>
      <h2>Items</h2>
      {#each order.items as item}
        <p>{item.name} × {item.quantity}</p>
      {/each}
    </div>
  </section>
{/if}
