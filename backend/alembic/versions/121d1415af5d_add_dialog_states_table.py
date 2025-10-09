"""add_dialog_states_table

Revision ID: 121d1415af5d
Revises: 71cbfe8861cb
Create Date: 2025-10-09 13:00:40.894915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '121d1415af5d'
down_revision: Union[str, None] = '71cbfe8861cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create dialog_states table for conversation state management.

    This table enables:
    - Multi-turn conversation tracking
    - Slot-filling workflows
    - Follow-up response handling
    - Context-aware intent classification
    """
    op.create_table(
        'dialog_states',
        # Primary Key
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),

        # Foreign Keys
        sa.Column('user_id', sa.BigInteger(), nullable=False),

        # Session Identifier
        sa.Column('session_id', sa.String(length=100), nullable=False, comment='Unique session identifier from conversations'),

        # State Information
        sa.Column(
            'state',
            sa.Enum('idle', 'collecting_info', 'awaiting_confirmation', 'executing_action', 'completed', 'error', name='dialogstatetype'),
            nullable=False,
            comment='Current conversation state'
        ),

        # Intent
        sa.Column('intent', sa.String(length=50), nullable=True, comment='Current intent being processed'),

        # Entities (JSON)
        sa.Column('collected_entities', mysql.JSON(), nullable=False, comment='Entities extracted and validated so far'),
        sa.Column('needed_entities', mysql.JSON(), nullable=False, comment='List of entity types still required'),

        # Pending Action (JSON)
        sa.Column('pending_action', mysql.JSON(), nullable=True, comment='Action waiting to be executed'),

        # Context (JSON)
        sa.Column('context', mysql.JSON(), nullable=False, comment='Additional context like last question asked'),

        # Expiration
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, comment='State expires after this time'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('session_id', name='uq_dialog_state_session'),
    )

    # Create Indexes
    op.create_index('idx_dialog_state_session', 'dialog_states', ['session_id'])
    op.create_index('idx_dialog_state_user', 'dialog_states', ['user_id'])
    op.create_index('idx_dialog_state_expires', 'dialog_states', ['expires_at'])
    op.create_index('idx_dialog_state_intent', 'dialog_states', ['intent'])
    op.create_index('idx_dialog_state_state', 'dialog_states', ['state'])


def downgrade() -> None:
    """Drop dialog_states table and related indexes"""
    op.drop_index('idx_dialog_state_state', table_name='dialog_states')
    op.drop_index('idx_dialog_state_intent', table_name='dialog_states')
    op.drop_index('idx_dialog_state_expires', table_name='dialog_states')
    op.drop_index('idx_dialog_state_user', table_name='dialog_states')
    op.drop_index('idx_dialog_state_session', table_name='dialog_states')
    op.drop_table('dialog_states')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS dialogstatetype")
