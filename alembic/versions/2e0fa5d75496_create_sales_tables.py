"""create sales tables

Revision ID: 2e0fa5d75496
Revises: 50e6c77dc457
Create Date: 2026-09-17 16:07:48.019865

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2e0fa5d75496"
down_revision: Union[str, Sequence[str], None] = "50e6c77dc457"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create sales and sale_items tables."""

    op.create_table(
        "sales",
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
            "total_amount",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            sa.String(30),
            nullable=False,
        ),
        sa.Column(
            "sold_at",
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
        op.f("ix_sales_business_id"),
        "sales",
        ["business_id"],
        unique=False,
    )

    op.create_table(
        "sale_items",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "sale_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sale_id"],
            ["sales.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_sale_items_product_id"),
        "sale_items",
        ["product_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_sale_items_sale_id"),
        "sale_items",
        ["sale_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop sales and sale_items tables."""

    op.drop_index(
        op.f("ix_sale_items_sale_id"),
        table_name="sale_items",
    )

    op.drop_index(
        op.f("ix_sale_items_product_id"),
        table_name="sale_items",
    )

    op.drop_table("sale_items")

    op.drop_index(
        op.f("ix_sales_business_id"),
        table_name="sales",
    )

    op.drop_table("sales")