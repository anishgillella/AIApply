from __future__ import annotations

"""Configuration helpers for the LinkedIn Easy Apply agent."""

from dataclasses import dataclass
import os
from typing import Final

from dotenv import load_dotenv


REQUIRED_ENV_VARS: Final[tuple[str, ...]] = (
    "OPENAI_API_KEY",
    "LINKEDIN_LOGIN_EMAIL",
    "LINKEDIN_PASSWORD",
    "RESUME_PATH",
    "MISTRAL_API_KEY",
)


@dataclass(frozen=True)
class LinkedinCredentials:
    email: str
    password: str
    resume_path: str
    mistral_api_key: str


def load_env() -> LinkedinCredentials:
    """Load required environment variables from the project's .env file."""

    load_dotenv(dotenv_path=".env")

    values: dict[str, str | None] = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LINKEDIN_LOGIN_EMAIL": os.getenv("LINKEDIN_LOGIN_EMAIL"),
        "LINKEDIN_PASSWORD": os.getenv("LINKEDIN_PASSWORD"),
        "RESUME_PATH": os.getenv("RESUME_PATH"),
        "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY"),
    }

    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(sorted(missing))}"
        )

    return LinkedinCredentials(
        email=values["LINKEDIN_LOGIN_EMAIL"],
        password=values["LINKEDIN_PASSWORD"],
        resume_path=values["RESUME_PATH"],
        mistral_api_key=values["MISTRAL_API_KEY"],
    )


