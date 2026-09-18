from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.debt import (
    DebtCreate,
    DebtPaymentCreate,
    DebtPaymentResponse,
    DebtResponse,
)
from app.services.business_service import get_user_business
from app.services.debt_service import (
    add_debt_payment,
    create_debt,
    get_business_debts,
)


router = APIRouter(
    prefix="/businesses/{business_id}/debts",
    tags=["Debts"],
)


@router.post(
    "/",
    response_model=DebtResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_debt_route(
    business_id: int,
    debt_data: DebtCreate,
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

    return create_debt(
        db=db,
        business_id=business.id,
        debt_data=debt_data,
    )


@router.get(
    "/",
    response_model=list[DebtResponse],
)
def get_debts_route(
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

    return get_business_debts(
        db=db,
        business_id=business.id,
    )


@router.post(
    "/{debt_id}/payments/",
    response_model=DebtPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_payment_route(
    business_id: int,
    debt_id: int,
    payment_data: DebtPaymentCreate,
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

    from app.models.debt import Debt

    debt = (
        db.query(Debt)
        .filter(
            Debt.id == debt_id,
            Debt.business_id == business.id,
        )
        .first()
    )

    if debt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dette introuvable.",
        )

    try:
        return add_debt_payment(
            db=db,
            debt=debt,
            payment_data=payment_data,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
