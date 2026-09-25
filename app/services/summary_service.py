from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


LOW_STOCK_THRESHOLD = Decimal("5")


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
        (
            Decimal(str(sale.total_amount))
            for sale in sales
        ),
        Decimal("0.00"),
    )

    # 2. Total des dépenses
    total_expenses = sum(
        (
            Decimal(str(expense.amount))
            for expense in expenses
        ),
        Decimal("0.00"),
    )

    # 3. Flux net
    net_cash_flow = total_sales - total_expenses

    # 4. Nombre de ventes
    sales_count = len(sales)

    # Produits accessibles dans cette activité
    products_by_id = {
        product.id: product
        for product in products
    }

    # 5. Valeur actuelle du stock
    #
    # Le stock est maintenant stocké dans l'unité de base.
    # Exemple :
    #   prix d'achat = 12 000 FCFA / sac
    #   1 sac = 25 kg
    #   stock = 222 kg
    #
    # Donc :
    #   prix d'achat/kg = 12 000 / 25 = 480 FCFA
    #   valeur stock = 222 × 480 = 106 560 FCFA

    stock_value = Decimal("0.00")

    for product in products:
        purchase_price = Decimal(
            str(product.purchase_price)
        )

        stock_quantity = Decimal(
            str(product.stock_quantity)
        )

        if (
            product.base_unit is not None
            and product.package_size is not None
            and Decimal(str(product.package_size)) > 0
        ):
            package_size = Decimal(
                str(product.package_size)
            )

            purchase_price_per_base_unit = (
                purchase_price / package_size
            )

            stock_value += (
                purchase_price_per_base_unit
                * stock_quantity
            )

        else:
            stock_value += (
                purchase_price
                * stock_quantity
            )

    # 6. Marge brute
    #
    # On compare toujours le prix de vente
    # et le prix d'achat dans la même unité.
    #
    # Exemple :
    #   sac : vente 14 000 / achat 12 000
    #   kg  : vente 560 / achat 480

    gross_margin = Decimal("0.00")

    for item in sale_items:
        product = products_by_id.get(item.product_id)

        if product is None:
            continue

        purchase_price = Decimal(
            str(product.purchase_price)
        )

        sold_unit = item.unit.strip().lower()
        product_unit = product.unit.strip().lower()

        # Vente dans l'unité commerciale
        # Exemple : 1 sac
        if sold_unit == product_unit:
            purchase_price_per_sold_unit = purchase_price

        # Vente dans l'unité de base
        # Exemple : 3 kg
        elif (
            product.base_unit is not None
            and sold_unit == product.base_unit.strip().lower()
            and product.package_size is not None
            and Decimal(str(product.package_size)) > 0
        ):
            package_size = Decimal(
                str(product.package_size)
            )

            purchase_price_per_sold_unit = (
                purchase_price / package_size
            )

        else:
            # Sécurité : unité inconnue.
            continue

        selling_price = Decimal(
            str(item.unit_price)
        )

        quantity = Decimal(
            str(item.quantity)
        )

        gross_margin += (
            selling_price
            - purchase_price_per_sold_unit
        ) * quantity

    # 7. Produits avec stock faible
    #
    # Pour un produit avec conversion :
    #   seuil = 1 paquet commercial.
    #
    # Exemple :
    #   1 sac = 25 kg
    #   alerte si stock <= 25 kg
    #
    # Pour un produit sans conversion :
    #   seuil = 5 unités.

    low_stock_products = []

    for product in products:
        stock_quantity = Decimal(
            str(product.stock_quantity)
        )

        if (
            product.base_unit is not None
            and product.package_size is not None
            and Decimal(str(product.package_size)) > 0
        ):
            low_stock_threshold = Decimal(
                str(product.package_size)
            )

        else:
            low_stock_threshold = LOW_STOCK_THRESHOLD

        if stock_quantity <= low_stock_threshold:
            low_stock_products.append(product.name)

    return {
        "total_sales": float(total_sales),
        "total_expenses": float(total_expenses),
        "net_cash_flow": float(net_cash_flow),
        "sales_count": sales_count,
        "stock_value": float(stock_value),
        "gross_margin": float(gross_margin),
        "low_stock_products": low_stock_products,
    }
