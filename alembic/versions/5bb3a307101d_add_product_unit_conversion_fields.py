"""add product unit conversion fields

Revision ID: 5bb3a307101d
Revises: 69494de3d44e
Create Date: 2026-09-24 23:35:51.785610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5bb3a307101d"
down_revision: Union[str, Sequence[str], None] = "69494de3d44e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "products",
        sa.Column(
            "base_unit",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "package_size",
            sa.Numeric(
                precision=12,
                scale=3,
            ),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "products",
        "package_size",
    )

    op.drop_column(
        "products",
        "base_unit",
    )
