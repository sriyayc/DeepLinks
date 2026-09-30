<script lang="ts">
  import { onMount } from "svelte";
  import {
    publicOauthBaseUrl,
    publicOauthClientId,
    publicOauthRedirectUri,
    publicOauthAttackerRedirectUri,
  } from "$lib/api";
  import {
    generateState,
    generateCodeVerifier,
    generateCodeChallenge,
    buildAuthorizeUrl,
    probeAuthorize,
    storePkceState,
  } from "$lib/oauth";

  let username = "";
  let password = "";
  let status: "idle" | "checking" | "blocked" | "error" = "idle";
  let statusDetail = "";
  let pkceMode: { pkce_enforced: boolean; mode: string; note: string } | null = null;

  onMount(async () => {
    try {
      const res = await fetch(`${publicOauthBaseUrl}/lab/pkce-status`);
      if (res.ok) pkceMode = await res.json();
    } catch {
      pkceMode = null;
    }
  });

  async function signInWithCyberId() {
    status = "checking";
    statusDetail = "";

    const state = generateState();
    const verifier = generateCodeVerifier();
    const challenge = await generateCodeChallenge(verifier);
    storePkceState(state, verifier);

    const attackerAuthorizeUrl = buildAuthorizeUrl(publicOauthBaseUrl, {
      clientId: publicOauthClientId,
      redirectUri: publicOauthAttackerRedirectUri,
      state,
      codeChallenge: challenge,
    });

    let probe: Awaited<ReturnType<typeof probeAuthorize>>;
    try {
      probe = await probeAuthorize(attackerAuthorizeUrl);
    } catch (err) {
      status = "error";
      statusDetail = "Could not reach the OAuth server. Is oauth-server running?";
      return;
    }

    if (probe.willRedirect) {
      window.location.href = attackerAuthorizeUrl;
      return;
    }

    status = "blocked";
    statusDetail =
      typeof probe.body === "object" && probe.body && "error" in (probe.body as Record<string, unknown>)
        ? String((probe.body as Record<string, unknown>).error)
        : "invalid_redirect_uri";

    const realState = generateState();
    const realVerifier = generateCodeVerifier();
    const realChallenge = await generateCodeChallenge(realVerifier);
    storePkceState(realState, realVerifier);

    const realAuthorizeUrl = buildAuthorizeUrl(publicOauthBaseUrl, {
      clientId: publicOauthClientId,
      redirectUri: publicOauthRedirectUri,
      state: realState,
      codeChallenge: realChallenge,
    });

    window.location.href = realAuthorizeUrl;
  }

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    signInWithCyberId();
  }
</script>

<p class="eyebrow">WORKSHOP · LAB 1 · TASK 5</p>
<h1>Sign in with CyberID</h1>
<p class="lead">Single sign-on demo — OAuth open redirect + PKCE.</p>

{#if pkceMode}
  <div class="notice" class:vulnerable={!pkceMode.pkce_enforced}>
    <strong>{pkceMode.pkce_enforced ? "🛡 FIXED" : "⚠ VULNERABLE"} MODE</strong>
    — <code>PKCE_ENFORCED={String(pkceMode.pkce_enforced)}</code>
    <p class="muted small" style="margin-top:0.4rem;">{pkceMode.note}</p>
  </div>
{/if}

<form class="form" on:submit={handleSubmit}>
  <label>
    Username
    <input type="text" bind:value={username} placeholder="alice" autocomplete="username" />
  </label>
  <label>
    Password
    <input
      type="password"
      bind:value={password}
      placeholder="••••••••"
      autocomplete="current-password"
    />
  </label>
  <div class="actions">
    <button class="button" type="submit" disabled={status === "checking"}>
      {status === "checking" ? "Signing in…" : "Sign in with CyberID"}
    </button>
  </div>
</form>

<p class="muted small" style="margin-top:0.75rem;">
  Demo login — any username/password is accepted. This form exists to demonstrate the
  OAuth open-redirect + PKCE lab; it does not check your password against anything.
</p>

{#if status === "blocked"}
  <div class="notice">
    <strong>Spoofed redirect_uri rejected</strong> (<code>{statusDetail}</code>) — continuing with the
    real, registered callback instead…
  </div>
{/if}

{#if status === "error"}
  <div class="notice vulnerable">
    <strong>Error:</strong> {statusDetail}
  </div>
{/if}

<section class="card lab-section">
  <h2>What just happened?</h2>
  <p class="small">
    Clicking "Sign in with CyberID" builds an <code>/authorize</code> request the way a phishing
    link would — with <code>redirect_uri</code> pointed at an attacker-controlled site. In
    vulnerable mode, CyberID doesn't check <code>redirect_uri</code> against the app's registered
    callback, so it issues a real authorization code to that attacker site. In fixed mode, CyberID
    rejects the mismatched <code>redirect_uri</code>, so this page falls back to the real callback
    and logs you in normally.
  </p>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p class="small">
    Set <code>PKCE_ENFORCED=true</code> on the oauth-server: <code>redirect_uri</code> must exactly
    match a registered URI, and the server recomputes <code>S256(code_verifier)</code> and rejects
    any mismatch.
  </p>
</section>

<style>
  .lab-section {
    margin-top: 2rem;
  }
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>
