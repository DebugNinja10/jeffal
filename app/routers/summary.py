from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.summary import BusinessSummaryResponse
from app.services.business_service import get_user_business
from app.services.summary_service import get_business_summary


router = APIRouter(
    prefix="/businesses/{business_id}/summary",
    tags=["Summary"],
)


@router.get(
    "/",
    response_model=BusinessSummaryResponse,
)
def get_summary_route(
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
            status_code=404,
            detail="Activité introuvable.",
        )

    return get_business_summary(
        db=db,
        business_id=business.id,
    )
