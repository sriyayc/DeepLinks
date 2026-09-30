<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { publicApiBaseUrl, publicChallengesEnabled } from "$lib/api";

  let leaderboard: { participant_id: number; display_name: string; score: number }[] = [];
  let timer: ReturnType<typeof setInterval> | undefined;

  async function load() {
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/challenges/leaderboard`, { credentials: "include" });
      if (res.ok) leaderboard = await res.json();
    } catch {
      // ignore
    }
  }

  onMount(() => {
    if (!publicChallengesEnabled) return;
    load();
    timer = setInterval(load, 20000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<svelte:head>
  <title>Leaderboard — CyberCart</title>
</svelte:head>

<p class="eyebrow">WORKSHOP CHALLENGES</p>
<h1>🏆 Leaderboard</h1>

{#if !publicChallengesEnabled}
  <section class="card empty-state">
    <h2>🔒 Leaderboard is locked</h2>
    <p class="muted">The challenges open later in the session. Check back then!</p>
    <a class="button secondary" href="/products">Back to the shop</a>
  </section>
{:else}
  <div class="head-row">
    <p class="lead">Top scorers across the CTF challenges.</p>
    <button class="button secondary small-btn" on:click={load}>Refresh</button>
  </div>

  {#if leaderboard.length}
    <section class="card">
      <ol class="lb-list">
        {#each leaderboard as row, i (row.participant_id)}
          <li>
            <span class="lb-rank">{i + 1}</span>
            <span class="lb-name">{row.display_name}</span>
            <span class="lb-score">{row.score}</span>
          </li>
        {/each}
      </ol>
    </section>
  {:else}
    <section class="card empty-state">
      <p class="muted">No scores yet — solve a challenge to get on the board.</p>
      <a class="button secondary" href="/challenges">Go to challenges →</a>
    </section>
  {/if}
{/if}

<style>
  .head-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
  }
  .empty-state { margin-top: 2rem; }
  .empty-state .button { margin-left: 0; margin-top: 0.75rem; }
  .small-btn { margin: 0; padding: 0.3rem 0.8rem; font-size: 0.85rem; }
  .lb-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.4rem;
  }
  .lb-list li {
    display: grid;
    grid-template-columns: 2.5rem 1fr auto;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    background: #10151e;
  }
  .lb-rank { color: #aab4c6; text-align: center; font-variant-numeric: tabular-nums; }
  .lb-score { color: #8fdbab; font-variant-numeric: tabular-nums; font-weight: 600; }
</style>
