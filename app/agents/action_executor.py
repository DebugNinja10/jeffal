from sqlalchemy.orm import Session

from app.agents.intents import IntentName
from app.agents.schemas import AgentUnderstanding
from app.schemas.debt import DebtCreate, DebtPaymentCreate
from app.schemas.expense import ExpenseCreate
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.debt_service import (
    add_debt_payment,
    create_debt,
    find_business_debt_by_customer_name,
)
from app.services.expense_service import create_expense
from app.services.product_service import find_business_product_by_name
from app.services.sale_service import create_sale


class ActionExecutor:

    def execute(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        if understanding.intent == IntentName.ENREGISTRER_VENTE:
            return self._execute_sale(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        if understanding.intent == IntentName.ENREGISTRER_DEPENSE:
            return self._execute_expense(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        if understanding.intent == IntentName.ENREGISTRER_DETTE:
            return self._execute_debt(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        if understanding.intent == IntentName.ENREGISTRER_REMBOURSEMENT:
            return self._execute_debt_payment(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        if understanding.intent == IntentName.CONSULTER_STOCK:
            return self._execute_stock_query(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        raise ValueError(
            f"Intent non supportée : "
            f"{understanding.intent}"
        )

    def _execute_sale(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        items = understanding.data["items"]

        sale_items = []

        for item in items:
            product = find_business_product_by_name(
                db=db,
                product_name=item["product_name"],
                business_id=business_id,
            )

            if product is None:
                raise ValueError(
                    f"Produit introuvable : "
                    f"'{item['product_name']}'."
                )

            sale_items.append(
    SaleItemCreate(
        product_id=product.id,
        quantity=item["quantity"],
        unit=item.get("unit") or product.unit,
    )
)

        sale_data = SaleCreate(
            payment_method=(
                understanding.data.get("payment_method")
                or "especes"
            ),
            items=sale_items,
        )

        sale = create_sale(
            db=db,
            business_id=business_id,
            sale_data=sale_data,
        )

        return {
            "sale_id": sale.id,
            "business_id": sale.business_id,
            "payment_method": sale.payment_method,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                }
                for item in sale.items
            ],
            "created_at": sale.created_at.isoformat()
            if sale.created_at
            else None,
        }

    def _execute_expense(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        expense_data = ExpenseCreate(
            amount=understanding.data["amount"],
            category=understanding.data["category"],
            description=understanding.data.get("description"),
            payment_method=(
                understanding.data.get("payment_method")
                or "especes"
            ),
        )

        expense = create_expense(
            db=db,
            business_id=business_id,
            expense_data=expense_data,
        )

        return {
            "expense_id": expense.id,
            "business_id": expense.business_id,
            "amount": float(expense.amount),
            "category": expense.category,
            "description": expense.description,
            "payment_method": expense.payment_method,
            "spent_at": expense.spent_at.isoformat()
            if expense.spent_at
            else None,
            "created_at": expense.created_at.isoformat()
            if expense.created_at
            else None,
        }

    def _execute_debt(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        debt_data = DebtCreate(
            customer_name=understanding.data["customer_name"],
            amount=understanding.data["amount"],
            description=understanding.data.get("description"),
        )

        debt = create_debt(
            db=db,
            business_id=business_id,
            debt_data=debt_data,
        )

        return {
            "debt_id": debt.id,
            "business_id": debt.business_id,
            "customer_name": debt.customer_name,
            "amount": float(debt.amount),
            "description": debt.description,
            "created_at": debt.created_at.isoformat()
            if debt.created_at
            else None,
        }

    def _execute_debt_payment(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        customer_name = understanding.data["customer_name"]
        amount = understanding.data["amount"]

        debt = find_business_debt_by_customer_name(
            db=db,
            business_id=business_id,
            customer_name=customer_name,
        )

        if debt is None:
            raise ValueError(
                f"Aucune dette ouverte trouvée "
                f"pour '{customer_name}'."
            )

        payment_data = DebtPaymentCreate(
            amount=amount,
        )

        payment = add_debt_payment(
            db=db,
            debt=debt,
            payment_data=payment_data,
        )

        return {
            "payment_id": payment.id,
            "debt_id": payment.debt_id,
            "amount": float(payment.amount),
            "paid_at": payment.paid_at.isoformat()
            if payment.paid_at
            else None,
        }

    def _execute_stock_query(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        product_name = understanding.data["product_name"]

        product = find_business_product_by_name(
            db=db,
            product_name=product_name,
            business_id=business_id,
        )

        if product is None:
            raise ValueError(
                f"Produit introuvable : "
                f"'{product_name}'."
            )

        return {
            "product_id": product.id,
            "product_name": product.name,
            "stock_quantity": product.stock_quantity,
            "unit": product.unit,
        }
