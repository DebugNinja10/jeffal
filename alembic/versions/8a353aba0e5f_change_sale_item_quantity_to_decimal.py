"""change sale item quantity to decimal

Revision ID: 8a353aba0e5f
Revises: 85c8f0169316
Create Date: 2026-09-25 00:XX:XX.XXXXXX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a353aba0e5f"
down_revision: Union[str, Sequence[str], None] = "85c8f0169316"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "sale_items",
        "quantity",
        existing_type=sa.INTEGER(),
        type_=sa.Numeric(
            precision=12,
            scale=3,
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "sale_items",
        "quantity",
        existing_type=sa.Numeric(
            precision=12,
            scale=3,
        ),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
