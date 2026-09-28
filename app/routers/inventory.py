from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.services.business_service import get_user_business
from app.services.inventory_service import get_business_inventory


router = APIRouter(
    prefix="/businesses/{business_id}/inventory",
    tags=["Inventory"],
)


@router.get(
    "/{period}",
)
def get_inventory_route(
    business_id: int,
    period: str,
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

    if period not in {"day", "week", "month"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Période invalide. Utilisez day, week ou month.",
        )

    return get_business_inventory(
        db=db,
        business_id=business.id,
        period=period,
    )


@router.get(
    "/{period}/pdf",
)
def get_inventory_pdf_route(
    business_id: int,
    period: str,
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

    if period not in {"day", "week", "month"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Période invalide. Utilisez day, week ou month.",
        )

    inventory = get_business_inventory(
        db=db,
        business_id=business.id,
        period=period,
    )

    from fastapi.responses import Response
    from app.services.inventory_pdf_service import (
        generate_inventory_pdf,
    )

    pdf = generate_inventory_pdf(
        inventory=inventory,
        business=business,
    )

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="inventaire-{period}.pdf"'
            )
        },
    )
