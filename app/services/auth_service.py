from __future__ import annotations

import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import User


class AuthService:
    """Service for user authentication and management."""

    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return self.hash_password(password) == hashed_password

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password."""
        user = self.db.scalar(
            select(User).where(User.username == username, User.is_active == True)
        )
        
        if user and self.verify_password(password, user.password):
            return user
        
        return None

    def create_user(
        self,
        username: str,
        password: str,
        full_name: str,
        role: str = "student",
        student_class: Optional[str] = None,
        admission_year: Optional[int] = None,
    ) -> User:
        """Create a new user."""
        
        # Check if username already exists
        existing = self.db.scalar(
            select(User).where(User.username == username)
        )
        if existing:
            raise ValueError("Username already exists")
        
        user = User(
            username=username,
            password=self.hash_password(password),
            full_name=full_name,
            role=role,
            student_class=student_class,
            admission_year=admission_year,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def update_user(
        self,
        user_id: int,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        student_class: Optional[str] = None,
        admission_year: Optional[int] = None,
        is_active: Optional[bool] = None,
        password: Optional[str] = None,
    ) -> User:
        """Update an existing user."""
        
        user = self.db.scalar(select(User).where(User.id == user_id))
        if not user:
            raise ValueError("User not found")
        
        if full_name is not None:
            user.full_name = full_name
        if role is not None:
            user.role = role
        if student_class is not None:
            user.student_class = student_class
        if admission_year is not None:
            user.admission_year = admission_year
        if is_active is not None:
            user.is_active = is_active
        if password is not None:
            user.password = self.hash_password(password)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        
        user = self.db.scalar(select(User).where(User.id == user_id))
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True

    def get_all_users(self) -> list[User]:
        """Get all users."""
        return list(self.db.scalars(select(User).order_by(User.created_at.desc())).all())

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.scalar(select(User).where(User.id == user_id))

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.scalar(select(User).where(User.username == username))
