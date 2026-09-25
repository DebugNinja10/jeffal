"""change stock quantity to decimal

Revision ID: 85c8f0169316
Revises: 1ad8f47c6891
Create Date: 2026-09-25 00:11:17.271258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "85c8f0169316"
down_revision: Union[str, Sequence[str], None] = "1ad8f47c6891"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "products",
        "stock_quantity",
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
        "products",
        "stock_quantity",
        existing_type=sa.Numeric(
            precision=12,
            scale=3,
        ),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
