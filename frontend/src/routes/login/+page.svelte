<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  // --- Participant magic-link flow (Task 1) --------------------------------
  let message = "Logging you in...";
  let hasToken = false;

  // --- Simple workshop login (numeric participant ID + shared password) -----
  let loginId = "";
  let loginPassword = "";
  let quickStatus: "idle" | "working" | "error" = "idle";
  let quickError = "";

  async function quickLogin(event: SubmitEvent) {
    event.preventDefault();
    quickStatus = "working";
    quickError = "";
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/login-id`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: Number(loginId),
          password: loginPassword,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        quickStatus = "error";
        quickError = data.detail ?? "Login failed";
        return;
      }
      window.dispatchEvent(new CustomEvent("auth-changed"));
      goto(data.role === "admin" ? "/admin" : "/orders");
    } catch {
      quickStatus = "error";
      quickError = "Could not reach the server.";
    }
  }

  onMount(async () => {
    const token = page.url.searchParams.get("token");
    hasToken = Boolean(token);
    if (!hasToken) return;

    const res = await fetch(`${publicApiBaseUrl}/api/login?token=${encodeURIComponent(token!)}`, {
      credentials: "include",
    });

    if (res.ok) {
      const data = await res.json();
      message = `Logged in as ${data.display_name}`;
      window.dispatchEvent(new CustomEvent("auth-changed"));
      goto(data.role === "admin" ? "/admin" : "/orders");
    } else {
      const data = await res.json();
      message = data.detail ?? "Login failed";
    }
  });
</script>

{#if hasToken}
  <h1>Logging in</h1>
  <p>{message}</p>
{:else}
  <p class="eyebrow">SIGN IN</p>
  <h1>Login</h1>

  <section class="card" style="margin-bottom:2rem;">
    <h2 style="margin-top:0;">Workshop sign-in</h2>
    <p class="small muted" style="margin-top:0;">
      Enter the participant number you were given and the workshop password.
    </p>
    <form class="form" on:submit={quickLogin}>
      <label>
        Participant ID
        <input type="number" bind:value={loginId} placeholder="1042" autocomplete="off" />
      </label>
      <label>
        Workshop password
        <input type="password" bind:value={loginPassword} placeholder="••••••••" autocomplete="off" />
      </label>
      <div class="actions">
        <button class="button" type="submit" disabled={quickStatus === "working"}>
          {quickStatus === "working" ? "Signing in…" : "Sign in"}
        </button>
      </div>
    </form>
    {#if quickStatus === "error"}
      <div class="notice vulnerable"><strong>Error:</strong> {quickError}</div>
    {/if}
  </section>

  <hr style="border:none; border-top:1px solid #30363d; margin:0 0 1.5rem;" />

  <section class="card">
    <h2 style="margin-top:0;">Or sign in with CyberID</h2>
    <p class="small muted" style="margin-top:0;">
      Single sign-on through the CyberID provider — opens the Task 5 OAuth lab.
    </p>
    <a class="button secondary" href="/lab/oauth">Sign in with CyberID ↗</a>
  </section>
{/if}

<style>
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>
