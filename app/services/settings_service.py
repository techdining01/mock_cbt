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
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings

    def update_settings(
        self,
        school_name: Optional[str] = None,
        school_address: Optional[str] = None,
        school_logo_path: Optional[str] = None,
        theme: Optional[str] = None,
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
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
