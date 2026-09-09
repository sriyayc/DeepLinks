from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import secrets

app = FastAPI(title="CyberID — Fake OAuth Provider")

# In-memory demo state. Never use this as a real OAuth implementation.
clients = {
    "cybercart": {
        "client_id": "cybercart",
        "name": "CyberCart",
        "redirect_uris": [
            "http://localhost:5173/oauth/callback"
        ],
    }
}

codes = {}

@app.get("/")
def root():
    return {
        "service": "CyberID",
        "message": "Fake OAuth provider for the local workshop",
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

    # Baseline intentionally keeps this provider simple.
    # Add your workshop's redirect-validation challenge here.
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

    # Baseline token exchange. Add PKCE verification as a workshop step.
    if record["client_id"] != client_id:
        return {"error": "invalid_grant"}

    del codes[code]

    return {
        "access_token": "demo-token-" + secrets.token_urlsafe(12),
        "token_type": "Bearer",
        "user": record["user"],
    }
