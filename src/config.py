from __future__ import annotations

"""Configuration helpers for the LinkedIn job application agent."""

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
    "CANDIDATE_FULL_NAME",
    "CANDIDATE_EMAIL",
    "CANDIDATE_PHONE",
    "CANDIDATE_REQUIRES_SPONSORSHIP",
    "CANDIDATE_WILLING_TO_RELOCATE",
    "CANDIDATE_DESIRED_COMPENSATION",
    "CANDIDATE_DEFAULT_YEARS_EXPERIENCE",
)


@dataclass(frozen=True)
class LinkedinCredentials:
    email: str
    password: str
    resume_path: str
    mistral_api_key: str


@dataclass(frozen=True)
class CandidateProfile:
    full_name: str
    email: str
    phone: str
    requires_sponsorship: bool
    willing_to_relocate: bool
    desired_compensation: str
    default_years_experience: str


@dataclass(frozen=True)
class AppConfig:
    credentials: LinkedinCredentials
    candidate: CandidateProfile


def _env_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_env() -> AppConfig:
    """Load required environment variables from the project's .env file."""

    load_dotenv(dotenv_path=".env")

    env_values: dict[str, str | None] = {name: os.getenv(name) for name in REQUIRED_ENV_VARS}

    missing = [name for name, value in env_values.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(sorted(missing))}"
        )

    credentials = LinkedinCredentials(
        email=env_values["LINKEDIN_LOGIN_EMAIL"],
        password=env_values["LINKEDIN_PASSWORD"],
        resume_path=env_values["RESUME_PATH"],
        mistral_api_key=env_values["MISTRAL_API_KEY"],
    )

    candidate = CandidateProfile(
        full_name=env_values["CANDIDATE_FULL_NAME"],
        email=env_values["CANDIDATE_EMAIL"],
        phone=env_values["CANDIDATE_PHONE"],
        requires_sponsorship=_env_bool(env_values["CANDIDATE_REQUIRES_SPONSORSHIP"]),
        willing_to_relocate=_env_bool(env_values["CANDIDATE_WILLING_TO_RELOCATE"]),
        desired_compensation=env_values["CANDIDATE_DESIRED_COMPENSATION"],
        default_years_experience=env_values["CANDIDATE_DEFAULT_YEARS_EXPERIENCE"],
    )

    return AppConfig(credentials=credentials, candidate=candidate)


