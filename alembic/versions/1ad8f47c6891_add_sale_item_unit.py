"""add sale item unit

Revision ID: 1ad8f47c6891
Revises: 5bb3a307101d
Create Date: 2026-09-25 00:03:16.942190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1ad8f47c6891"
down_revision: Union[str, Sequence[str], None] = "5bb3a307101d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "sale_items",
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
            server_default="unité",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "sale_items",
        "unit",
    )
