from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    debt_id: Mapped[int] = mapped_column(
        ForeignKey("debts.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    paid_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    debt = relationship(
        "Debt",
        back_populates="payments",
    )
