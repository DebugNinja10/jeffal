from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

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

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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

    product = relationship(
        "Product",
    )
