from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.business import (
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
)
from app.services.business_service import (
    create_business,
    delete_business,
    get_user_business,
    get_user_businesses,
    update_business,
)


router = APIRouter(
    prefix="/businesses",
    tags=["Businesses"],
)


@router.post(
    "/",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_route(
    business_data: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_business(
        db=db,
        user_id=current_user.id,
        name=business_data.name,
        sector=business_data.sector,
        location=business_data.location,
    )


@router.get(
    "/",
    response_model=list[BusinessResponse],
)
def get_businesses_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_businesses(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
)
def get_business_route(
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

    return business


@router.patch(
    "/{business_id}",
    response_model=BusinessResponse,
)
def update_business_route(
    business_id: int,
    business_data: BusinessUpdate,
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

    return update_business(
        db=db,
        business=business,
        name=business_data.name,
        sector=business_data.sector,
        location=business_data.location,
    )


@router.delete(
    "/{business_id}",
)
def delete_business_route(
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

    delete_business(
        db=db,
        business=business,
    )

    return {
        "message": "Activité supprimée avec succès."
    }
