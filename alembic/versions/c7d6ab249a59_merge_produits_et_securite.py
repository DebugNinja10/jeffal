"""merge produits et securite

Revision ID: c7d6ab249a59
Revises: 1504eee98b4c, a1b2c3d4e5f6
Create Date: 2026-09-29 12:52:40.505664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d6ab249a59'
down_revision: Union[str, Sequence[str], None] = ('1504eee98b4c', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
