"""supprimer la contrainte unique redondante des refresh tokens

Revision ID: 95db552d753b
Revises: c7d6ab249a59
Create Date: 2026-09-29 13:39:33.680927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95db552d753b'
down_revision: Union[str, Sequence[str], None] = 'c7d6ab249a59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove the redundant unique constraint on token_hash."""
    op.drop_constraint(
        "refresh_tokens_token_hash_key",
        "refresh_tokens",
        type_="unique",
    )


def downgrade() -> None:
    """Restore the unique constraint on token_hash."""
    op.create_unique_constraint(
        "refresh_tokens_token_hash_key",
        "refresh_tokens",
        ["token_hash"],
    )
