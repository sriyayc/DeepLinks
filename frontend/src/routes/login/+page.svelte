<script lang="ts">
  let username = "alice";
  let password = "alice123";
  let message = "";

  async function login() {
    const res = await fetch("http://localhost:8000/api/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("cybercart_user", JSON.stringify(data.user));
      message = `Logged in as ${data.user.username}`;
    } else {
      message = data.detail ?? "Login failed";
    }
  }
</script>

<h1>Login</h1>

<section class="card form">
  <label>
    Username
    <input bind:value={username} />
  </label>

  <label>
    Password
    <input type="password" bind:value={password} />
  </label>

  <button class="button" on:click={login}>Login</button>

  <p class="muted">
    Workshop account: alice / alice123
  </p>

  {#if message}
    <p>{message}</p>
  {/if}
</section>
