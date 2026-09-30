<script lang="ts">
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  let loggedIn = false;
  let myOrderIds: number[] = [];
  let loading = true;

  onMount(async () => {
    try {
      const me = await fetch(`${publicApiBaseUrl}/api/me`, { credentials: "include" });
      loggedIn = me.ok;
      if (loggedIn) {
        const orders = await fetch(`${publicApiBaseUrl}/api/orders`, { credentials: "include" });
        if (orders.ok) {
          const data = await orders.json();
          myOrderIds = data.map((o: { id: number }) => o.id);
        }
      }
    } catch {
      loggedIn = false;
    } finally {
      loading = false;
    }
  });
</script>

<p class="eyebrow">WORKSHOP · LAB 3</p>
<h1>IDOR — Insecure Direct Object Reference</h1>

<p class="lead">
  The order endpoint checks that you are logged in, but not that the order is <em>yours</em>.
  Changing the ID in the URL lets you read other participants' orders.
</p>

{#if loading}
  <p class="muted">Loading status…</p>
{:else if loggedIn}
  <div class="notice">
    <strong>Your order IDs:</strong> <code>{myOrderIds.join(", ") || "none"}</code>
    <span class="muted small"> — now try an ID that isn't in this list.</span>
  </div>
{:else}
  <div class="notice"><strong>Not logged in.</strong> Log in first, then come back.</div>
{/if}

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Note your orders</h2>
    <p>Open your orders and note the ID numbers that belong to you.</p>
    <a class="button" href="/orders">Go to my orders ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Change the ID</h2>
    <p>Hit the API directly with a different number — try 1, 2, 100 — to read orders that aren't yours.</p>
    <a class="button" href="/api/orders/1" target="_blank" rel="noreferrer">Open /api/orders/1 ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Apply the fix</h2>
    <p>Add <code>?strict_authz=true</code> — other people's orders now return <code>404 Not Found</code>.</p>
    <a class="button secondary" href="/api/orders/1?strict_authz=true" target="_blank" rel="noreferrer">Open with the fix ↗</a>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable endpoint</h2>
  <dl>
    <dt>Request</dt>
    <dd><code>GET /api/orders/{"{id}"}</code></dd>
    <dt>Flaw</dt>
    <dd>Any authenticated participant can read any order — ownership is not checked.</dd>
    <dt>Effect</dt>
    <dd>Other participants' order details are exposed.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>
    Verify <code>order.participant_id == current_user.id</code> before returning the order,
    and respond with <code>404</code> otherwise — "logged in" is not the same as "is this yours".
  </p>
</section>

<style>
  .lab-steps,
  .lab-section {
    margin-top: 2rem;
  }
  .lab-steps .button {
    margin-top: 0.75rem;
  }
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>
