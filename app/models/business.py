from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sector: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="businesses",
    )

    products = relationship(
        "Product",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    sales = relationship(
        "Sale",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    expenses = relationship(
        "Expense",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    debts = relationship(
        "Debt",
        back_populates="business",
        cascade="all, delete-orphan",
    )
