from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.core.security import decrypt_phone, encrypt_phone


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150)
    )

    phone_encrypted: Mapped[str] = mapped_column(String(255), nullable=False)

    preferred_language: Mapped[str] = mapped_column(
        String(20),
        default="wolof",
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    businesses = relationship(
        "Business",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def phone(self) -> str:
        return decrypt_phone(self.phone_encrypted)

    @phone.setter
    def phone(self, value: str) -> None:
        self.phone_encrypted = encrypt_phone(value)
