<svelte:head>
  <title>Admin Dashboard — CyberCart</title>
</svelte:head>

<script>
  import { publicApiBaseUrl } from "$lib/api";

  let users = [];
  let error = "";
  let loading = true;

  async function fetchUsers() {
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/admin/users`, { credentials: "include" });
      if (!res.ok) {
        error = `${res.status} — ${(await res.json()).detail || res.statusText}`;
        return;
      }
      users = await res.json();
    } catch (e) {
      error = "Could not reach the API.";
    } finally {
      loading = false;
    }
  }

  fetchUsers();
</script>

<h1>Admin Dashboard</h1>
<p class="muted small">Internal user management panel — authorized personnel only.</p>

{#if loading}
  <p class="muted">Loading…</p>
{:else if error}
  <div class="notice" style="border-color:#6b3030;background:#1a1010">
    <strong>Access denied:</strong> {error}
  </div>
{:else}
  <p class="muted small">{users.length} users</p>
  <div style="overflow-x:auto">
    <table class="admin-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Role</th>
        </tr>
      </thead>
      <tbody>
        {#each users as u}
          <tr>
            <td>{u.id}</td>
            <td>{u.display_name}</td>
            <td>{u.email}</td>
            <td>
              <span class="badge" class:admin-badge={u.role === "admin"}>
                {u.role}
              </span>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .admin-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    font-size: 0.9rem;
  }
  .admin-table th,
  .admin-table td {
    text-align: left;
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid #222a38;
  }
  .admin-table th {
    color: #7f8ba0;
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .admin-table tr:hover td {
    background: #10151f;
  }
  .admin-badge {
    border-color: #3d6b30 !important;
    color: #8fdf6f;
  }
</style>
