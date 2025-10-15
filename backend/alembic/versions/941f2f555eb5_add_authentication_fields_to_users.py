"""add_authentication_fields_to_users

Revision ID: 941f2f555eb5
Revises: 5ea86f4d316b
Create Date: 2025-10-06 23:45:47.032861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '941f2f555eb5'
down_revision: Union[str, None] = '5ea86f4d316b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add authentication fields to users table
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('mobile_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

    # Make email unique
    op.create_index('idx_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    # Remove authentication fields from users table
    op.drop_index('idx_users_email', table_name='users')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'mobile_verified')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'password_hash')
