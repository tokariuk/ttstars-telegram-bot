"""stars orders

Revision ID: 002
Revises: 001
Create Date: 2026-03-14 12:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Optional[str] = "001"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "stars_orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("recipient_username", sa.String(length=32), nullable=False),
        sa.Column("stars_count", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("payment_currency", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payment_payload", sa.String(), nullable=True),
        sa.Column("provider_invoice_id", sa.BigInteger(), nullable=True),
        sa.Column("provider_reference", sa.String(length=128), nullable=True),
        sa.Column("provider_amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("provider_status", sa.String(length=64), nullable=True),
        sa.Column("checkout_url", sa.String(), nullable=True),
        sa.Column("checkout_message_id", sa.BigInteger(), nullable=True),
        sa.Column("fragment_tx_hash", sa.String(length=128), nullable=True),
        sa.Column("fragment_error", sa.String(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('UTC', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("timezone('UTC', now())"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stars_orders_user_id_created_at",
        "stars_orders",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stars_orders_status",
        "stars_orders",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_stars_orders_provider_invoice_id",
        "stars_orders",
        ["payment_provider", "provider_invoice_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_stars_orders_provider_invoice_id", table_name="stars_orders")
    op.drop_index("ix_stars_orders_status", table_name="stars_orders")
    op.drop_index("ix_stars_orders_user_id_created_at", table_name="stars_orders")
    op.drop_table("stars_orders")
