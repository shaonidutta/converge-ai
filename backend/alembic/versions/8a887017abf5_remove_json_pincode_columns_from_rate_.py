"""Remove JSON pincode columns from rate_cards and providers

Revision ID: 8a887017abf5
Revises: fffcde798556
Create Date: 2025-10-06 22:19:15.655231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8a887017abf5'
down_revision: Union[str, None] = 'fffcde798556'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop the old JSON columns now that data has been migrated to relational tables

    Prerequisites:
    1. New pincode tables must exist (pincodes, rate_card_pincodes, provider_pincodes)
    2. Data must be migrated from JSON columns to new tables
    3. Application code must be updated to use new tables

    Run backend/scripts/migrate_pincodes_to_tables.py before this migration
    """
    # Drop available_pincodes JSON column from rate_cards
    op.drop_column('rate_cards', 'available_pincodes')

    # Drop service_pincodes JSON column from providers
    op.drop_column('providers', 'service_pincodes')


def downgrade() -> None:
    """
    Restore JSON columns (for rollback purposes)
    Note: This will NOT restore the data, only the column structure
    """
    # Add back available_pincodes JSON column to rate_cards
    op.add_column('rate_cards',
        sa.Column('available_pincodes', mysql.JSON(), nullable=True)
    )

    # Add back service_pincodes JSON column to providers
    op.add_column('providers',
        sa.Column('service_pincodes', mysql.JSON(), nullable=True)
    )
