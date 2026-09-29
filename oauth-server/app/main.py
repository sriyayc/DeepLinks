import hashlib
import base64
import os
import secrets
from urllib.parse import urlencode

from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(title="CyberID — Fake OAuth Provider")

# ---------------------------------------------------------------------------
# CORS: the frontend calls /authorize and /token directly via fetch() so it
# can inspect the result (redirect vs. invalid_redirect_uri error) before
# deciding where to send the browser next. Keep this scoped to the shop
# frontend's origins — never add the attacker origin here.
# ---------------------------------------------------------------------------
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_allowed_origins = [
    o.strip()
    for o in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Task 5 — PKCE / open-redirect lab toggle
#
# PKCE_ENFORCED=false (the default here) is the VULNERABLE mode:
#   - /authorize does not check redirect_uri against the client's registered
#     list, so an attacker can supply their own redirect_uri and have the
#     authorization code (and later the token) delivered to a site they
#     control instead of the real app.
#   - /token does not verify code_verifier against the code_challenge that
#     was issued, so PKCE is present in the flow but never actually checked.
#
# Set PKCE_ENFORCED=true (or flip the default below) for the FIXED mode:
#   - redirect_uri must exactly match one of the client's registered URIs.
#   - /token recomputes S256(code_verifier) and rejects the exchange if it
#     does not match the stored code_challenge.
#
# This flag only governs this local training instance; it does not affect
# any other/external system.
# ---------------------------------------------------------------------------
PKCE_ENFORCED = os.environ.get("PKCE_ENFORCED", "false").lower() == "true"

# In-memory demo state. Never use this as a real OAuth implementation.
clients = {
    "cybercart": {
        "client_id": "cybercart",
        "name": "CyberCart",
        "redirect_uris": [
            "http://localhost:5173/oauth/callback",
            "https://layer8-frontend.up.railway.app/oauth/callback",
        ],
    }
}

codes = {}


def verify_pkce(code_verifier: str | None, code_challenge: str | None, method: str | None) -> bool:
    """Recompute the code_challenge from the verifier and compare."""
    if not code_verifier or not code_challenge:
        return False
    if method == "plain":
        return secrets.compare_digest(code_verifier, code_challenge)
    # default / "S256"
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return secrets.compare_digest(computed, code_challenge)


@app.get("/")
def root():
    return {
        "service": "CyberID",
        "message": "Fake OAuth provider for the local workshop",
        "pkce_enforced": PKCE_ENFORCED,
    }


@app.get("/lab/pkce-status")
def pkce_status():
    """Check current mode for this task, same pattern as the CSRF lab."""
    return {
        "pkce_enforced": PKCE_ENFORCED,
        "mode": "fixed" if PKCE_ENFORCED else "vulnerable",
        "note": (
            "redirect_uri is validated and code_verifier is checked against "
            "code_challenge before a token is issued."
            if PKCE_ENFORCED
            else "redirect_uri is NOT validated against the registered list, "
            "and code_verifier is accepted without being checked. An "
            "attacker-supplied redirect_uri will receive the auth code."
        ),
    }


@app.get("/authorize")
def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str | None = None,
):
    if client_id not in clients:
        return {"error": "unknown_client"}

    if PKCE_ENFORCED:
        # FIXED: redirect_uri must be one of the client's registered URIs.
        if redirect_uri not in clients[client_id]["redirect_uris"]:
            return {"error": "invalid_redirect_uri"}
        if not code_challenge or code_challenge_method not in ("S256", "plain"):
            return {"error": "invalid_request", "detail": "PKCE code_challenge is required"}
    # VULNERABLE (default): redirect_uri is trusted as-is, so a caller can
    # point it at an attacker-controlled origin and still get a valid code.

    code = secrets.token_urlsafe(24)

    codes[code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "user": "alice",
    }

    params = {"code": code}
    if state:
        params["state"] = state

    return RedirectResponse(
        url=f"{redirect_uri}?{urlencode(params)}"
    )


@app.post("/token")
def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    code_verifier: str | None = Form(default=None),
):
    record = codes.get(code)

    if not record:
        return {"error": "invalid_grant"}

    if record["client_id"] != client_id:
        return {"error": "invalid_grant"}

    if PKCE_ENFORCED:
        # FIXED: redirect_uri must match what /authorize issued the code for,
        # and the verifier must match the original challenge.
        if redirect_uri != record["redirect_uri"]:
            return {"error": "invalid_grant"}
        if not verify_pkce(code_verifier, record["code_challenge"], record["code_challenge_method"]):
            return {"error": "invalid_grant", "detail": "PKCE verification failed"}
    # VULNERABLE (default): code_verifier is accepted without ever being
    # checked against the code_challenge from /authorize.

    del codes[code]

    return {
        "access_token": "demo-token-" + secrets.token_urlsafe(12),
        "token_type": "Bearer",
        "user": record["user"],
    }
