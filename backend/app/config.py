import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    STRICT_AUTHZ: bool = os.getenv("STRICT_AUTHZ", "true").lower() == "true"

    SESSION_COOKIE_HTTPONLY: bool = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    # "none" is required for the cross-origin CSRF/attacker-site demo to work at all.
    # NOTE: browsers require Secure=True whenever SameSite=None, which means the
    # shop must be served over HTTPS (e.g. via mkcert) for that cookie to actually
    # be set. Switch to "lax" + SESSION_COOKIE_SECURE=false for local http-only testing
    # of everything except the live CSRF demo.
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "none").lower()
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"

    PKCE_ENFORCED: bool = os.getenv("PKCE_ENFORCED", "false").lower() == "true"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


settings = Settings()