<script lang="ts">
  import { onMount } from "svelte";
  import { publicApiBaseUrl, publicAttackerBaseUrl } from "$lib/api";

  let loggedIn = false;
  let shippingAddress = "";
  let csrfStatus: { samesite: string; secure: boolean; vulnerable: boolean } | null = null;
  let loading = true;

  onMount(async () => {
    try {
      const me = await fetch(`${publicApiBaseUrl}/api/me`, { credentials: "include" });
      loggedIn = me.ok;
      if (loggedIn) {
        const orders = await fetch(`${publicApiBaseUrl}/api/orders`, { credentials: "include" });
        if (orders.ok) {
          const data = await orders.json();
          shippingAddress = data[0]?.shipping_address ?? "No orders available";
        }
      }
    } catch {
      loggedIn = false;
    }

    try {
      const response = await fetch(`${publicApiBaseUrl}/api/lab/csrf-status`);
      if (response.ok) csrfStatus = await response.json();
    } finally {
      loading = false;
    }
  });
</script>

<p class="eyebrow">WORKSHOP · LAB 4</p>
<h1>CSRF — Cross-Site Request Forgery</h1>

<p class="lead">
  The shipping-address endpoint trusts the participant's session cookie but requires no
  CSRF token. A malicious page can therefore submit the form on the participant's behalf.
</p>

{#if loading}
  <p class="muted">Loading status…</p>
{:else}
  <div class="notice" class:vulnerable={csrfStatus?.vulnerable}>
    {#if csrfStatus?.vulnerable}
      <strong>⚠ VULNERABLE ENDPOINT</strong> — no CSRF token;
      <code>SameSite={csrfStatus.samesite}</code>, <code>Secure={String(csrfStatus.secure)}</code>
    {:else}
      Could not fetch backend status.
    {/if}
  </div>

  {#if loggedIn}
    <div class="notice">
      <strong>Current shipping address:</strong>
      <code>{shippingAddress}</code>
      <span class="muted small"> — reload after the attack to see it change.</span>
    </div>
  {:else}
    <div class="notice">
      <strong>Not logged in.</strong> Open a participant's unique login link first.
    </div>
  {/if}
{/if}

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Log in</h2>
    <p>Use a participant URL from the generated login CSV, then note an order's shipping address.</p>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Visit the attacker</h2>
    <p>The phishing page silently submits a cross-origin form with a replacement address.</p>
    <a class="button" href={publicAttackerBaseUrl} target="_blank" rel="noreferrer">Open phishing page ↗</a>
    <a class="button secondary" href={`${publicAttackerBaseUrl}/demo`} target="_blank" rel="noreferrer">Demo mode ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Verify the change</h2>
    <p>Return here and reload. The address should read <code>666 Attacker Avenue</code>.</p>
    <button class="button secondary" on:click={() => location.reload()}>Reload page</button>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable endpoint</h2>
  <dl>
    <dt>Request</dt>
    <dd><code>POST /api/orders/shipping-address</code></dd>
    <dt>Body</dt>
    <dd><code>shipping_address=666 Attacker Avenue</code></dd>
    <dt>Authentication</dt>
    <dd>Cookie session, with no CSRF-token validation</dd>
    <dt>Effect</dt>
    <dd>Changes the logged-in participant's order shipping addresses.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>
    Require a per-session CSRF token on every state-changing form. A suitable
    <code>SameSite</code> cookie policy adds another browser-level defence.
  </p>
  <p class="muted small">
    Cross-site <code>SameSite=None</code> cookies also require <code>Secure=true</code> and HTTPS in modern browsers.
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
