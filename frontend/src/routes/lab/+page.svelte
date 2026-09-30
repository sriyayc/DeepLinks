<p class="eyebrow">WORKSHOP</p>
<h1>CyberCart Security Labs</h1>
<p class="lead">Base application is ready. Add each vulnerability as an isolated lab.</p>

<section class="grid">
  <a class="card link-card" href="/products"><span class="badge">01</span><h2>Deep links</h2><p>Map URL schemes, paths, and parameters to application actions.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/search"><span class="badge">02</span><h2>Reflected XSS</h2><p>Compare unsafe reflection with framework-safe rendering.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/orders"><span class="badge">03</span><h2>IDOR</h2><p>Explore object identifiers and authorization boundaries.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/lab/csrf"><span class="badge">04</span><h2>CSRF</h2><p>Cookies + state-changing requests.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/login"><span class="badge">05</span><h2>Code exchange</h2><p>Trace an authorization code through the token exchange.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/login"><span class="badge">06</span><h2>PKCE</h2><p>Bind authorization codes to a client-generated verifier.</p><p class="muted small">→ Open</p></a>
  <a class="card link-card" href="/agent"><span class="badge">07</span><h2>Agent navigation</h2><p>Build a policy layer between untrusted links and agent actions.</p><p class="muted small">→ Open</p></a>
</section>

<style>
  .link-card { display: block; text-decoration: none; color: inherit; }
  .link-card:hover { border-color: #58a6ff; }
  .link-card .small { margin-top: 0.5rem; }
</style>

<div class="notice">
  <strong>Organizer note:</strong> Keep the vulnerable implementations local,
  fake, and clearly separated from the secure implementations.
</div>
