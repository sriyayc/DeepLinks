import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    # =====================================================
    # AUTHORIZATION
    # =====================================================

    STRICT_AUTHZ: bool = (
        os.getenv(
            "STRICT_AUTHZ",
            "true",
        ).lower()
        == "true"
    )


    # =====================================================
    # SESSION / CSRF WORKSHOP SETTINGS
    # =====================================================

    SESSION_COOKIE_HTTPONLY: bool = (
        os.getenv(
            "SESSION_COOKIE_HTTPONLY",
            "true",
        ).lower()
        == "true"
    )


    # "none" is required for the cross-origin CSRF
    # attacker-site demonstration.
    #
    # Browsers require Secure=True whenever
    # SameSite=None.

    SESSION_COOKIE_SAMESITE: str = (
        os.getenv(
            "SESSION_COOKIE_SAMESITE",
            "none",
        ).lower()
    )


    SESSION_COOKIE_SECURE: bool = (
        os.getenv(
            "SESSION_COOKIE_SECURE",
            "true",
        ).lower()
        == "true"
    )


    # =====================================================
    # OAUTH / PKCE
    # =====================================================

    PKCE_ENFORCED: bool = (
        os.getenv(
            "PKCE_ENFORCED",
            "false",
        ).lower()
        == "true"
    )


    # =====================================================
    # AI AGENT
    # =====================================================

    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        "",
    )


    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )


    AGENT_DEMO_LINK: str = os.getenv(
        "AGENT_DEMO_LINK",
        "http://evil.local/editor-pick",
    )


settings = Settings()