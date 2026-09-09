<script lang="ts">
  let url = "https://localhost:5173/product/1";
  let result: any = null;
  let loading = false;

  async function inspect() {
    loading = true;
    const res = await fetch("http://localhost:8000/api/agent/inspect", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ url })
    });
    result = await res.json();
    loading = false;
  }
</script>

<p class="eyebrow">AGENT LAB</p>
<h1>CyberCart Assistant</h1>
<p class="lead">
  Give the assistant a link. The base implementation only inspects it;
  workshop exercises can add controlled actions and security policies.
</p>

<section class="card form">
  <label>
    Link
    <input bind:value={url} />
  </label>

  <button class="button" on:click={inspect} disabled={loading}>
    {loading ? "Inspecting..." : "Inspect link"}
  </button>
</section>

{#if result}
  <section class="card">
    <h2>Agent inspection</h2>
    <dl>
      <dt>Scheme</dt><dd>{result.scheme || "(none)"}</dd>
      <dt>Domain</dt><dd>{result.domain || "(none)"}</dd>
      <dt>Path</dt><dd>{result.path || "/"}</dd>
      <dt>Query</dt><dd>{result.query || "(none)"}</dd>
      <dt>Proposed action</dt><dd>{result.proposed_action}</dd>
    </dl>
    <div class="notice">No action was executed.</div>
  </section>
{/if}
