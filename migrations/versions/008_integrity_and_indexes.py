"""integrity and indexes

Revision ID: 008
Revises: 007
Create Date: 2026-04-20 00:00:00.000000

"""

from typing import Optional, Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "008"
down_revision: Optional[str] = "007"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_users_balance_cents_non_negative",
        "users",
        "balance_cents >= 0",
    )
    op.create_check_constraint(
        "ck_users_referral_balance_cents_non_negative",
        "users",
        "referral_balance_cents >= 0",
    )
    op.create_check_constraint(
        "ck_users_referral_earned_cents_non_negative",
        "users",
        "referral_earned_cents >= 0",
    )
    op.create_check_constraint(
        "ck_users_referrer_not_self",
        "users",
        "referrer_id IS NULL OR referrer_id <> id",
    )

    op.create_check_constraint(
        "ck_stars_orders_amount_cents_non_negative",
        "stars_orders",
        "amount_cents >= 0",
    )
    op.create_check_constraint(
        "ck_stars_orders_stars_count_non_negative",
        "stars_orders",
        "stars_count >= 0",
    )
    op.create_check_constraint(
        "ck_stars_orders_product_payload_consistency",
        "stars_orders",
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

    op.create_check_constraint(
        "ck_user_checks_amount_cents_positive",
        "user_checks",
        "amount_cents > 0",
    )
    op.create_check_constraint(
        "ck_user_checks_stars_count_non_negative",
        "user_checks",
        "stars_count >= 0",
    )
    op.create_check_constraint(
        "ck_user_checks_product_payload_consistency",
        "user_checks",
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

    op.create_index(
        "ix_stars_orders_polling_queue",
        "stars_orders",
        ["status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_stars_orders_provider_payload",
        "stars_orders",
        ["payment_provider", "payment_payload"],
        unique=False,
    )
    op.create_index(
        "ix_stars_orders_provider_reference",
        "stars_orders",
        ["payment_provider", "provider_reference"],
        unique=False,
    )
    op.create_index(
        "ix_stars_orders_user_status_created_at",
        "stars_orders",
        ["user_id", "status", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_user_checks_inline_message_id",
        "user_checks",
        ["inline_message_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_checks_creator_status_updated_at",
        "user_checks",
        ["creator_id", "status", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_checks_creator_status_updated_at", table_name="user_checks")
    op.drop_index("ix_user_checks_inline_message_id", table_name="user_checks")
    op.drop_index("ix_stars_orders_user_status_created_at", table_name="stars_orders")
    op.drop_index("ix_stars_orders_provider_reference", table_name="stars_orders")
    op.drop_index("ix_stars_orders_provider_payload", table_name="stars_orders")
    op.drop_index("ix_stars_orders_polling_queue", table_name="stars_orders")

    op.drop_constraint("ck_user_checks_product_payload_consistency", "user_checks", type_="check")
    op.drop_constraint("ck_user_checks_stars_count_non_negative", "user_checks", type_="check")
    op.drop_constraint("ck_user_checks_amount_cents_positive", "user_checks", type_="check")

    op.drop_constraint(
        "ck_stars_orders_product_payload_consistency",
        "stars_orders",
        type_="check",
    )
    op.drop_constraint("ck_stars_orders_stars_count_non_negative", "stars_orders", type_="check")
    op.drop_constraint("ck_stars_orders_amount_cents_non_negative", "stars_orders", type_="check")

    op.drop_constraint("ck_users_referrer_not_self", "users", type_="check")
    op.drop_constraint("ck_users_referral_earned_cents_non_negative", "users", type_="check")
    op.drop_constraint("ck_users_referral_balance_cents_non_negative", "users", type_="check")
    op.drop_constraint("ck_users_balance_cents_non_negative", "users", type_="check")
