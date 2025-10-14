"""add_description_to_rate_cards

Revision ID: 1faf3a73edb3
Revises: c3e31b948762
Create Date: 2025-10-14 18:53:16.681154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1faf3a73edb3'
down_revision: Union[str, None] = 'c3e31b948762'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add description column to rate_cards table.
    This column will help customers understand what makes each rate card special.
    """
    # Add description column (TEXT type for longer descriptions)
    op.add_column('rate_cards', sa.Column('description', sa.Text(), nullable=True))

    # Note: Descriptions will be populated by a separate script after migration


def downgrade() -> None:
    """
    Remove description column from rate_cards table
    """
    op.drop_column('rate_cards', 'description')
