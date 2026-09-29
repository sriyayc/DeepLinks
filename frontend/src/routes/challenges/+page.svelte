<script lang="ts">
  import { challenges, checkChallengeAnswer } from "$lib/challenges";
  import type { Challenge } from "$lib/challenges";

  let submissions: Record<string, string> = {};
  let results: Record<string, boolean> = {};
  let solved: Record<string, boolean> = {};
  let pending: Record<string, boolean> = {};
  let errors: Record<string, string> = {};

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
      if (correct) solved = { ...solved, [challenge.id]: true };
    } catch {
      errors = { ...errors, [challenge.id]: "Could not check your flag. Please try again." };
    } finally {
      pending = { ...pending, [challenge.id]: false };
    }
  }
</script>

<svelte:head>
  <title>Challenges — CyberCart</title>
</svelte:head>

<p class="eyebrow">WORKSHOP CHALLENGES</p>
<h1>Challenges</h1>
<p class="lead">A few simple questions to check what you've learned.</p>

{#if challenges.length}
  <ol class="question-list">
    {#each challenges as question, index (question.id)}
      <li class="card">
        <div class="card-heading">
          <span class="badge">Challenge {index + 1}{question.category ? ` · ${question.category}` : ""}</span>
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
          <details>
            <summary>Need a hint?</summary>
            <p class="hint">{question.hint}</p>
            {#if question.toolUrl}
              <a class="button secondary tool-link" href={question.toolUrl} target="_blank" rel="noopener noreferrer">{question.toolLabel ?? "Open CyberChef ROT13 ↗"}</a>
            {/if}
          </details>
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
                  {results[question.id] ? "Correct! Challenge solved." : "Not quite. Check your flag and try again."}
                </p>
              {/if}
            </div>
          </form>
        {/if}
      </li>
    {/each}
  </ol>
{:else}
  <section class="card empty-state">
    <h2>Challenges coming soon</h2>
    <p class="muted">Check back here for the workshop challenges.</p>
    <a class="button secondary" href="/products">Back to the shop</a>
  </section>
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
  .tool-link { margin-left: 0; margin-top: 1rem; }
  .flag-form { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #222a38; }
  .flag-controls { display: flex; gap: 0.75rem; margin-top: 0.6rem; }
  .flag-controls input { flex: 1; min-width: 0; }
  .flag-controls button { white-space: nowrap; }
  .feedback { margin-bottom: 0; }
  @media (max-width: 500px) { .flag-controls { flex-direction: column; } }
</style>