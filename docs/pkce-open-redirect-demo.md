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
