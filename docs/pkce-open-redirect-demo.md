# Task 5 — OAuth Open Redirect + Missing PKCE Verification

## Services

- OAuth server: `localhost:9000` (`oauth-server/`)
- "Malicious" site: `localhost:7001/oauth/callback` (`attacker-site/`) — a
  dummy sink that only displays whatever it receives, never forwards it
- Real app callback: `localhost:5173/oauth/callback` (`frontend/`)

## Vulnerable mode (default: `PKCE_ENFORCED=false`)

1. `/authorize` on the OAuth server accepts **any** `redirect_uri`, not just
   the ones registered for the client. An attacker can craft an authorize
   link that points `redirect_uri` at `http://localhost:7001/oauth/callback`
   instead of the real app.
2. If a logged-in user is tricked into opening that link, the OAuth server
   redirects them — with a valid authorization `code` — to the attacker's
   origin instead of CyberCart.
3. Separately, `/token` accepts a token exchange without ever checking that
   `code_verifier` matches the `code_challenge` that was issued at
   `/authorize`. Even if `redirect_uri` were fixed, a stolen `code` could
   still be exchanged for a token without knowing the original verifier.

Check current mode: `GET localhost:9000/lab/pkce-status`
## UI walkthrough (recommended for the workshop)

1. Start all four services.
2. Open `localhost:5173` and click **Login** in the nav — this goes to `/login`,
   which shows CyberID's current mode and a demo credentials form (any
   username/password is accepted; it isn't checked against anything).
3. Click **Sign in with CyberID**. The page builds an `/authorize` request the
   way a spoofed login link would: `redirect_uri` points at the attacker site
   (`PUBLIC_OAUTH_ATTACKER_REDIRECT_URI`, e.g. the deployed `attacker-site`).
   - **Vulnerable mode:** the OAuth server doesn't check `redirect_uri`, so
     the browser is redirected to the attacker's `/oauth/callback` with a real
     authorization code — the dummy sink displays it.
   - **Fixed mode:** the OAuth server rejects the mismatched `redirect_uri`
     (`invalid_redirect_uri`). The login page detects this and automatically
     retries with CyberCart's real, registered callback, completes the PKCE
     token exchange, and redirects to the homepage.
4. Flip `PKCE_ENFORCED` on the `oauth-server` service and repeat to see the
   other mode.
   
## Attack walkthrough (local only)

1. Start all four services (`docker compose up` or run each with `uvicorn`).
2. Log into CyberCart normally at `localhost:5173`.
3. Visit an authorize URL with a spoofed `redirect_uri`, e.g.:
   ```
   http://localhost:9000/authorize?response_type=code&client_id=cybercart&redirect_uri=http://localhost:7001/oauth/callback&state=abc
   ```
4. You land on `localhost:7001/oauth/callback`, which displays the leaked
   `code` value — demonstrating it went to the wrong origin.

## The fix

Set `PKCE_ENFORCED=true` for the `oauth-server` service, which:

- Rejects `/authorize` requests whose `redirect_uri` isn't in the client's
  registered `redirect_uris` list.
- Requires a `code_challenge` at `/authorize`.
- Recomputes `S256(code_verifier)` at `/token` and rejects the exchange if it
  doesn't match the stored `code_challenge`.

```python
if redirect_uri not in clients[client_id]["redirect_uris"]:
    return {"error": "invalid_redirect_uri"}
...
if not verify_pkce(code_verifier, record["code_challenge"], record["code_challenge_method"]):
    return {"error": "invalid_grant"}
```

Re-run the same attack URL in fixed mode and confirm it now returns
`invalid_redirect_uri` instead of issuing a code.
