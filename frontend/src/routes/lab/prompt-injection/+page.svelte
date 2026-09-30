<script lang="ts">
  import { publicAttackerBaseUrl } from "$lib/api";
</script>

<p class="eyebrow">WORKSHOP · LAB 5</p>
<h1>Prompt Injection — AI Chatbot</h1>

<p class="lead">
  The shopping assistant reads catalogue data — including a product's seller note. A hidden
  instruction planted in that note makes the assistant recommend an attacker's link, even
  though the attacker never talks to the AI directly.
</p>

<div class="notice vulnerable">
  <strong>⚠ INDIRECT PROMPT INJECTION</strong> — untrusted retrieved content is treated as
  instructions the model follows.
</div>

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Open the assistant</h2>
    <p>Use the chat widget at the bottom-right of any shop page.</p>
    <a class="button" href="/products">Go to the shop ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Ask about deals</h2>
    <p>Ask the assistant:</p>
    <div class="ciphertext"><code>Any laptop deals today?</code></div>
    <p class="muted small">It recommends an "Editor's Pick" link — planted by the seller note.</p>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Follow the link</h2>
    <p>The recommended link is a fake login (phishing). Type anything and it reveals the simulation.</p>
    <a class="button" href={`${publicAttackerBaseUrl}/editor-pick`} target="_blank" rel="noreferrer">Open the recommended link ↗</a>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable behaviour</h2>
  <dl>
    <dt>Where</dt>
    <dd>The assistant's context includes an untrusted seller note.</dd>
    <dt>Flaw</dt>
    <dd>Instructions hidden in that data are followed as if they came from the operator.</dd>
    <dt>Effect</dt>
    <dd>The assistant steers shoppers to an attacker-controlled phishing page.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>
    Treat all retrieved content as untrusted <em>data</em>, never instructions. The protected
    assistant ignores instructions hidden in catalogue data and refuses to promote links outside
    the shop.
  </p>
</section>

<style>
  .lab-steps,
  .lab-section {
    margin-top: 2rem;
  }
  .lab-steps .button {
    margin-top: 0.75rem;
  }
  .ciphertext {
    padding: 1rem;
    border: 1px solid #30394a;
    border-radius: 10px;
    background: #090c12;
    margin: 0.75rem 0;
  }
  .ciphertext code {
    overflow-wrap: anywhere;
    user-select: all;
  }
  .vulnerable {
    border-color: #f85149;
    background: #1a0d0d;
  }
</style>
