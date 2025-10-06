"""Add staff and RBAC tables

Revision ID: 5ea86f4d316b
Revises: 8a887017abf5
Create Date: 2025-10-06 22:24:34.958179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5ea86f4d316b'
down_revision: Union[str, None] = '8a887017abf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create staff and RBAC tables
    Separate staff/employees from customers with proper role management
    """

    # 1. Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='unique_role_name')
    )
    op.create_index('idx_role_name', 'roles', ['name'])
    op.create_index('idx_role_level', 'roles', ['level'])
    op.create_index('idx_role_active', 'roles', ['is_active'])

    # 2. Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='unique_permission_name')
    )
    op.create_index('idx_permission_name', 'permissions', ['name'])
    op.create_index('idx_permission_module', 'permissions', ['module'])
    op.create_index('idx_permission_action', 'permissions', ['action'])

    # 3. Create role_permissions junction table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='unique_role_permission')
    )
    op.create_index('idx_rp_role', 'role_permissions', ['role_id'])
    op.create_index('idx_rp_permission', 'role_permissions', ['permission_id'])

    # 4. Create staff table
    op.create_table(
        'staff',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('mobile', sa.String(length=15), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('designation', sa.String(length=100), nullable=True),
        sa.Column('reporting_to', sa.BigInteger(), nullable=True),
        sa.Column('date_of_joining', sa.Date(), nullable=True),
        sa.Column('date_of_leaving', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['reporting_to'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', name='unique_employee_id'),
        sa.UniqueConstraint('email', name='unique_staff_email'),
        sa.UniqueConstraint('mobile', name='unique_staff_mobile')
    )
    op.create_index('idx_staff_employee_id', 'staff', ['employee_id'])
    op.create_index('idx_staff_email', 'staff', ['email'])
    op.create_index('idx_staff_mobile', 'staff', ['mobile'])
    op.create_index('idx_staff_role', 'staff', ['role_id'])
    op.create_index('idx_staff_active', 'staff', ['is_active'])
    op.create_index('idx_staff_reporting', 'staff', ['reporting_to'])

    # 5. Create staff_sessions table
    op.create_table(
        'staff_sessions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('staff_id', sa.BigInteger(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('login_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('logout_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token', name='unique_session_token')
    )
    op.create_index('idx_session_staff', 'staff_sessions', ['staff_id'])
    op.create_index('idx_session_token', 'staff_sessions', ['session_token'])
    op.create_index('idx_session_active', 'staff_sessions', ['is_active'])
    op.create_index('idx_session_expires', 'staff_sessions', ['expires_at'])

    # 6. Create staff_activity_log table
    op.create_table(
        'staff_activity_log',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('staff_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.BigInteger(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_activity_staff', 'staff_activity_log', ['staff_id'])
    op.create_index('idx_activity_action', 'staff_activity_log', ['action'])
    op.create_index('idx_activity_module', 'staff_activity_log', ['module'])
    op.create_index('idx_activity_entity', 'staff_activity_log', ['entity_type', 'entity_id'])
    op.create_index('idx_activity_created', 'staff_activity_log', ['created_at'])

    # 7. Add staff foreign keys to existing tables
    op.add_column('priority_queue', sa.Column('reviewed_by_staff_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_priority_queue_staff', 'priority_queue', 'staff', ['reviewed_by_staff_id'], ['id'], ondelete='SET NULL')

    op.add_column('complaints', sa.Column('assigned_to_staff_id', sa.BigInteger(), nullable=True))
    op.add_column('complaints', sa.Column('resolved_by_staff_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_complaints_assigned_staff', 'complaints', 'staff', ['assigned_to_staff_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_complaints_resolved_staff', 'complaints', 'staff', ['resolved_by_staff_id'], ['id'], ondelete='SET NULL')

    op.add_column('complaint_updates', sa.Column('staff_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_complaint_updates_staff', 'complaint_updates', 'staff', ['staff_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """
    Drop staff and RBAC tables
    """
    # Drop foreign keys from existing tables
    op.drop_constraint('fk_complaint_updates_staff', 'complaint_updates', type_='foreignkey')
    op.drop_column('complaint_updates', 'staff_id')

    op.drop_constraint('fk_complaints_resolved_staff', 'complaints', type_='foreignkey')
    op.drop_constraint('fk_complaints_assigned_staff', 'complaints', type_='foreignkey')
    op.drop_column('complaints', 'resolved_by_staff_id')
    op.drop_column('complaints', 'assigned_to_staff_id')

    op.drop_constraint('fk_priority_queue_staff', 'priority_queue', type_='foreignkey')
    op.drop_column('priority_queue', 'reviewed_by_staff_id')

    # Drop tables in reverse order
    op.drop_table('staff_activity_log')
    op.drop_table('staff_sessions')
    op.drop_table('staff')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
