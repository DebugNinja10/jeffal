from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.models.expense import Expense
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


LOW_STOCK_THRESHOLD = Decimal("5")


def get_report_period(period: str) -> tuple[datetime, datetime, str]:
    now = datetime.now()

    if period == "day":
        start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        end = start + timedelta(days=1)
        label = f"Jour du {start.strftime('%d/%m/%Y')}"

    elif period == "week":
        start = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) - timedelta(days=now.weekday())

        end = start + timedelta(days=7)

        label = (
            f"Semaine du {start.strftime('%d/%m/%Y')} "
            f"au {(end - timedelta(days=1)).strftime('%d/%m/%Y')}"
        )

    elif period == "month":
        start = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if start.month == 12:
            end = start.replace(
                year=start.year + 1,
                month=1,
            )
        else:
            end = start.replace(
                month=start.month + 1,
            )

        label = f"Mois de {start.strftime('%m/%Y')}"

    else:
        raise ValueError(
            "Période invalide. Utilisez day, week ou month."
        )

    return start, end, label


def get_business_activity_report(
    db: Session,
    business_id: int,
    period: str,
) -> dict:

    start, end, period_label = get_report_period(period)

    sales = (
        db.query(Sale)
        .filter(
            Sale.business_id == business_id,
            Sale.sold_at >= start,
            Sale.sold_at < end,
        )
        .all()
    )

    expenses = (
        db.query(Expense)
        .filter(
            Expense.business_id == business_id,
            Expense.spent_at >= start,
            Expense.spent_at < end,
        )
        .all()
    )

    debts = (
        db.query(Debt)
        .filter(
            Debt.business_id == business_id,
            Debt.created_at >= start,
            Debt.created_at < end,
        )
        .all()
    )

    debt_payments = (
        db.query(DebtPayment)
        .join(Debt, DebtPayment.debt_id == Debt.id)
        .filter(
            Debt.business_id == business_id,
            DebtPayment.paid_at >= start,
            DebtPayment.paid_at < end,
        )
        .all()
    )

    products = (
        db.query(Product)
        .filter(
            Product.business_id == business_id,
        )
        .all()
    )

    # ---------------------------------------------------------
    # 1. CHIFFRE D'AFFAIRES
    # ---------------------------------------------------------

    total_sales = sum(
        (
            Decimal(str(sale.total_amount))
            for sale in sales
        ),
        Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # 2. DEPENSES
    # ---------------------------------------------------------

    total_expenses = sum(
        (
            Decimal(str(expense.amount))
            for expense in expenses
        ),
        Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # 3. REMBOURSEMENTS DE DETTES
    # ---------------------------------------------------------

    total_debt_payments = sum(
        (
            Decimal(str(payment.amount))
            for payment in debt_payments
        ),
        Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # 4. FLUX NET
    # ---------------------------------------------------------

    net_cash_flow = (
        total_sales
        + total_debt_payments
        - total_expenses
    )

    # ---------------------------------------------------------
    # 5. NOMBRE D'OPERATIONS
    # ---------------------------------------------------------

    sales_count = len(sales)
    expenses_count = len(expenses)
    debts_count = len(debts)
    debt_payments_count = len(debt_payments)

    # ---------------------------------------------------------
    # 6. MARGE BRUTE
    # ---------------------------------------------------------

    sale_items = (
        db.query(SaleItem)
        .join(Sale, SaleItem.sale_id == Sale.id)
        .filter(
            Sale.business_id == business_id,
            Sale.sold_at >= start,
            Sale.sold_at < end,
        )
        .all()
    )

    products_by_id = {
        product.id: product
        for product in products
    }

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

        if sold_unit == product_unit:
            purchase_price_per_sold_unit = purchase_price

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

    # ---------------------------------------------------------
    # 7. STOCK ACTUEL
    # ---------------------------------------------------------

    stock_purchase_value = Decimal("0.00")
    stock_selling_value = Decimal("0.00")
    low_stock_products = []

    for product in products:
        purchase_price = Decimal(
            str(product.purchase_price)
        )

        selling_price = Decimal(
            str(product.selling_price)
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

            stock_packages = (
                stock_quantity / package_size
            )

            stock_purchase_value += (
                stock_packages * purchase_price
            )

            stock_selling_value += (
                stock_packages * selling_price
            )

            low_stock_threshold = package_size

        else:
            stock_purchase_value += (
                stock_quantity * purchase_price
            )

            stock_selling_value += (
                stock_quantity * selling_price
            )

            low_stock_threshold = LOW_STOCK_THRESHOLD

        if stock_quantity <= low_stock_threshold:
            low_stock_products.append(
                product.name
            )

    # ---------------------------------------------------------
    # 8. ENCOURS DE DETTES
    # ---------------------------------------------------------

    all_debts = (
        db.query(Debt)
        .filter(
            Debt.business_id == business_id,
        )
        .all()
    )

    outstanding_debt = sum(
        (
            Decimal(str(debt.remaining_amount))
            for debt in all_debts
        ),
        Decimal("0.00"),
    )

    # ---------------------------------------------------------
    # 9. RESULTAT
    # ---------------------------------------------------------

    return {
        "period": period,
        "period_label": period_label,
        "start": start.isoformat(),
        "end": end.isoformat(),

        "total_sales": float(total_sales),
        "total_expenses": float(total_expenses),
        "total_debt_payments": float(total_debt_payments),

        "net_cash_flow": float(net_cash_flow),

        "sales_count": sales_count,
        "expenses_count": expenses_count,
        "debts_count": debts_count,
        "debt_payments_count": debt_payments_count,

        "gross_margin": float(gross_margin),

        "stock_purchase_value": float(
            stock_purchase_value
        ),
        "stock_selling_value": float(
            stock_selling_value
        ),

        "outstanding_debt": float(
            outstanding_debt
        ),

        "low_stock_products": low_stock_products,
    }
