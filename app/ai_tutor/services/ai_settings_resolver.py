from __future__ import annotations

import os
from typing import Any


_ENV_DEFAULTS: dict[str, str] = {
    "OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    "OLLAMA_MODEL": "qwen2.5:0.5b-instruct",
    "OLLAMA_TIMEOUT": "90",
    "GEMINI_MODEL": "gemini-3.6-flash",
    "GEMINI_TIMEOUT": "45",
    "AI_PROVIDER_PREFERENCE": "ollama-only",  # Always default to Ollama first
}


def resolve_env_from_db_settings(db_settings: dict[str, Any]) -> None:
    """Merge database AI settings into the current process environment.

    Environment variables that are already explicitly set (e.g. from .env)
    win over database values — this allows admins to lock values via .env
    while still letting users optionally override via the settings UI when
    no env value is present.
    """
    mapping: list[tuple[str, str]] = [
        ("gemini_api_key", "GEMINI_API_KEY"),
        ("ollama_base_url", "OLLAMA_BASE_URL"),
        ("ollama_model", "OLLAMA_MODEL"),
        ("ai_provider_preference", "AI_PROVIDER_PREFERENCE"),
    ]

    for db_key, env_key in mapping:
        db_value = db_settings.get(db_key)
        if db_value is None:
            continue
        db_str = str(db_value).strip()
        if not db_str:
            continue
        existing = os.environ.get(env_key) or os.getenv(env_key)
        if existing and existing.strip():
            # Environment already has a value; don't clobber it.
            continue
        os.environ[env_key] = db_str


def get_preference() -> str:
    value = (os.getenv("AI_PROVIDER_PREFERENCE") or "").strip().lower()
    if value in ("local-first", "cloud-first", "gemini-only", "ollama-only"):
        return value
    return _ENV_DEFAULTS["AI_PROVIDER_PREFERENCE"]
