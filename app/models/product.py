from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Unité actuellement utilisée par le produit.
    # Exemple : sac, bouteille, carton.
    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Unité de référence pour la gestion fine du stock.
    # Exemple : kg, litre, unité.
    base_unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Quantité de l'unité de base contenue
    # dans une unité principale.
    #
    # Exemple :
    # 1 sac = 25 kg
    # package_size = 25
    package_size: Mapped[float | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    purchase_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    selling_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    stock_quantity: Mapped[float] = mapped_column(
    Numeric(12, 3),
    nullable=False,
    default=0,
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    business = relationship(
        "Business",
        back_populates="products",
    )
