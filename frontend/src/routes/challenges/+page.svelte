<script lang="ts">
  import { onMount } from "svelte";
  import { challenges, checkChallengeAnswer, challengeTier } from "$lib/challenges";
  import type { Challenge } from "$lib/challenges";
  import { publicApiBaseUrl, publicChallengesEnabled } from "$lib/api";

  let submissions: Record<string, string> = {};
  let results: Record<string, boolean> = {};
  let solved: Record<string, boolean> = {};
  let hinted: Record<string, boolean> = {};
  let revealedHints: Record<string, boolean> = {};
  let hintPending: Record<string, boolean> = {};
  let hintErrors: Record<string, string> = {};
  let pending: Record<string, boolean> = {};
  let errors: Record<string, string> = {};

  let score = 0;
  let loggedIn = true;

  async function loadMe() {
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/challenges/me`, { credentials: "include" });
      if (res.status === 401) {
        loggedIn = false;
        return;
      }
      if (!res.ok) return;
      const data = await res.json();
      loggedIn = true;
      score = data.score ?? 0;
      solved = Object.fromEntries((data.solved ?? []).map((id: string) => [id, true]));
      hinted = Object.fromEntries((data.hinted ?? []).map((id: string) => [id, true]));
      revealedHints = { ...hinted };
    } catch {
      // leave defaults; scoring simply won't record
    }
  }

  async function submitAnswer(challenge: Challenge) {
    if (pending[challenge.id]) return;
    pending = { ...pending, [challenge.id]: true };
    errors = { ...errors, [challenge.id]: "" };
    const nextResults = { ...results };
    delete nextResults[challenge.id];
    results = nextResults;
    try {
      const correct = await checkChallengeAnswer(challenge, submissions[challenge.id] ?? "");
      results = { ...results, [challenge.id]: correct };
      if (correct && !solved[challenge.id]) {
        solved = { ...solved, [challenge.id]: true };
        // Record the solve for the leaderboard (server dedupes; ignore if not logged in).
        try {
          const res = await fetch(`${publicApiBaseUrl}/api/challenges/solve`, {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ challenge_id: challenge.id }),
          });
          if (res.ok) {
            const data = await res.json();
            score = data.score ?? score;
          } else if (res.status === 401) {
            loggedIn = false;
          }
        } catch {
          // scoring unavailable; the solve still shows locally
        }
      }
    } catch {
      errors = { ...errors, [challenge.id]: "Could not check your flag. Please try again." };
    } finally {
      pending = { ...pending, [challenge.id]: false };
    }
  }

  async function revealHint(challenge: Challenge) {
    if (revealedHints[challenge.id] || hintPending[challenge.id]) return;
    // Already paid for this hint earlier — show it without charging again.
    if (hinted[challenge.id]) {
      revealedHints = { ...revealedHints, [challenge.id]: true };
      return;
    }
    hintPending = { ...hintPending, [challenge.id]: true };
    hintErrors = { ...hintErrors, [challenge.id]: "" };
    try {
      const res = await fetch(`${publicApiBaseUrl}/api/challenges/hint`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ challenge_id: challenge.id }),
      });
      if (res.ok) {
        const data = await res.json();
        score = data.score ?? score;
        hinted = { ...hinted, [challenge.id]: true };
        // Only reveal once the points have actually been deducted.
        revealedHints = { ...revealedHints, [challenge.id]: true };
      } else if (res.status === 401) {
        loggedIn = false;
        hintErrors = { ...hintErrors, [challenge.id]: "Log in to use hints." };
      } else {
        hintErrors = { ...hintErrors, [challenge.id]: "Could not deduct points. Try again." };
      }
    } catch {
      hintErrors = { ...hintErrors, [challenge.id]: "Could not reach the server." };
    } finally {
      hintPending = { ...hintPending, [challenge.id]: false };
    }
  }

  onMount(() => {
    if (!publicChallengesEnabled) return;
    loadMe();
  });
</script>

<svelte:head>
  <title>Challenges — CyberCart</title>
</svelte:head>

<p class="eyebrow">WORKSHOP CHALLENGES</p>
<h1>Challenges</h1>

{#if !publicChallengesEnabled}
  <section class="card empty-state">
    <h2>🔒 Challenges are locked</h2>
    <p class="muted">The CTF challenges open later in the session. Check back then!</p>
    <a class="button secondary" href="/products">Back to the shop</a>
  </section>
{:else}
  <p class="lead">Solve challenges to score points. Hints cost points, so use them wisely.</p>

  <div class="score-row">
    <div class="score-chip">Your score: <strong>{score}</strong></div>
    <a class="button secondary small-btn" href="/leaderboard">🏆 Leaderboard →</a>
    {#if !loggedIn}<span class="muted small">Log in to record your score.</span>{/if}
  </div>

  <ol class="question-list">
    {#each challenges as question, index (question.id)}
      {@const tier = challengeTier(question)}
      <li class="card">
        <div class="card-heading">
          <span class="badge">Challenge {index + 1}{question.category ? ` · ${question.category}` : ""} · {tier.points} pts</span>
          {#if solved[question.id]}<span class="solved">✓ Solved</span>{/if}
        </div>
        {#if question.title}<h2>{question.title}</h2>{/if}
        <p class="prompt">{question.prompt}</p>
        {#if question.challengeUrl}
          <a class="button secondary tool-link" href={question.challengeUrl} target="_blank" rel="noopener noreferrer">{question.challengeLabel ?? "Open challenge ↗"}</a>
        {/if}
        {#if question.downloadUrl}
          <a class="button secondary tool-link" href={question.downloadUrl} download>Download image ↓</a>
          <p class="muted small">Flag format: <code>{"layer8{...}"}</code></p>
        {/if}
        {#if question.ciphertext}
          <div class="ciphertext">
            <span class="muted small">Encoded message</span>
            <code>{question.ciphertext}</code>
          </div>
          <p class="muted small">Flag format: <code>{"layer8{...}"}</code></p>
        {/if}
        {#if question.cipherDetails}
          <details>
            <summary>Cipher details</summary>
            <p class="hint cipher-details">{question.cipherDetails}</p>
          </details>
        {/if}
        {#if question.hint}
          <div class="hint-block">
            {#if revealedHints[question.id]}
              <p class="hint">{question.hint}</p>
              {#if question.toolUrl}
                <a class="button secondary tool-link" href={question.toolUrl} target="_blank" rel="noopener noreferrer">{question.toolLabel ?? "Open CyberChef ROT13 ↗"}</a>
              {/if}
            {:else}
              <button class="button secondary" on:click={() => revealHint(question)} disabled={hintPending[question.id]}>
                {hintPending[question.id] ? "Deducting…" : `Reveal hint (−${tier.hintCost} pts)`}
              </button>
              {#if hintErrors[question.id]}<p class="feedback">{hintErrors[question.id]}</p>{/if}
            {/if}
          </div>
        {/if}
        {#if question.answerHash}
          <form class="flag-form" on:submit|preventDefault={() => submitAnswer(question)}>
            <label for={`flag-${question.id}`}>Your flag</label>
            <div class="flag-controls">
              <input id={`flag-${question.id}`} bind:value={submissions[question.id]} placeholder={"layer8{...}"}
                required maxlength="100" autocomplete="off" spellcheck="false" />
              <button class="button" disabled={pending[question.id]}>{pending[question.id] ? "Checking…" : "Check flag"}</button>
            </div>
            <div aria-live="polite">
              {#if errors[question.id]}<p class="feedback">{errors[question.id]}</p>{/if}
              {#if question.id in results}
                <p class="feedback" class:correct={results[question.id]}>
                  {results[question.id] ? `Correct! +${tier.points} points.` : "Not quite. Check your flag and try again."}
                </p>
              {/if}
            </div>
          </form>
        {/if}
      </li>
    {/each}
  </ol>
{/if}

<style>
  .question-list {
    display: grid;
    gap: 1rem;
    padding: 0;
    margin-top: 2rem;
    list-style: none;
  }

  .empty-state {
    margin-top: 2rem;
  }

  .empty-state .button {
    margin-left: 0;
    margin-top: 0.75rem;
  }

  summary {
    cursor: pointer;
    color: #aab4c6;
  }

  .prompt, .hint {
    line-height: 1.7;
  }
  .prompt { white-space: pre-line; }
  .cipher-details { white-space: pre-line; }

  .card-heading { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
  .solved, .correct { color: #8fdbab; }
  .ciphertext { display: grid; gap: 0.6rem; padding: 1.2rem; border: 1px solid #30394a; border-radius: 10px; background: #090c12; }
  .ciphertext code { font-size: clamp(1rem, 3vw, 1.3rem); overflow-wrap: anywhere; user-select: all; }
  details { margin-top: 1.5rem; }
  .hint-block { margin-top: 1.5rem; }
  .tool-link { margin-left: 0; margin-top: 1rem; }
  .flag-form { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #222a38; }
  .flag-controls { display: flex; gap: 0.75rem; margin-top: 0.6rem; }
  .flag-controls input { flex: 1; min-width: 0; }
  .flag-controls button { white-space: nowrap; }
  .feedback { margin-bottom: 0; }
  @media (max-width: 500px) { .flag-controls { flex-direction: column; } }

  .score-row { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-top: 1rem; }
  .score-chip { background: #10151e; border: 1px solid #30394a; border-radius: 999px; padding: 0.4rem 1rem; }
  .score-chip strong { color: #8fdbab; }
  .small-btn { margin: 0; padding: 0.3rem 0.8rem; font-size: 0.85rem; }
</style>
