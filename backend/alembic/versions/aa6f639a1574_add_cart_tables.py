"""add_cart_tables

Revision ID: aa6f639a1574
Revises: 941f2f555eb5
Create Date: 2025-10-07 00:31:18.589745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa6f639a1574'
down_revision: Union[str, None] = '941f2f555eb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create carts table
    op.create_table(
        'carts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_carts_id', 'carts', ['id'])
    op.create_index('ix_carts_user_id', 'carts', ['user_id'])

    # Create cart_items table
    op.create_table(
        'cart_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cart_id', sa.Integer(), nullable=False),
        sa.Column('rate_card_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('total_price', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rate_card_id'], ['rate_cards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cart_items_id', 'cart_items', ['id'])
    op.create_index('ix_cart_items_cart_id', 'cart_items', ['cart_id'])
    op.create_index('ix_cart_items_rate_card_id', 'cart_items', ['rate_card_id'])


def downgrade() -> None:
    # Drop cart_items table
    op.drop_index('ix_cart_items_rate_card_id', 'cart_items')
    op.drop_index('ix_cart_items_cart_id', 'cart_items')
    op.drop_index('ix_cart_items_id', 'cart_items')
    op.drop_table('cart_items')

    # Drop carts table
    op.drop_index('ix_carts_user_id', 'carts')
    op.drop_index('ix_carts_id', 'carts')
    op.drop_table('carts')
