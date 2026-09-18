from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
)
def create_user_route(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        user = create_user(
            db=db,
            full_name=user_data.full_name,
            phone=user_data.phone,
            preferred_language=user_data.preferred_language,
            password=user_data.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users_route(
    db: Session = Depends(get_db),
):
    return get_users(db)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable.",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user_route(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
):
    try:
        user = update_user(
            db=db,
            user_id=user_id,
            full_name=user_data.full_name,
            phone=user_data.phone,
            preferred_language=user_data.preferred_language,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable.",
        )

    return user


@router.delete(
    "/{user_id}",
)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_user(
        db=db,
        user_id=user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable.",
        )

    return {
        "message": "Utilisateur supprimé avec succès."
    }
