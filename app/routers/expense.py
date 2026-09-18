from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.business_service import get_user_business
from app.services.expense_service import (
    create_expense,
    get_business_expenses,
)


router = APIRouter(
    prefix="/businesses/{business_id}/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_route(
    business_id: int,
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_user_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité introuvable.",
        )

    return create_expense(
        db=db,
        business_id=business.id,
        expense_data=expense_data,
    )


@router.get(
    "/",
    response_model=list[ExpenseResponse],
)
def get_expenses_route(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_user_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité introuvable.",
        )

    return get_business_expenses(
        db=db,
        business_id=business.id,
    )
