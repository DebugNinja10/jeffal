from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale


def get_inventory_period(period: str) -> tuple[datetime, datetime, str]:
    """
    Retourne le début, la fin et le libellé d'une période.

    period:
        - day
        - week
        - month
    """

    now = datetime.now()

    if period == "day":
        start = datetime(
            now.year,
            now.month,
            now.day,
        )
        end = start + timedelta(days=1)
        label = f"Jour du {now.strftime('%d/%m/%Y')}"

    elif period == "week":
        start = datetime(
            now.year,
            now.month,
            now.day,
        ) - timedelta(days=now.weekday())

        end = start + timedelta(days=7)

        label = (
            f"Semaine du {start.strftime('%d/%m/%Y')} "
            f"au {(end - timedelta(days=1)).strftime('%d/%m/%Y')}"
        )

    elif period == "month":
        start = datetime(
            now.year,
            now.month,
            1,
        )

        if now.month == 12:
            end = datetime(
                now.year + 1,
                1,
                1,
            )
        else:
            end = datetime(
                now.year,
                now.month + 1,
                1,
            )

        label = (
            f"Mois de {now.strftime('%m/%Y')}"
        )

    else:
        raise ValueError(
            "Période invalide. "
            "Utilisez day, week ou month."
        )

    return start, end, label


def get_business_inventory(
    db: Session,
    business_id: int,
    period: str = "day",
) -> dict:

    start, end, label = get_inventory_period(
        period
    )

    products = (
        db.query(Product)
        .filter(
            Product.business_id == business_id
        )
        .order_by(Product.name.asc())
        .all()
    )

    sales = (
        db.query(Sale)
        .filter(
            Sale.business_id == business_id,
            Sale.sold_at >= start,
            Sale.sold_at < end,
        )
        .all()
    )

    sold_by_product: dict[int, dict] = {}

    for sale in sales:
        for item in sale.items:

            product_id = item.product_id

            if product_id not in sold_by_product:
                sold_by_product[product_id] = {
                    "quantity": 0.0,
                    "revenue": 0.0,
                }

            sold_by_product[product_id]["quantity"] += (
                float(item.quantity)
            )

            sold_by_product[product_id]["revenue"] += (
                float(item.subtotal)
            )

    items = []

    total_stock_purchase_value = 0.0
    total_stock_selling_value = 0.0
    total_period_revenue = 0.0

    for product in products:

        sold = sold_by_product.get(
            product.id,
            {
                "quantity": 0.0,
                "revenue": 0.0,
            },
        )

        stock_quantity = float(
            product.stock_quantity
        )

        purchase_price = float(
            product.purchase_price
        )

        selling_price = float(
            product.selling_price
        )

        if (
            product.base_unit is not None
            and product.package_size is not None
            and product.package_size > 0
        ):
            stock_packages = (
                stock_quantity
                / float(product.package_size)
            )

            stock_purchase_value = (
                stock_packages * purchase_price
            )

            stock_selling_value = (
                stock_packages * selling_price
            )
        else:
            stock_purchase_value = (
                stock_quantity * purchase_price
            )

            stock_selling_value = (
                stock_quantity * selling_price
            )

        total_stock_purchase_value += (
            stock_purchase_value
        )

        total_stock_selling_value += (
            stock_selling_value
        )

        total_period_revenue += sold["revenue"]

        items.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "category": product.category,
                "stock_quantity": stock_quantity,
                "stock_unit": (
                    product.base_unit
                    or product.unit
                ),
                "quantity_sold": sold["quantity"],
                "revenue": sold["revenue"],
                "purchase_price": purchase_price,
                "selling_price": selling_price,
                "stock_purchase_value": (
                    stock_purchase_value
                ),
                "stock_selling_value": (
                    stock_selling_value
                ),
            }
        )

    return {
        "period": period,
        "period_label": label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "items": items,
        "total_products": len(items),
        "total_period_revenue": total_period_revenue,
        "total_stock_purchase_value": (
            total_stock_purchase_value
        ),
        "total_stock_selling_value": (
            total_stock_selling_value
        ),
    }
