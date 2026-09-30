<p class="eyebrow">WORKSHOP</p>
<h1>CyberCart Security Labs</h1>
<p class="lead">Each lab has a guided demo page: read the vulnerability, run the exploit, then apply the fix.</p>

<section class="grid">
  <a class="card link-card" href="/lab/oauth"><span class="badge">01</span><h2>OAuth open redirect + PKCE</h2><p>An unvalidated redirect_uri leaks the authorization code; PKCE binds it to the real app.</p><p class="muted small">→ Open lab</p></a>
  <a class="card link-card" href="/lab/xss"><span class="badge">02</span><h2>Reflected XSS</h2><p>An unescaped search term is rendered as HTML and runs in your browser.</p><p class="muted small">→ Open lab</p></a>
  <a class="card link-card" href="/lab/idor"><span class="badge">03</span><h2>IDOR</h2><p>Change an ID in the URL to read another participant's order.</p><p class="muted small">→ Open lab</p></a>
  <a class="card link-card" href="/lab/csrf"><span class="badge">04</span><h2>CSRF</h2><p>A cross-site page submits a state-changing form using your session cookie.</p><p class="muted small">→ Open lab</p></a>
  <a class="card link-card" href="/lab/prompt-injection"><span class="badge">05</span><h2>Prompt injection</h2><p>A hidden instruction in catalogue data steers the AI assistant to an attacker link.</p><p class="muted small">→ Open lab</p></a>
  <a class="card link-card" href="/lab/admin"><span class="badge">06</span><h2>Admin escalation</h2><p>An admin-only endpoint that never checks your role.</p><p class="muted small">→ Open lab</p></a>
</section>

<div class="notice">
  <strong>Organizer note:</strong> Keep the vulnerable implementations local,
  fake, and clearly separated from the secure implementations.
</div>

<style>
  .link-card { display: block; text-decoration: none; color: inherit; }
  .link-card:hover { border-color: #58a6ff; }
  .link-card .small { margin-top: 0.5rem; }
</style>
