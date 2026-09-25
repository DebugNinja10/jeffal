from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.schemas.sale import SaleCreate
from app.services.unit_service import convert_to_base_unit


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

    # 2. Préparer les lignes de vente et vérifier le stock.
    sale_lines = []

    for item in sale_data.items:
        product = products_by_id[item.product_id]

        sold_unit = item.unit.strip().lower()

        # Si l'unité vendue est l'unité commerciale
        # du produit (ex: sac), on utilise le prix
        # commercial du produit.
        if sold_unit == product.unit.strip().lower():
            unit_price = Decimal(
                str(product.selling_price)
            )

        # Si l'utilisateur vend directement dans
        # l'unité de base (ex: kg), on calcule
        # automatiquement le prix correspondant.
        elif (
            product.base_unit is not None
            and sold_unit == product.base_unit.strip().lower()
        ):
            if (
                product.package_size is None
                or product.package_size <= 0
            ):
                raise ValueError(
                    f"Le produit '{product.name}' "
                    f"n'a pas de package_size valide."
                )

            unit_price = (
                Decimal(str(product.selling_price))
                / Decimal(str(product.package_size))
            )

        else:
            raise ValueError(
                f"Unité '{item.unit}' non compatible "
                f"avec le produit '{product.name}'."
            )

        # Convertir la quantité vendue vers
        # l'unité de base du stock.
        if product.base_unit is None:
            if sold_unit != product.unit.strip().lower():
                raise ValueError(
                    f"Le produit '{product.name}' "
                    f"ne possède pas d'unité de base."
                )

            stock_quantity = float(item.quantity)

        else:
            stock_quantity = convert_to_base_unit(
                quantity=float(item.quantity),
                sold_unit=sold_unit,
                base_unit=product.base_unit,
                package_size=(
                    float(product.package_size)
                    if product.package_size is not None
                    else None
                ),
            )

        if stock_quantity > float(product.stock_quantity):
            raise ValueError(
                f"Stock insuffisant pour "
                f"'{product.name}'. "
                f"Stock disponible : "
                f"{product.stock_quantity} "
                f"{product.base_unit or product.unit}. "
                f"Quantité demandée : "
                f"{stock_quantity} "
                f"{product.base_unit or product.unit}."
            )

        subtotal = (
            unit_price
            * Decimal(str(item.quantity))
        )

        sale_lines.append(
            {
                "item": item,
                "product": product,
                "unit_price": unit_price,
                "stock_quantity": stock_quantity,
                "subtotal": subtotal,
            }
        )

    # 3. Créer la vente.
    sale = Sale(
        business_id=business_id,
        total_amount=Decimal("0.00"),
        payment_method=sale_data.payment_method,
    )

    db.add(sale)

    # 4. Créer les lignes de vente et mettre
    #    à jour le stock.
    total_amount = Decimal("0.00")

    for line in sale_lines:
        item = line["item"]
        product = line["product"]
        unit_price = line["unit_price"]
        stock_quantity = line["stock_quantity"]
        subtotal = line["subtotal"]

        sale_item = SaleItem(
            sale=sale,
            product=product,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=unit_price,
            subtotal=subtotal,
        )

        db.add(sale_item)

        # Le stock est toujours diminué
        # dans l'unité de base.
        product.stock_quantity -= Decimal(
            str(stock_quantity)
        )

        total_amount += subtotal

    # 5. Enregistrer le total.
    sale.total_amount = total_amount

    # 6. Une seule transaction PostgreSQL.
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
