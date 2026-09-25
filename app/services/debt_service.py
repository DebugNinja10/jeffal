from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.schemas.debt import DebtCreate, DebtPaymentCreate


def create_debt(
    db: Session,
    business_id: int,
    debt_data: DebtCreate,
) -> Debt:

    amount = Decimal(str(debt_data.amount))

    debt = Debt(
        business_id=business_id,
        customer_name=debt_data.customer_name,
        initial_amount=amount,
        remaining_amount=amount,
        description=debt_data.description,
        status="pending",
        due_date=debt_data.due_date,
    )

    db.add(debt)

    try:
        db.commit()
        db.refresh(debt)
    except Exception:
        db.rollback()
        raise

    return debt


def get_business_debts(
    db: Session,
    business_id: int,
) -> list[Debt]:

    return (
        db.query(Debt)
        .filter(
            Debt.business_id == business_id
        )
        .order_by(
            Debt.created_at.desc()
        )
        .all()
    )

def find_business_debt_by_customer_name(
    db: Session,
    business_id: int,
    customer_name: str,
) -> Debt | None:

    return (
        db.query(Debt)
        .filter(
            Debt.business_id == business_id,
            Debt.customer_name.ilike(
                customer_name.strip()
            ),
            Debt.remaining_amount > 0,
        )
        .order_by(
            Debt.created_at.desc()
        )
        .first()
    )

def add_debt_payment(
    db: Session,
    debt: Debt,
    payment_data: DebtPaymentCreate,
) -> DebtPayment:

    payment_amount = Decimal(
        str(payment_data.amount)
    )

    remaining_amount = Decimal(
        str(debt.remaining_amount)
    )

    if payment_amount > remaining_amount:
        raise ValueError(
            "Le montant du remboursement dépasse "
            "le montant restant de la dette."
        )

    paid_at = (
        payment_data.paid_at
        if payment_data.paid_at is not None
        else datetime.utcnow()
    )

    payment = DebtPayment(
        debt_id=debt.id,
        amount=payment_amount,
        note=payment_data.note,
        paid_at=paid_at,
    )

    db.add(payment)

    debt.remaining_amount = (
        remaining_amount - payment_amount
    )

    if debt.remaining_amount == Decimal("0.00"):
        debt.status = "paid"
    else:
        debt.status = "partial"

    try:
        db.commit()
        db.refresh(payment)
        db.refresh(debt)
    except Exception:
        db.rollback()
        raise

    return payment
