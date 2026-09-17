from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import AppSettings


class SettingsService:
    """Service for managing application-wide settings."""

    def __init__(self, db: Session):
        self.db = db

    def get_settings(self) -> AppSettings:
        """Get or create default app settings."""
        settings = self.db.scalar(select(AppSettings).limit(1))

        if not settings:
            # Create default settings
            settings = AppSettings(
                school_name="CBT Examination",
                school_address=None,
                school_logo_path=None,
                theme="light",
                gemini_api_key=None,
                ollama_base_url=None,
                ollama_model=None,
                ai_provider_preference="ollama-only",
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        # Migrate legacy rows: ensure AI-related columns exist on the object.
        # Defensive: older databases may have rows inserted before the new columns.
        mutated = False
        if getattr(settings, "ai_provider_preference", None) is None:
            settings.ai_provider_preference = "ollama-only"
            mutated = True
        # Upgrade legacy preferences (local-first / cloud-first) to ollama-only
        # so the desktop app works with no API keys and Ollama is always primary.
        current_pref = getattr(settings, "ai_provider_preference", None)
        if current_pref in ("local-first", "cloud-first", ""):
            settings.ai_provider_preference = "ollama-only"
            mutated = True
        if mutated:
            try:
                self.db.commit()
                self.db.refresh(settings)
            except Exception:
                self.db.rollback()

        return settings

    def update_settings(
        self,
        school_name: Optional[str] = None,
        school_address: Optional[str] = None,
        school_logo_path: Optional[str] = None,
        theme: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        ai_provider_preference: Optional[str] = None,
    ) -> AppSettings:
        """Update app settings."""
        settings = self.get_settings()

        if school_name is not None:
            settings.school_name = school_name
        if school_address is not None:
            settings.school_address = school_address
        if school_logo_path is not None:
            settings.school_logo_path = school_logo_path
        if theme is not None:
            settings.theme = theme
        if gemini_api_key is not None:
            settings.gemini_api_key = gemini_api_key.strip() or None
        if ollama_base_url is not None:
            settings.ollama_base_url = ollama_base_url.strip().rstrip("/") or None
        if ollama_model is not None:
            settings.ollama_model = ollama_model.strip() or None
        if ai_provider_preference is not None:
            pref = (ai_provider_preference or "").strip().lower()
            if pref in (
                "local-first",
                "cloud-first",
                "gemini-only",
                "ollama-only",
            ):
                settings.ai_provider_preference = pref

        self.db.commit()
        self.db.refresh(settings)

        return settings

    def get_ai_settings(self) -> dict:
        """Get AI-specific settings as a plain dict for easy consumption."""
        settings = self.get_settings()
        return {
            "gemini_api_key": settings.gemini_api_key,
            "ollama_base_url": settings.ollama_base_url,
            "ollama_model": settings.ollama_model,
            "ai_provider_preference": settings.ai_provider_preference,
        }
