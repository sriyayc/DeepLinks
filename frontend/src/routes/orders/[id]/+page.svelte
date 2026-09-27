<script lang="ts">
  import { page } from "$app/state";
  import { onMount } from "svelte";

  let order: any = null;
  let error = "";

  onMount(async () => {
    const strictAuthz = page.url.searchParams.get("strict_authz") === "true";
    const strictAuthzQuery = strictAuthz ? "?strict_authz=true" : "";
    const res = await fetch(
      `http://localhost:8000/api/orders/${page.params.id}${strictAuthzQuery}`,
      { credentials: "include" }
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
      <p>Participant: #{order.participant_id}</p>
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

{#if page.url.searchParams.get("strict_authz") === "true"}
  <p class="muted">Strict authorization mode is enabled.</p>
{/if}
