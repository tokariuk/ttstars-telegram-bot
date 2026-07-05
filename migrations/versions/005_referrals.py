"""referrals

Revision ID: 005
Revises: 004
Create Date: 2026-04-04 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Optional[str] = "004"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "referral_balance_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "referral_earned_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("referrer_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_referrer_id_users",
        "users",
        "users",
        ["referrer_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_users_referrer_id",
        "users",
        ["referrer_id"],
        unique=False,
    )
    op.alter_column("users", "referral_balance_cents", server_default=None)
    op.alter_column("users", "referral_earned_cents", server_default=None)

    op.add_column(
        "stars_orders",
        sa.Column(
            "referral_reward_total_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "stars_orders",
        sa.Column(
            "referral_reward_level1_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "stars_orders",
        sa.Column(
            "referral_reward_level2_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "stars_orders",
        sa.Column(
            "referral_reward_level3_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "stars_orders",
        sa.Column("referral_processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_stars_orders_referral_processed_at",
        "stars_orders",
        ["referral_processed_at"],
        unique=False,
    )
    op.alter_column("stars_orders", "referral_reward_total_cents", server_default=None)
    op.alter_column("stars_orders", "referral_reward_level1_cents", server_default=None)
    op.alter_column("stars_orders", "referral_reward_level2_cents", server_default=None)
    op.alter_column("stars_orders", "referral_reward_level3_cents", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_stars_orders_referral_processed_at", table_name="stars_orders")
    op.drop_column("stars_orders", "referral_processed_at")
    op.drop_column("stars_orders", "referral_reward_level3_cents")
    op.drop_column("stars_orders", "referral_reward_level2_cents")
    op.drop_column("stars_orders", "referral_reward_level1_cents")
    op.drop_column("stars_orders", "referral_reward_total_cents")

    op.drop_index("ix_users_referrer_id", table_name="users")
    op.drop_constraint("fk_users_referrer_id_users", "users", type_="foreignkey")
    op.drop_column("users", "referrer_id")
    op.drop_column("users", "referral_earned_cents")
    op.drop_column("users", "referral_balance_cents")
