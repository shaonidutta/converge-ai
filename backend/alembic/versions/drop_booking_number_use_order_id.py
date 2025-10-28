"""drop_booking_number_column_use_order_id_only

Revision ID: f9e8d7c6b5a4
Revises: 121d1415af5d
Create Date: 2025-10-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9e8d7c6b5a4'
down_revision: Union[str, None] = '121d1415af5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop booking_number column from bookings table.
    From now on, we will use order_id as the primary customer-facing identifier.

    Prerequisites:
    1. Ensure all code has been updated to use order_id instead of booking_number
    2. Ensure all API responses use order_id
    3. Ensure all frontend code uses order_id
    """
    # Drop the unique index on booking_number
    op.drop_index('idx_booking_number', table_name='bookings')

    # Drop the booking_number column
    op.drop_column('bookings', 'booking_number')

    # Create unique index on order_id for faster lookups
    op.create_index('idx_order_id', 'bookings', ['order_id'], unique=True)


def downgrade() -> None:
    """
    Restore booking_number column (for rollback purposes).
    Note: This will NOT restore the data, only the column structure.
    """
    # Drop the order_id index
    op.drop_index('idx_order_id', table_name='bookings')

    # Add back booking_number column
    op.add_column('bookings', sa.Column('booking_number', sa.String(length=50), nullable=True))

    # Recreate the unique index
    op.create_index('idx_booking_number', 'bookings', ['booking_number'], unique=True)

