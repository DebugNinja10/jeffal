from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.schemas.sale import SaleCreate


def create_sale(
    db: Session,
    business_id: int,
    sale_data: SaleCreate,
) -> Sale:

    # 1. Vérifier que tous les produits appartiennent
    #    à l'activité concernée.
    product_ids = [
        item.product_id
        for item in sale_data.items
    ]

    products = (
        db.query(Product)
        .filter(
            Product.business_id == business_id,
            Product.id.in_(product_ids),
        )
        .all()
    )

    products_by_id = {
        product.id: product
        for product in products
    }

    if len(products_by_id) != len(set(product_ids)):
        raise ValueError(
            "Un ou plusieurs produits "
            "n'appartiennent pas à cette activité."
        )

    # 2. Vérifier les quantités et le stock.
    for item in sale_data.items:
        product = products_by_id[item.product_id]

        if item.quantity > product.stock_quantity:
            raise ValueError(
                f"Stock insuffisant pour "
                f"'{product.name}'. "
                f"Stock disponible : "
                f"{product.stock_quantity}. "
                f"Quantité demandée : "
                f"{item.quantity}."
            )

    # 3. Créer la vente.
    sale = Sale(
        business_id=business_id,
        total_amount=Decimal("0.00"),
        payment_method=sale_data.payment_method,
    )

    db.add(sale)

    # 4. Calculer les lignes et le total.
    total_amount = Decimal("0.00")

    for item in sale_data.items:
        product = products_by_id[item.product_id]

        unit_price = Decimal(
            str(product.selling_price)
        )

        subtotal = unit_price * item.quantity

        sale_item = SaleItem(
            sale=sale,
            product=product,
            quantity=item.quantity,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        db.add(sale_item)

        # 5. Diminuer le stock.
        product.stock_quantity -= item.quantity

        # 6. Ajouter au total.
        total_amount += subtotal

    sale.total_amount = total_amount

    # 7. Une seule transaction PostgreSQL.
    try:
        db.commit()
        db.refresh(sale)

    except Exception:
        db.rollback()
        raise

    return sale
def get_business_sales(
    db: Session,
    business_id: int,
) -> list[Sale]:

    return (
        db.query(Sale)
        .filter(
            Sale.business_id == business_id
        )
        .order_by(
            Sale.sold_at.desc()
        )
        .all()
    )
