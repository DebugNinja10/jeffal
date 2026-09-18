from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    full_name: Mapped[str] = mapped_column(
        String(150)
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        unique=True,
    )

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