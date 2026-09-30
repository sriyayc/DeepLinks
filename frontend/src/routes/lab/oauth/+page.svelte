<script lang="ts">
  import { onMount } from "svelte";
  import { publicOauthBaseUrl } from "$lib/api";

  let pkce: { pkce_enforced: boolean; mode: string; note: string } | null = null;
  let loading = true;

  onMount(async () => {
    try {
      const res = await fetch(`${publicOauthBaseUrl}/lab/pkce-status`);
      if (res.ok) pkce = await res.json();
    } catch {
      pkce = null;
    } finally {
      loading = false;
    }
  });
</script>

<p class="eyebrow">WORKSHOP · LAB 1</p>
<h1>OAuth — Open Redirect + PKCE</h1>

<p class="lead">
  The CyberID provider issues an authorization code to whatever <code>redirect_uri</code>
  the caller supplies. In vulnerable mode it never checks that address against the app's
  registered callback, so an attacker-controlled site receives the code.
</p>

{#if loading}
  <p class="muted">Loading status…</p>
{:else if pkce}
  <div class="notice" class:vulnerable={!pkce.pkce_enforced}>
    {#if pkce.pkce_enforced}
      <strong>🛡 FIXED MODE</strong> — <code>PKCE_ENFORCED=true</code>. {pkce.note}
    {:else}
      <strong>⚠ VULNERABLE MODE</strong> — <code>PKCE_ENFORCED=false</code>. {pkce.note}
    {/if}
  </div>
{/if}

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Open the login page</h2>
    <p>The login page shows the current mode and the "Sign in with CyberID" button.</p>
    <a class="button" href="/login">Go to login ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Sign in with CyberID</h2>
    <p>The app builds an <code>/authorize</code> request with <code>redirect_uri</code> pointed at the attacker — exactly like a phishing link.</p>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Observe the result</h2>
    <p>Vulnerable → you land on the attacker's callback (the code leaked). Fixed → the spoofed <code>redirect_uri</code> is rejected and login continues safely.</p>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable endpoint</h2>
  <dl>
    <dt>Request</dt>
    <dd><code>GET /authorize?redirect_uri=…&amp;code_challenge=…</code></dd>
    <dt>Flaw</dt>
    <dd><code>redirect_uri</code> is not checked against the client's registered list, and <code>code_verifier</code> is never verified.</dd>
    <dt>Effect</dt>
    <dd>An attacker-supplied redirect receives a valid authorization code.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>
    Set <code>PKCE_ENFORCED=true</code> on the oauth-server: <code>redirect_uri</code> must
    exactly match a registered URI, and the server recomputes <code>S256(code_verifier)</code>
    and rejects any mismatch.
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
