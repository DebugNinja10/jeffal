from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.business_service import get_user_business
from app.services.product_service import (
    create_product,
    delete_product,
    get_business_product,
    get_business_products,
    update_product,
)


router = APIRouter(
    prefix="/businesses/{business_id}/products",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_route(
    business_id: int,
    product_data: ProductCreate,
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

    return create_product(
    db=db,
    business_id=business.id,
    name=product_data.name,
    category=product_data.category,
    unit=product_data.unit,
    base_unit=product_data.base_unit,
    package_size=product_data.package_size,
    purchase_price=product_data.purchase_price,
    selling_price=product_data.selling_price,
    stock_quantity=product_data.stock_quantity,
)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def get_products_route(
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

    return get_business_products(
        db=db,
        business_id=business.id,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_route(
    business_id: int,
    product_id: int,
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

    product = get_business_product(
        db=db,
        product_id=product_id,
        business_id=business.id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )

    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product_route(
    business_id: int,
    product_id: int,
    product_data: ProductUpdate,
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

    product = get_business_product(
        db=db,
        product_id=product_id,
        business_id=business.id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )

    return update_product(
        db=db,
        product=product,
        name=product_data.name,
        category=product_data.category,
        unit=product_data.unit,
        base_unit=product_data.base_unit,
        package_size=product_data.package_size,
        purchase_price=product_data.purchase_price,
        selling_price=product_data.selling_price,
        stock_quantity=product_data.stock_quantity,
    )


@router.delete(
    "/{product_id}",
)
def delete_product_route(
    business_id: int,
    product_id: int,
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

    product = get_business_product(
        db=db,
        product_id=product_id,
        business_id=business.id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produit introuvable.",
        )

    delete_product(
        db=db,
        product=product,
    )

    return {
        "message": "Produit supprimé avec succès."
    }
