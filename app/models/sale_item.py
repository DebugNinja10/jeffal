from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    sale_id: Mapped[int] = mapped_column(
        ForeignKey("sales.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[float] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    # Unité réellement vendue.
    # Exemple : sac, kg, litre, unité.
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unité",
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    subtotal: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    sale = relationship(
        "Sale",
        back_populates="items",
    )

    product = relationship("Product")
