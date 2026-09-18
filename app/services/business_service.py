from sqlalchemy.orm import Session

from app.models.business import Business


def create_business(
    db: Session,
    user_id: int,
    name: str,
    sector: str,
    location: str | None = None,
) -> Business:

    business = Business(
        user_id=user_id,
        name=name,
        sector=sector,
        location=location,
    )

    db.add(business)
    db.commit()
    db.refresh(business)

    return business


def get_user_businesses(
    db: Session,
    user_id: int,
) -> list[Business]:

    return (
        db.query(Business)
        .filter(Business.user_id == user_id)
        .all()
    )


def get_user_business(
    db: Session,
    business_id: int,
    user_id: int,
) -> Business | None:

    return (
        db.query(Business)
        .filter(
            Business.id == business_id,
            Business.user_id == user_id,
        )
        .first()
    )


def update_business(
    db: Session,
    business: Business,
    name: str | None = None,
    sector: str | None = None,
    location: str | None = None,
) -> Business:

    if name is not None:
        business.name = name

    if sector is not None:
        business.sector = sector

    if location is not None:
        business.location = location

    db.commit()
    db.refresh(business)

    return business


def delete_business(
    db: Session,
    business: Business,
) -> None:

    db.delete(business)
    db.commit()
