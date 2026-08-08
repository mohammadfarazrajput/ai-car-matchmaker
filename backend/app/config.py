"""Application settings.

Constitution Principle II (Zero-Key Demo): every integration credential below is
optional. Absent a key, the corresponding adapter selects its mock and the full
journey still completes. Only the LLM is a real dependency, and even that has an
`echo` provider so CI needs nothing.
"""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LlmProvider = Literal["google", "groq", "echo"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM -----------------------------------------------------------------
    llm_provider: LlmProvider = "echo"
    google_api_key: str = ""
    google_model: str = "gemini-3.5-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # --- Notification channels ----------------------------------------------
    resend_api_key: str = ""
    email_from: str = "onboarding@resend.dev"

    slack_bot_token: str = ""
    slack_channel: str = "#sales-leads"
    slack_lead_threshold: float = 0.90

    # --- Observability (STRETCH) --------------------------------------------
    observability_provider: Literal["phoenix", "langfuse", "none"] = "none"
    phoenix_collector_endpoint: str = "http://localhost:6006"
    phoenix_project_name: str = "car-matchmaker"

    # --- App wiring ----------------------------------------------------------
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    resume_token_ttl_s: int = 3600
    session_secret: str = "dev-only-not-a-secret"

    # --- Derived -------------------------------------------------------------

    def channel_modes(self) -> dict[str, str]:
        """Live-vs-mock per channel, surfaced by /health.

        Makes the zero-key state observable rather than inferred (FR-029).
        """
        return {
            "email": "live" if self.resend_api_key else "mock",
            "slack": "live" if self.slack_bot_token else "mock",
        }


settings = Settings()
