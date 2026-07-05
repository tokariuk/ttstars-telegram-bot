"""split balance topups into dedicated table

Revision ID: 015
Revises: 014
Create Date: 2026-05-22 19:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015"
down_revision: Optional[str] = "014"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "balance_topups",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("payment_currency", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payment_payload", sa.Text(), nullable=True),
        sa.Column("provider_invoice_id", sa.BigInteger(), nullable=True),
        sa.Column("provider_reference", sa.String(length=128), nullable=True),
        sa.Column("provider_amount_minor", sa.BigInteger(), nullable=True),
        sa.Column("provider_status", sa.String(length=64), nullable=True),
        sa.Column("checkout_url", sa.Text(), nullable=True),
        sa.Column("checkout_message_id", sa.BigInteger(), nullable=True),
        sa.Column("auto_product_type", sa.String(length=16), nullable=True),
        sa.Column("auto_recipient_username", sa.String(length=32), nullable=True),
        sa.Column("auto_stars_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("auto_premium_months", sa.Integer(), nullable=True),
        sa.Column("auto_recipient_user_id", sa.BigInteger(), nullable=True),
        sa.Column("auto_gift_id", sa.String(length=64), nullable=True),
        sa.Column("auto_gift_message", sa.String(length=128), nullable=True),
        sa.Column("auto_gift_sender_private", sa.Boolean(), nullable=True),
        sa.Column("linked_order_id", sa.BigInteger(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("credited_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.CheckConstraint(
            "amount_cents >= 0",
            name="ck_balance_topups_amount_cents_non_negative",
        ),
        sa.CheckConstraint(
            "auto_stars_count >= 0",
            name="ck_balance_topups_auto_stars_count_non_negative",
        ),
        sa.CheckConstraint(
            "linked_order_id IS NULL OR linked_order_id > 0",
            name="ck_balance_topups_linked_order_id_positive",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["linked_order_id"], ["store_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_balance_topups_user_id_created_at",
        "balance_topups",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_status",
        "balance_topups",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_provider_invoice_id",
        "balance_topups",
        ["payment_provider", "provider_invoice_id"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_provider_payload",
        "balance_topups",
        ["payment_provider", "payment_payload"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_provider_reference",
        "balance_topups",
        ["payment_provider", "provider_reference"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_linked_order_id",
        "balance_topups",
        ["linked_order_id"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_auto_product_type",
        "balance_topups",
        ["auto_product_type"],
        unique=False,
    )
    op.create_index(
        "ix_balance_topups_polling_queue",
        "balance_topups",
        ["status", "created_at"],
        unique=False,
    )

    op.add_column(
        "store_orders",
        sa.Column("funding_topup_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "store_orders",
        sa.Column("funding_provider", sa.String(length=32), nullable=True),
    )
    op.create_foreign_key(
        "fk_store_orders_funding_topup_id_balance_topups",
        "store_orders",
        "balance_topups",
        ["funding_topup_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_store_orders_funding_topup_id",
        "store_orders",
        ["funding_topup_id"],
        unique=False,
    )
    op.create_index(
        "ix_store_orders_funding_provider",
        "store_orders",
        ["funding_provider"],
        unique=False,
    )

    # Backfill historical topups from store_orders to balance_topups preserving existing records.
    op.execute(
        sa.text(
            """
            INSERT INTO balance_topups (
                user_id,
                amount_cents,
                payment_provider,
                payment_currency,
                status,
                payment_payload,
                provider_invoice_id,
                provider_reference,
                provider_amount_minor,
                provider_status,
                checkout_url,
                checkout_message_id,
                auto_product_type,
                auto_recipient_username,
                auto_stars_count,
                auto_premium_months,
                auto_recipient_user_id,
                auto_gift_id,
                auto_gift_message,
                auto_gift_sender_private,
                linked_order_id,
                error_message,
                paid_at,
                credited_at,
                completed_at,
                canceled_at,
                failed_at,
                created_at,
                updated_at
            )
            SELECT
                o.user_id,
                o.amount_cents,
                o.payment_provider,
                o.payment_currency,
                o.status,
                o.payment_payload,
                o.provider_invoice_id,
                o.provider_reference,
                o.provider_amount_minor,
                o.provider_status,
                o.checkout_url,
                o.checkout_message_id,
                NULL,
                NULL,
                0,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                o.id,
                o.fragment_error,
                o.paid_at,
                CASE
                    WHEN o.status = 'completed' THEN COALESCE(o.fulfilled_at, o.paid_at, o.updated_at)
                    ELSE NULL
                END AS credited_at,
                CASE
                    WHEN o.status = 'completed' THEN COALESCE(o.fulfilled_at, o.paid_at, o.updated_at)
                    ELSE NULL
                END AS completed_at,
                o.canceled_at,
                o.failed_at,
                o.created_at,
                o.updated_at
            FROM store_orders o
            WHERE o.product_type = 'topup'
            """
        )
    )

    op.alter_column("balance_topups", "auto_stars_count", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_store_orders_funding_provider", table_name="store_orders")
    op.drop_index("ix_store_orders_funding_topup_id", table_name="store_orders")
    op.drop_constraint(
        "fk_store_orders_funding_topup_id_balance_topups",
        "store_orders",
        type_="foreignkey",
    )
    op.drop_column("store_orders", "funding_provider")
    op.drop_column("store_orders", "funding_topup_id")

    op.drop_index("ix_balance_topups_polling_queue", table_name="balance_topups")
    op.drop_index("ix_balance_topups_auto_product_type", table_name="balance_topups")
    op.drop_index("ix_balance_topups_linked_order_id", table_name="balance_topups")
    op.drop_index("ix_balance_topups_provider_reference", table_name="balance_topups")
    op.drop_index("ix_balance_topups_provider_payload", table_name="balance_topups")
    op.drop_index("ix_balance_topups_provider_invoice_id", table_name="balance_topups")
    op.drop_index("ix_balance_topups_status", table_name="balance_topups")
    op.drop_index("ix_balance_topups_user_id_created_at", table_name="balance_topups")
    op.drop_table("balance_topups")
