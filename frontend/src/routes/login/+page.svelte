<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import {
    publicApiBaseUrl,
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

  // --- Existing participant magic-link flow (Task 1) -----------------------
  let message = "Logging you in...";
  let hasToken = false;

  // --- Task 5: CyberID (OAuth/PKCE) demo login ------------------------------
  let username = "";
  let password = "";
  let status: "idle" | "checking" | "blocked" | "error" = "idle";
  let statusDetail = "";
  let pkceMode: { pkce_enforced: boolean; mode: string; note: string } | null = null;

  onMount(async () => {
    const token = page.url.searchParams.get("token");
    hasToken = Boolean(token);

    if (!hasToken) {
      try {
        const res = await fetch(`${publicOauthBaseUrl}/lab/pkce-status`);
        if (res.ok) pkceMode = await res.json();
      } catch {
        pkceMode = null;
      }
      return;
    }

    const res = await fetch(`${publicApiBaseUrl}/api/login?token=${encodeURIComponent(token!)}`, {
      credentials: "include",
    });

    if (res.ok) {
      const data = await res.json();
      message = `Logged in as ${data.display_name}`;
      window.dispatchEvent(new CustomEvent("auth-changed"));
      goto("/orders");
    } else {
      const data = await res.json();
      message = data.detail ?? "Login failed";
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

{#if hasToken}
  <h1>Logging in</h1>
  <p>{message}</p>
{:else}
  <p class="eyebrow">SIGN IN</p>
  <h1>Login</h1>
  <p class="lead">Sign in to CyberCart with CyberID.</p>

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
    Demo login — any username/password is accepted. This form exists to
    demonstrate Task 5 (OAuth open redirect + PKCE); it does not check your
    password against anything.
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

  <section class="card lab-section" style="margin-top:2rem;">
    <h2>What just happened?</h2>
    <p class="small">
      Clicking "Sign in with CyberID" builds an <code>/authorize</code> request the
      way a phishing link would — with <code>redirect_uri</code> pointed at an
      attacker-controlled site. In vulnerable mode, CyberID doesn't check
      <code>redirect_uri</code> against the app's registered callback, so it
      issues a real authorization code to that attacker site. In fixed mode,
      CyberID rejects the mismatched <code>redirect_uri</code>, so this page
      falls back to the real callback and logs you in normally.
    </p>
    <p class="small muted">
      See <code>docs/pkce-open-redirect-demo.md</code> for the full write-up.
    </p>
  </section>
{/if}

<style>
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>