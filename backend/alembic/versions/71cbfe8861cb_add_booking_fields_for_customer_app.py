"""add_booking_fields_for_customer_app

Revision ID: 71cbfe8861cb
Revises: aa6f639a1574
Create Date: 2025-10-07 00:47:41.979509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71cbfe8861cb'
down_revision: Union[str, None] = 'aa6f639a1574'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to bookings table
    op.add_column('bookings', sa.Column('booking_number', sa.String(length=50), nullable=True))
    op.add_column('bookings', sa.Column('address_id', sa.BigInteger(), nullable=True))
    op.add_column('bookings', sa.Column('preferred_date', sa.Date(), nullable=True))
    op.add_column('bookings', sa.Column('preferred_time', sa.Time(), nullable=True))
    op.add_column('bookings', sa.Column('special_instructions', sa.Text(), nullable=True))
    op.add_column('bookings', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('bookings', sa.Column('cancelled_at', sa.DateTime(), nullable=True))

    # Add foreign key constraint for address_id
    op.create_foreign_key(
        'fk_bookings_address_id',
        'bookings', 'addresses',
        ['address_id'], ['id'],
        ondelete='RESTRICT'
    )

    # Create index on booking_number
    op.create_index('idx_booking_number', 'bookings', ['booking_number'], unique=True)

    # Create index on address_id
    op.create_index('idx_address', 'bookings', ['address_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_address', table_name='bookings')
    op.drop_index('idx_booking_number', table_name='bookings')

    # Drop foreign key
    op.drop_constraint('fk_bookings_address_id', 'bookings', type_='foreignkey')

    # Drop columns
    op.drop_column('bookings', 'cancelled_at')
    op.drop_column('bookings', 'cancellation_reason')
    op.drop_column('bookings', 'special_instructions')
    op.drop_column('bookings', 'preferred_time')
    op.drop_column('bookings', 'preferred_date')
    op.drop_column('bookings', 'address_id')
    op.drop_column('bookings', 'booking_number')
