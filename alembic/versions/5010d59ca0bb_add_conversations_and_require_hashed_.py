"""add conversations

Revision ID: 5010d59ca0bb
Revises: 8a353aba0e5f
Create Date: 2026-09-25 18:53:12.188790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5010d59ca0bb"
down_revision: Union[str, Sequence[str], None] = "8a353aba0e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "business_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "state",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "context",
            sa.JSON(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_conversations_business_id"),
        "conversations",
        ["business_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_conversations_conversation_id"),
        "conversations",
        ["conversation_id"],
        unique=True,
    )

    op.create_index(
        op.f("ix_conversations_user_id"),
        "conversations",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_conversations_user_id"),
        table_name="conversations",
    )

    op.drop_index(
        op.f("ix_conversations_conversation_id"),
        table_name="conversations",
    )

    op.drop_index(
        op.f("ix_conversations_business_id"),
        table_name="conversations",
    )

    op.drop_table("conversations")
