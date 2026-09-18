from datetime import datetime

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate


def create_expense(
    db: Session,
    business_id: int,
    expense_data: ExpenseCreate,
) -> Expense:

    spent_at = (
        expense_data.spent_at
        if expense_data.spent_at is not None
        else datetime.utcnow()
    )

    expense = Expense(
        business_id=business_id,
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        payment_method=expense_data.payment_method,
        spent_at=spent_at,
    )

    db.add(expense)

    try:
        db.commit()
        db.refresh(expense)
    except Exception:
        db.rollback()
        raise

    return expense


def get_business_expenses(
    db: Session,
    business_id: int,
) -> list[Expense]:

    return (
        db.query(Expense)
        .filter(
            Expense.business_id == business_id
        )
        .order_by(
            Expense.spent_at.desc()
        )
        .all()
    )
