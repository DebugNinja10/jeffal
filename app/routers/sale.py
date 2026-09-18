from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.business_service import get_user_business
from app.services.sale_service import (
    create_sale,
    get_business_sales,
)

router = APIRouter(
    prefix="/businesses/{business_id}/sales",
    tags=["Sales"],
)


@router.post(
    "/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale_route(
    business_id: int,
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que l'activité appartient
    # bien à l'utilisateur connecté.
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

    try:
        sale = create_sale(
            db=db,
            business_id=business.id,
            sale_data=sale_data,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return sale
@router.get(
    "/",
    response_model=list[SaleResponse],
)
def get_sales_route(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que l'activité appartient
    # bien à l'utilisateur connecté.
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

    return get_business_sales(
        db=db,
        business_id=business.id,
    )
