from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Debt(Base):
    __tablename__ = "debts"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

    customer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    initial_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    remaining_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    business = relationship(
        "Business",
        back_populates="debts",
    )

    payments = relationship(
        "DebtPayment",
        back_populates="debt",
        cascade="all, delete-orphan",
    )
