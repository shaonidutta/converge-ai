"""add_provider_id_to_rate_cards

Revision ID: c3e31b948762
Revises: 5ea86f4d316b
Create Date: 2025-10-09 23:38:38.456934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3e31b948762'
down_revision: Union[str, None] = '5ea86f4d316b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add provider_id column to rate_cards table and assign existing rate cards
    to random providers (first 30 active providers)
    """
    # Step 1: Add provider_id column as nullable first (BIGINT to match providers.id)
    op.add_column('rate_cards', sa.Column('provider_id', sa.BigInteger(), nullable=True))

    # Step 2: Assign provider IDs to existing rate cards
    # Get connection to execute raw SQL
    connection = op.get_bind()

    # Get first 30 active provider IDs
    result = connection.execute(sa.text("""
        SELECT id FROM providers
        WHERE is_active = 1
        ORDER BY id
        LIMIT 30
    """))
    provider_ids = [row[0] for row in result.fetchall()]

    if provider_ids:
        # Get all rate card IDs
        result = connection.execute(sa.text("SELECT id FROM rate_cards ORDER BY id"))
        rate_card_ids = [row[0] for row in result.fetchall()]

        # Randomly assign providers to rate cards (round-robin distribution)
        import random
        random.shuffle(provider_ids)  # Shuffle for randomness

        for idx, rate_card_id in enumerate(rate_card_ids):
            # Use modulo to cycle through providers
            provider_id = provider_ids[idx % len(provider_ids)]
            connection.execute(
                sa.text("UPDATE rate_cards SET provider_id = :provider_id WHERE id = :rate_card_id"),
                {"provider_id": provider_id, "rate_card_id": rate_card_id}
            )

    # Step 3: Make provider_id NOT NULL (MySQL requires existing_type)
    op.alter_column('rate_cards', 'provider_id',
                    existing_type=sa.BigInteger(),
                    nullable=False)

    # Step 4: Add foreign key constraint
    op.create_foreign_key(
        'fk_rate_cards_provider_id',
        'rate_cards', 'providers',
        ['provider_id'], ['id'],
        ondelete='RESTRICT'
    )

    # Step 5: Add indexes
    op.create_index('idx_rate_cards_provider', 'rate_cards', ['provider_id'])
    op.create_index('idx_provider_category', 'rate_cards', ['provider_id', 'category_id', 'subcategory_id', 'is_active'])


def downgrade() -> None:
    """
    Remove provider_id column from rate_cards table
    """
    # Drop indexes first
    op.drop_index('idx_provider_category', 'rate_cards')
    op.drop_index('idx_rate_cards_provider', 'rate_cards')

    # Drop foreign key constraint
    op.drop_constraint('fk_rate_cards_provider_id', 'rate_cards', type_='foreignkey')

    # Drop column
    op.drop_column('rate_cards', 'provider_id')
