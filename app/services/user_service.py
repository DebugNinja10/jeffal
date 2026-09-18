from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


def create_user(
    db: Session,
    full_name: str,
    phone: str,
    preferred_language: str,
    password: str,
) -> User:
    hashed_password = hash_password(password)

    user = User(
        full_name=full_name,
        phone=phone,
        preferred_language=preferred_language,
        hashed_password=hashed_password,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Ce numéro de téléphone est déjà utilisé."
        )

    return user


def get_users(db: Session) -> list[User]:
    return db.query(User).all()


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user(
    db: Session,
    user_id: int,
    full_name: str | None = None,
    phone: str | None = None,
    preferred_language: str | None = None,
) -> User | None:
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        return None

    if full_name is not None:
        user.full_name = full_name

    if phone is not None:
        user.phone = phone

    if preferred_language is not None:
        user.preferred_language = preferred_language

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Ce numéro de téléphone est déjà utilisé."
        )

    return user


def delete_user(
    db: Session,
    user_id: int,
) -> bool:
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True
