from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


LOW_STOCK_THRESHOLD = 5


def get_business_summary(
    db: Session,
    business_id: int,
) -> dict:

    sales = (
        db.query(Sale)
        .filter(
            Sale.business_id == business_id
        )
        .all()
    )

    expenses = (
        db.query(Expense)
        .filter(
            Expense.business_id == business_id
        )
        .all()
    )

    products = (
        db.query(Product)
        .filter(
            Product.business_id == business_id
        )
        .all()
    )

    sale_items = (
        db.query(SaleItem)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .filter(
            Sale.business_id == business_id
        )
        .all()
    )

    # 1. Chiffre d'affaires
    total_sales = sum(
        (Decimal(str(sale.total_amount)) for sale in sales),
        Decimal("0.00"),
    )

    # 2. Total des dépenses
    total_expenses = sum(
        (Decimal(str(expense.amount)) for expense in expenses),
        Decimal("0.00"),
    )

    # 3. Flux net
    net_cash_flow = total_sales - total_expenses

    # 4. Nombre de ventes
    sales_count = len(sales)

    # 5. Valeur actuelle du stock au prix d'achat
    stock_value = sum(
        (
            Decimal(str(product.purchase_price))
            * product.stock_quantity
            for product in products
        ),
        Decimal("0.00"),
    )

    # 6. Marge brute sur les produits vendus
    gross_margin = Decimal("0.00")

    products_by_id = {
        product.id: product
        for product in products
    }

    for item in sale_items:
        product = products_by_id.get(item.product_id)

        if product is None:
            continue

        purchase_price = Decimal(
            str(product.purchase_price)
        )

        selling_price = Decimal(
            str(item.unit_price)
        )

        gross_margin += (
            selling_price - purchase_price
        ) * item.quantity

    # 7. Produits avec stock faible
    low_stock_products = [
        product.name
        for product in products
        if product.stock_quantity <= LOW_STOCK_THRESHOLD
    ]

    return {
        "total_sales": float(total_sales),
        "total_expenses": float(total_expenses),
        "net_cash_flow": float(net_cash_flow),
        "sales_count": sales_count,
        "stock_value": float(stock_value),
        "gross_margin": float(gross_margin),
        "low_stock_products": low_stock_products,
    }
