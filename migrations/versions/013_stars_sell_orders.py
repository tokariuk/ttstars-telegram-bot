"""stars sell orders

Revision ID: 013
Revises: 012
Create Date: 2026-05-13 02:10:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013"
down_revision: Optional[str] = "012"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "stars_sell_orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("stars_count", sa.Integer(), nullable=False),
        sa.Column("payout_method", sa.String(length=32), nullable=False),
        sa.Column("payout_wallet", sa.String(length=128), nullable=False),
        sa.Column("payout_amount_cents", sa.Integer(), nullable=False),
        sa.Column("invoice_payload", sa.String(length=96), nullable=False),
        sa.Column("invoice_message_id", sa.BigInteger(), nullable=True),
        sa.Column("invoice_total_amount", sa.Integer(), nullable=False),
        sa.Column("telegram_payment_charge_id", sa.String(length=128), nullable=True),
        sa.Column("provider_payment_charge_id", sa.String(length=128), nullable=True),
        sa.Column("paid_stars_amount", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("failure_reason", sa.String(), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payout_available_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
            "stars_count > 0",
            name="ck_stars_sell_orders_stars_count_positive",
        ),
        sa.CheckConstraint(
            "invoice_total_amount > 0",
            name="ck_stars_sell_orders_invoice_total_amount_positive",
        ),
        sa.CheckConstraint(
            "payout_amount_cents >= 0",
            name="ck_stars_sell_orders_payout_amount_non_negative",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_stars_sell_orders_user_id_created_at",
        "stars_sell_orders",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stars_sell_orders_status_created_at",
        "stars_sell_orders",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stars_sell_orders_payout_available_at",
        "stars_sell_orders",
        ["payout_available_at"],
        unique=False,
    )
    op.create_index(
        "ix_stars_sell_orders_invoice_payload",
        "stars_sell_orders",
        ["invoice_payload"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_stars_sell_orders_invoice_payload",
        table_name="stars_sell_orders",
    )
    op.drop_index(
        "ix_stars_sell_orders_payout_available_at",
        table_name="stars_sell_orders",
    )
    op.drop_index(
        "ix_stars_sell_orders_status_created_at",
        table_name="stars_sell_orders",
    )
    op.drop_index(
        "ix_stars_sell_orders_user_id_created_at",
        table_name="stars_sell_orders",
    )
    op.drop_table("stars_sell_orders")
