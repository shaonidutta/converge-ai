"""Add pincode optimization tables

Revision ID: fffcde798556
Revises: c69d77625ee9
Create Date: 2025-10-06 21:18:52.643517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'fffcde798556'
down_revision: Union[str, None] = 'c69d77625ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pincodes master table
    op.create_table(
        'pincodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pincode', sa.String(length=6), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('is_serviceable', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pincode', name='unique_pincode')
    )
    op.create_index('idx_pincode', 'pincodes', ['pincode'])
    op.create_index('idx_city', 'pincodes', ['city'])
    op.create_index('idx_state', 'pincodes', ['state'])
    op.create_index('idx_serviceable', 'pincodes', ['is_serviceable'])

    # Create rate_card_pincodes junction table
    op.create_table(
        'rate_card_pincodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rate_card_id', sa.Integer(), nullable=False),
        sa.Column('pincode_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['rate_card_id'], ['rate_cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pincode_id'], ['pincodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rate_card_id', 'pincode_id', name='unique_rate_card_pincode')
    )
    op.create_index('idx_rate_card', 'rate_card_pincodes', ['rate_card_id'])
    op.create_index('idx_pincode_rcp', 'rate_card_pincodes', ['pincode_id'])

    # Create provider_pincodes junction table
    op.create_table(
        'provider_pincodes',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('provider_id', sa.BigInteger(), nullable=False),
        sa.Column('pincode_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['provider_id'], ['providers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pincode_id'], ['pincodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'pincode_id', name='unique_provider_pincode')
    )
    op.create_index('idx_provider', 'provider_pincodes', ['provider_id'])
    op.create_index('idx_pincode_pp', 'provider_pincodes', ['pincode_id'])


def downgrade() -> None:
    # Drop junction tables first (due to foreign keys)
    op.drop_table('provider_pincodes')
    op.drop_table('rate_card_pincodes')
    op.drop_table('pincodes')
