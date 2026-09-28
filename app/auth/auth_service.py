from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.core.security import verify_password
from app.core.security import normalize_phone
from app.models.user import User


def authenticate_user(
    db: Session,
    phone: str,
    password: str,
) -> User | None:
    normalized_phone = normalize_phone(phone)
    user = next(
        (candidate for candidate in db.query(User).all()
         if normalize_phone(candidate.phone) == normalized_phone),
        None,
    )

    if user is None:
        return None

    if user.hashed_password is None:
        return None

    if not verify_password(
        password,
        user.hashed_password,
    ):
        return None

    return user


def login_user(
    db: Session,
    phone: str,
    password: str,
) -> str | None:
    user = authenticate_user(
        db=db,
        phone=phone,
        password=password,
    )

    if user is None:
        return None

    return create_access_token(user.id)
