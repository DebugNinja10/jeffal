from uuid import uuid4

from app.database.connection import SessionLocal
from app.models.user import User


def test_create_user():
    db = SessionLocal()

    try:
        phone = f"77{uuid4().int % 100000000:08d}"

        user = User(
            full_name="Test JËFAL",
            phone=phone,
            preferred_language="wolof",
            hashed_password="test_hash",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        assert user.id is not None
        assert user.full_name == "Test JËFAL"
        assert user.phone == phone
        assert user.preferred_language == "wolof"

    finally:
        db.close()
