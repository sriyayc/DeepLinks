<script lang="ts">
  import { onMount } from "svelte";

  let username = "";
  let csrfStatus: any = null;
  let loading = true;

  onMount(async () => {
    // Fetch current user
    try {
      const res = await fetch("http://localhost:8000/api/me", { credentials: "include" });
      if (res.ok) {
        const d = await res.json();
        username = d.display_name;
      }
    } catch {}

    // Fetch CSRF vulnerability status
    try {
      const res = await fetch("http://localhost:8000/api/lab/csrf-status");
      if (res.ok) csrfStatus = await res.json();
    } catch {}

    loading = false;
  });
</script>

<p class="eyebrow">WORKSHOP · LAB 4</p>
<h1>CSRF — Cross-Site Request Forgery</h1>

<p class="lead">
  When a session cookie has <strong>SameSite=None</strong> and there is no CSRF token,
  any page on any origin can make authenticated requests on behalf of a logged-in victim.
</p>

{#if loading}
  <p class="muted">Loading status...</p>
{:else}
  <!-- Vulnerability status banner -->
  <div class="notice" style={csrfStatus?.vulnerable ? "border-color: #f85149; background: #1a0d0d;" : "border-color: #3fb950; background: #0d1a0d;"}>
    {#if csrfStatus?.vulnerable}
      <strong style="color: #f85149;">⚠ VULNERABLE</strong> —
      <code>SameSite={csrfStatus.samesite}</code> · Browser sends cookie on cross-origin requests.
    {:else if csrfStatus}
      <strong style="color: #3fb950;">✅ PROTECTED</strong> —
      <code>SameSite={csrfStatus.samesite}</code> · Cross-origin requests won't carry the cookie.
    {:else}
      <span class="muted">Could not fetch backend status.</span>
    {/if}
  </div>

  <!-- Current identity -->
  {#if username}
    <div class="notice">
      <strong>Logged in as:</strong>
      <code id="username-display">{username}</code>
      <span class="muted small"> — Reload this page after the attack to see your name change.</span>
    </div>
  {:else}
    <div class="notice">
      <strong>Not logged in.</strong>
      <a href="/login">Get a login link</a> first (run <code>python -m app.export_logins</code> in backend).
    </div>
  {/if}
{/if}

<!-- Attack instructions -->
<section class="grid" style="margin-top: 2rem;">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Log in to CyberCart</h2>
    <p>Use a login URL from the CSV. You'll see your name in the top-right corner of the nav.</p>
    <a class="button secondary" href="/login" style="display:inline-block; margin-top: 1rem;">Go to Login</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Visit the Attacker Site</h2>
    <p>While still logged in, open the attacker's page. It silently changes your display name.</p>
    <a class="button" href="http://localhost:7000" target="_blank" rel="noreferrer" style="display:inline-block; margin-top: 1rem;">
      Open Phishing Page ↗
    </a>
    <br />
    <a class="button secondary" href="http://localhost:7000/demo" target="_blank" rel="noreferrer" style="display:inline-block; margin-top: 0.5rem;">
      Open Demo Mode ↗
    </a>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Come back &amp; reload</h2>
    <p>
      Return here and reload the page. Your name in the nav should now read
      <code>H4CKED_BY_ATTACKER</code>.
    </p>
    <button class="button secondary" style="margin-top: 1rem;" on:click={() => location.reload()}>
      Reload page
    </button>
  </article>
</section>

<!-- The fix -->
<section class="card" style="margin-top: 2rem;">
  <h2>🛡 The Fix</h2>
  <p>
    In <code>backend/.env</code>, change the SameSite value and restart the backend:
  </p>
  <pre style="background:#0a0e15; border:1px solid #30394a; border-radius:9px; padding:1rem; margin:1rem 0; overflow-x:auto; color:#79c0ff;">SESSION_COOKIE_SAMESITE=lax
SESSION_COOKIE_SECURE=false   # for local HTTP testing</pre>
  <p>
    With <code>SameSite=Lax</code>, browsers will <strong>not</strong> send the cookie on
    cross-origin POST requests → the attacker's form gets a <strong>401 Unauthorized</strong>.
  </p>
  <p class="muted small" style="margin-top: 1rem;">
    Additional defence: add a CSRF token (random secret tied to the session, embedded in
    every form, verified server-side). An attacker can't read the real page's token due to
    same-origin policy, so the forged form is always missing it.
  </p>
</section>

<!-- Vulnerable endpoint info -->
<section class="card" style="margin-top: 1rem;">
  <h2>Vulnerable Endpoint</h2>
  <dl>
    <dt>Method &amp; Path</dt>
    <dd><code>POST /api/me/update</code></dd>
    <dt>Body type</dt>
    <dd><code>application/x-www-form-urlencoded</code> (plain HTML form — no JS needed)</dd>
    <dt>Auth</dt>
    <dd>Session cookie only. No CSRF token check.</dd>
    <dt>Effect</dt>
    <dd>Changes the victim's <code>display_name</code> in the database.</dd>
  </dl>
</section>
