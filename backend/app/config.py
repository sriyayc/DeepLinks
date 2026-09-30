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


    # =====================================================
    # SIMPLE WORKSHOP LOGIN
    # =====================================================
    # Shared password so participants can log in with just their numeric ID
    # (1001-1150) + this password, instead of a long token link.
    WORKSHOP_PASSWORD: str = os.getenv(
        "WORKSHOP_PASSWORD",
        "cybercart",
    )


    # =====================================================
    # CHATBOT RATE LIMIT (per participant, rolling window)
    # =====================================================
    CHAT_RATE_LIMIT_MAX: int = int(
        os.getenv("CHAT_RATE_LIMIT_MAX", "20")
    )

    CHAT_RATE_LIMIT_WINDOW_SECONDS: int = int(
        os.getenv("CHAT_RATE_LIMIT_WINDOW_SECONDS", "600")
    )


settings = Settings()