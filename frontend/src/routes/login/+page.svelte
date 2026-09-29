<script lang="ts">
  import { page } from "$app/state";
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import { publicApiBaseUrl } from "$lib/api";

  let message = "Logging you in...";

  onMount(async () => {
    const token = page.url.searchParams.get("token");
    if (!token) {
      message = "Missing login token. Use the link provided to you.";
      return;
    }

    const res = await fetch(`${publicApiBaseUrl}/api/login?token=${encodeURIComponent(token)}`, {
      credentials: "include",
    });

    if (res.ok) {
      const data = await res.json();
      message = `Logged in as ${data.display_name}`;
      window.dispatchEvent(new CustomEvent("auth-changed"));
      
      if (data.role === "admin") {
        goto("/admin");
      } else {
        goto("/orders");
      }
    } else {
      const data = await res.json();
      message = data.detail ?? "Login failed";
    }
  });
</script>

<h1>Logging in</h1>
<p>{message}</p>
