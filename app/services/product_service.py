from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(
    db: Session,
    business_id: int,
    name: str,
    category: str | None,
    unit: str,
    purchase_price: float,
    selling_price: float,
    stock_quantity: int,
) -> Product:

    product = Product(
        business_id=business_id,
        name=name,
        category=category,
        unit=unit,
        purchase_price=purchase_price,
        selling_price=selling_price,
        stock_quantity=stock_quantity,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_business_products(
    db: Session,
    business_id: int,
) -> list[Product]:

    return (
        db.query(Product)
        .filter(Product.business_id == business_id)
        .all()
    )


def get_business_product(
    db: Session,
    product_id: int,
    business_id: int,
) -> Product | None:

    return (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.business_id == business_id,
        )
        .first()
    )


def update_product(
    db: Session,
    product: Product,
    name: str | None = None,
    category: str | None = None,
    unit: str | None = None,
    purchase_price: float | None = None,
    selling_price: float | None = None,
    stock_quantity: int | None = None,
) -> Product:

    if name is not None:
        product.name = name

    if category is not None:
        product.category = category

    if unit is not None:
        product.unit = unit

    if purchase_price is not None:
        product.purchase_price = purchase_price

    if selling_price is not None:
        product.selling_price = selling_price

    if stock_quantity is not None:
        product.stock_quantity = stock_quantity

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product: Product,
) -> None:

    db.delete(product)
    db.commit()
