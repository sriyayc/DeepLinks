<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { publicOauthBaseUrl, publicOauthClientId, publicOauthRedirectUri } from "$lib/api";
  import { takePkceState } from "$lib/oauth";

  let status: "exchanging" | "success" | "error" = "exchanging";
  let detail = "";
  let accessToken = "";

  onMount(async () => {
    const code = page.url.searchParams.get("code");
    const state = page.url.searchParams.get("state");
    const oauthError = page.url.searchParams.get("error");

    if (oauthError) {
      status = "error";
      detail = oauthError;
      return;
    }

    if (!code || !state) {
      status = "error";
      detail = "Missing code or state in callback URL.";
      return;
    }

    const codeVerifier = takePkceState(state);
    if (!codeVerifier) {
      status = "error";
      detail = "No matching code_verifier found for this state (expired or wrong browser tab?).";
      return;
    }

    try {
      const res = await fetch(`${publicOauthBaseUrl}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          grant_type: "authorization_code",
          code,
          client_id: publicOauthClientId,
          redirect_uri: publicOauthRedirectUri,
          code_verifier: codeVerifier,
        }),
      });

      const data = await res.json();

      if (!res.ok || data.error) {
        status = "error";
        detail = data.error ?? "Token exchange failed";
        return;
      }

      accessToken = data.access_token;
      status = "success";
      window.dispatchEvent(new CustomEvent("auth-changed"));

      setTimeout(() => goto("/"), 1200);
    } catch {
      status = "error";
      detail = "Could not reach the OAuth server to exchange the code.";
    }
  });
</script>

<p class="eyebrow">CYBERID CALLBACK</p>
<h1>Signing you in</h1>

{#if status === "exchanging"}
  <p class="muted">Exchanging authorization code for a token…</p>
{:else if status === "success"}
  <div class="notice">
    <strong>Logged in via CyberID.</strong>
    <p class="small muted" style="margin-top:0.4rem;">
      Token: <code>{accessToken}</code>
    </p>
    <p class="small muted">Redirecting to the homepage…</p>
  </div>
{:else}
  <div class="notice vulnerable">
    <strong>Login failed:</strong> {detail}
  </div>
{/if}

<style>
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>