from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    conversation_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="idle",
    )

    context: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = relationship(
        "User",
    )

    business = relationship(
        "Business",
    )
