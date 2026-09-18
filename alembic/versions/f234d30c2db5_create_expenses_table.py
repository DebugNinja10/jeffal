"""create expenses table

Revision ID: f234d30c2db5
Revises: 2e0fa5d75496
Create Date: 2026-09-17 20:28:21.164810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f234d30c2db5"
down_revision: Union[str, Sequence[str], None] = "2e0fa5d75496"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "payment_method",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "spent_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_expenses_business_id"),
        "expenses",
        ["business_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_expenses_business_id"),
        table_name="expenses",
    )

    op.drop_table("expenses")

