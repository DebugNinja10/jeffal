from sqlalchemy.orm import Session

from app.models.product import Product


# Alias de produits utilisés naturellement par les utilisateurs.
# Cette liste pourra être enrichie progressivement.
PRODUCT_ALIASES = {
    "ceeb": "riz",
    "riz": "riz",
    "suukar": "sucre",
    "sucre": "sucre",
    "meew": "lait",
    "lait": "lait",
}


def normalize_product_name(product_name: str) -> str:
    """
    Normalise un nom de produit avant sa recherche.
    """

    name = product_name.strip().lower()

    return PRODUCT_ALIASES.get(name, name)


def create_product(
    db: Session,
    business_id: int,
    name: str,
    category: str | None,
    unit: str,
    base_unit: str | None,
    package_size: float | None,
    purchase_price: float,
    selling_price: float,
    stock_quantity: float,
) -> Product:

    product = Product(
        business_id=business_id,
        name=name,
        category=category,
        unit=unit,
        base_unit=base_unit,
        package_size=package_size,
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


def find_business_product_by_name(
    db: Session,
    product_name: str,
    business_id: int,
) -> Product | None:

    original_name = product_name.strip()

    if not original_name:
        return None

    # ============================================================
    # 1. RECHERCHE EXACTE
    # ============================================================

    product = (
        db.query(Product)
        .filter(
            Product.business_id == business_id,
            Product.name.ilike(original_name),
        )
        .first()
    )

    if product is not None:
        return product

    # ============================================================
    # 2. NORMALISATION / ALIAS
    # ============================================================

    normalized_name = normalize_product_name(
        original_name
    )

    # ============================================================
    # 3. COMPARAISON AVEC LES PRODUITS EXISTANTS
    # ============================================================

    products = (
        db.query(Product)
        .filter(
            Product.business_id == business_id
        )
        .all()
    )

    for product in products:

        product_normalized = normalize_product_name(
            product.name
        )

        # Exemple :
        # utilisateur → "riz"
        # produit     → "Riz 25 kg"
        #
        # normalize("riz")      = "riz"
        # normalize("Riz 25 kg") = "riz 25 kg"

        if (
            product_normalized == normalized_name
            or product_normalized.startswith(
                normalized_name + " "
            )
        ):
            return product

    return None


def update_product(
    db: Session,
    product: Product,
    name: str | None = None,
    category: str | None = None,
    unit: str | None = None,
    base_unit: str | None = None,
    package_size: float | None = None,
    purchase_price: float | None = None,
    selling_price: float | None = None,
    stock_quantity: float | None = None,
) -> Product:

    if name is not None:
        product.name = name

    if category is not None:
        product.category = category

    if unit is not None:
        product.unit = unit

    if base_unit is not None:
        product.base_unit = base_unit

    if package_size is not None:
        product.package_size = package_size

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
