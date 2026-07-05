"""store orders gifts

Revision ID: 011
Revises: 010
Create Date: 2026-05-05 02:15:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011"
down_revision: Optional[str] = "010"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "store_orders",
        sa.Column("recipient_user_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "store_orders",
        sa.Column("gift_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "store_orders",
        sa.Column("gift_message", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "store_orders",
        sa.Column("gift_sender_private", sa.Boolean(), nullable=True),
    )

    op.drop_constraint(
        "ck_store_orders_product_payload_consistency",
        "store_orders",
        type_="check",
    )
    op.create_check_constraint(
        "ck_store_orders_product_payload_consistency",
        "store_orders",
        "("
        "("
        "product_type = 'stars' AND stars_count > 0 AND premium_months IS NULL "
        "AND recipient_user_id IS NULL AND gift_id IS NULL AND gift_message IS NULL "
        "AND gift_sender_private IS NULL"
        ") "
        "OR "
        "("
        "product_type = 'premium' AND stars_count = 0 "
        "AND premium_months IS NOT NULL AND premium_months > 0 "
        "AND recipient_user_id IS NULL AND gift_id IS NULL AND gift_message IS NULL "
        "AND gift_sender_private IS NULL"
        ") "
        "OR "
        "("
        "product_type = 'gift' AND stars_count = 0 AND premium_months IS NULL "
        "AND recipient_user_id IS NOT NULL AND gift_id IS NOT NULL "
        "AND gift_sender_private IS NOT NULL"
        ") "
        "OR "
        "("
        "product_type = 'topup' AND stars_count = 0 AND premium_months IS NULL "
        "AND recipient_user_id IS NULL AND gift_id IS NULL AND gift_message IS NULL "
        "AND gift_sender_private IS NULL"
        ")"
        ")",
    )
    op.create_check_constraint(
        "ck_store_orders_recipient_user_id_positive",
        "store_orders",
        "recipient_user_id IS NULL OR recipient_user_id > 0",
    )

    op.create_index(
        "ix_store_orders_recipient_user_id",
        "store_orders",
        ["recipient_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_store_orders_gift_id",
        "store_orders",
        ["gift_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_store_orders_gift_id", table_name="store_orders")
    op.drop_index("ix_store_orders_recipient_user_id", table_name="store_orders")

    op.drop_constraint(
        "ck_store_orders_recipient_user_id_positive",
        "store_orders",
        type_="check",
    )
    op.drop_constraint(
        "ck_store_orders_product_payload_consistency",
        "store_orders",
        type_="check",
    )
    op.create_check_constraint(
        "ck_store_orders_product_payload_consistency",
        "store_orders",
        "("
        "(product_type = 'stars' AND stars_count > 0 AND premium_months IS NULL) "
        "OR "
        "("
        "product_type = 'premium' AND stars_count = 0 "
        "AND premium_months IS NOT NULL AND premium_months > 0"
        ") "
        "OR "
        "(product_type = 'topup' AND stars_count = 0 AND premium_months IS NULL)"
        ")",
    )

    op.drop_column("store_orders", "gift_sender_private")
    op.drop_column("store_orders", "gift_message")
    op.drop_column("store_orders", "gift_id")
    op.drop_column("store_orders", "recipient_user_id")

