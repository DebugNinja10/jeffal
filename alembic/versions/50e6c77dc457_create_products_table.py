"""create products table

Revision ID: 50e6c77dc457
Revises: c1bcdcd3de9e
Create Date: 2026-09-17 14:57:52.492862

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "50e6c77dc457"
down_revision: Union[str, Sequence[str], None] = "c1bcdcd3de9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "business_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "purchase_price",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "selling_price",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "stock_quantity",
            sa.Integer(),
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
        op.f("ix_products_business_id"),
        "products",
        ["business_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_products_business_id"),
        table_name="products",
    )

    op.drop_table("products")
