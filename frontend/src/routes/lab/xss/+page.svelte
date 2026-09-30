<script lang="ts">
  const payload = "<img src=x onerror=alert('XSS')>";
  const exploitUrl = "/search?q=" + encodeURIComponent(payload);
  const fixedUrl = "/search?q=" + encodeURIComponent(payload) + "&safe=true";
</script>

<p class="eyebrow">WORKSHOP · LAB 2</p>
<h1>Reflected XSS</h1>

<p class="lead">
  The search page reflects your query back into the page. In vulnerable mode it is rendered
  as raw HTML, so injected markup and scripts run in your browser.
</p>

<div class="notice vulnerable">
  <strong>⚠ VULNERABLE SINK</strong> — the search query is rendered with raw HTML output
  (<code>{"{@html query}"}</code>) unless <code>safe=true</code> is set.
</div>

<section class="grid lab-steps">
  <article class="card">
    <span class="badge">STEP 1</span>
    <h2>Open search</h2>
    <p>Any normal search reflects your term back onto the page.</p>
    <a class="button" href="/search">Go to search ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 2</span>
    <h2>Inject a payload</h2>
    <p>This search term is not a word — it's HTML that runs a script:</p>
    <div class="ciphertext"><code>{payload}</code></div>
    <a class="button" href={exploitUrl} target="_blank" rel="noreferrer">Run the payload ↗</a>
  </article>

  <article class="card">
    <span class="badge">STEP 3</span>
    <h2>Apply the fix</h2>
    <p>The same payload with <code>&amp;safe=true</code> is shown as harmless text — no pop-up.</p>
    <a class="button secondary" href={fixedUrl} target="_blank" rel="noreferrer">Run with the fix ↗</a>
  </article>
</section>

<section class="card lab-section">
  <h2>The vulnerable behaviour</h2>
  <dl>
    <dt>Where</dt>
    <dd><code>/search?q=…</code> reflects the query into the page.</dd>
    <dt>Flaw</dt>
    <dd>The query is rendered as raw HTML, so tags and event handlers execute.</dd>
    <dt>Effect</dt>
    <dd>Attacker-controlled JavaScript runs in the victim's session.</dd>
  </dl>
</section>

<section class="card lab-section">
  <h2>The fix</h2>
  <p>Render the query through the framework's escaped expression so it is always treated as
  text, never as markup — the same input then displays harmlessly.</p>
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
