<script lang="ts">
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  let loggedIn = false;
  let role = "";
  let loading = true;

  onMount(async () => {
    try {
      const me = await fetch(`${publicApiBaseUrl}/api/me`, { credentials: "include" });
      loggedIn = me.ok;
      if (loggedIn) {
        const data = await me.json();
        role = data.role ?? "participant";
      }
    } catch {
      loggedIn = false;
    } finally {
      loading = false;
    }
  });
</script>

<p class="eyebrow">WORKSHOP · LAB 6</p>
<h1>Broken Access Control — Admin</h1>

<p class="lead">
  The admin user list checks only that you are logged in, not that you are an admin. Any
  participant who knows the address can read every participant's details.
</p>

{#if loading}
  <p class="muted">Loading status…</p>
{:else if loggedIn}
  <div class="notice">
    <strong>You are logged in.</strong>
    <span class="muted small"> A regular participant should not be able to open the admin list — but you can.</span>
  </div>
{:else}
  <div class="notice"><strong>Not logged in.</strong> Log in as a normal participant first.</div>
{/if}

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Log in</h2>
    <p>Sign in as a normal participant (any number except 1000).</p>
    <a class="button" href="/login">Go to login ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Call the admin endpoint</h2>
    <p>Open the admin user list directly — it returns every participant, even though you're not an admin.</p>
    <a class="button" href="/api/admin/users" target="_blank" rel="noreferrer">Open /api/admin/users ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Apply the fix</h2>
    <p>Add <code>?strict_authz=true</code> — a non-admin now gets <code>403 Forbidden</code>.</p>
    <a class="button secondary" href="/api/admin/users?strict_authz=true" target="_blank" rel="noreferrer">Open with the fix ↗</a>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable endpoint</h2>
  <dl>
    <dt>Request</dt>
    <dd><code>GET /api/admin/users</code></dd>
    <dt>Flaw</dt>
    <dd>Any authenticated participant can call it — the role is not checked.</dd>
    <dt>Effect</dt>
    <dd>Every participant's account details are exposed to non-admins.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>
    Check <code>role == "admin"</code> on every sensitive endpoint and return <code>403</code>
    otherwise. Hiding the admin page in the UI is not access control.
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
