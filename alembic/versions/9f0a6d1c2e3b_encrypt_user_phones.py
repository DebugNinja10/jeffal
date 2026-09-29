"""encrypt user phone numbers"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.security import encrypt_phone

revision: str = "9f0a6d1c2e3b"
down_revision: Union[str, Sequence[str], None] = "5010d59ca0bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_encrypted", sa.String(255), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, phone FROM users")).mappings().all()
    for row in rows:
        bind.execute(
            sa.text("UPDATE users SET phone_encrypted = :encrypted WHERE id = :id"),
            {"encrypted": encrypt_phone(row["phone"]), "id": row["id"]},
        )
    op.alter_column("users", "phone_encrypted", nullable=False)
    op.drop_constraint("users_phone_key", "users", type_="unique")
    op.drop_column("users", "phone")


def downgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(30), nullable=True))
    op.drop_column("users", "phone_encrypted")
