from app.database.connection import SessionLocal
from app.models.user import User


db = SessionLocal()

try:
    user = User(
        full_name="Test JËFAL",
        phone="770000000",
        preferred_language="wolof",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Utilisateur créé avec l'id : {user.id}")

finally:
    db.close()
