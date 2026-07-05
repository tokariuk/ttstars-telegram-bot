"""storefront table naming

Revision ID: 010
Revises: 009
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Optional, Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "010"
down_revision: Optional[str] = "009"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.rename_table("stars_orders", "store_orders")
    op.rename_table("user_checks", "stars_checks")

    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_stars_orders_amount_cents_non_negative "
        "TO ck_store_orders_amount_cents_non_negative"
    )
    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_stars_orders_stars_count_non_negative "
        "TO ck_store_orders_stars_count_non_negative"
    )
    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_stars_orders_product_payload_consistency "
        "TO ck_store_orders_product_payload_consistency"
    )
    op.execute(
        "ALTER TABLE stars_checks RENAME CONSTRAINT "
        "ck_user_checks_amount_cents_positive "
        "TO ck_stars_checks_amount_cents_positive"
    )
    op.execute(
        "ALTER TABLE stars_checks RENAME CONSTRAINT "
        "ck_user_checks_stars_count_positive "
        "TO ck_stars_checks_stars_count_positive"
    )

    op.execute(
        "ALTER INDEX ix_stars_orders_user_id_created_at "
        "RENAME TO ix_store_orders_user_id_created_at"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_status "
        "RENAME TO ix_store_orders_status"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_provider_invoice_id "
        "RENAME TO ix_store_orders_provider_invoice_id"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_product_type "
        "RENAME TO ix_store_orders_product_type"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_referral_processed_at "
        "RENAME TO ix_store_orders_referral_processed_at"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_polling_queue "
        "RENAME TO ix_store_orders_polling_queue"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_provider_payload "
        "RENAME TO ix_store_orders_provider_payload"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_provider_reference "
        "RENAME TO ix_store_orders_provider_reference"
    )
    op.execute(
        "ALTER INDEX ix_stars_orders_user_status_created_at "
        "RENAME TO ix_store_orders_user_status_created_at"
    )

    op.execute(
        "ALTER INDEX ix_user_checks_code "
        "RENAME TO ix_stars_checks_code"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_creator_id "
        "RENAME TO ix_stars_checks_creator_id"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_recipient_id "
        "RENAME TO ix_stars_checks_recipient_id"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_status "
        "RENAME TO ix_stars_checks_status"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_creator_status "
        "RENAME TO ix_stars_checks_creator_status"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_inline_message_id "
        "RENAME TO ix_stars_checks_inline_message_id"
    )
    op.execute(
        "ALTER INDEX ix_user_checks_creator_status_updated_at "
        "RENAME TO ix_stars_checks_creator_status_updated_at"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_store_orders_amount_cents_non_negative "
        "TO ck_stars_orders_amount_cents_non_negative"
    )
    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_store_orders_stars_count_non_negative "
        "TO ck_stars_orders_stars_count_non_negative"
    )
    op.execute(
        "ALTER TABLE store_orders RENAME CONSTRAINT "
        "ck_store_orders_product_payload_consistency "
        "TO ck_stars_orders_product_payload_consistency"
    )
    op.execute(
        "ALTER TABLE stars_checks RENAME CONSTRAINT "
        "ck_stars_checks_amount_cents_positive "
        "TO ck_user_checks_amount_cents_positive"
    )
    op.execute(
        "ALTER TABLE stars_checks RENAME CONSTRAINT "
        "ck_stars_checks_stars_count_positive "
        "TO ck_user_checks_stars_count_positive"
    )

    op.execute(
        "ALTER INDEX ix_store_orders_user_id_created_at "
        "RENAME TO ix_stars_orders_user_id_created_at"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_status "
        "RENAME TO ix_stars_orders_status"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_provider_invoice_id "
        "RENAME TO ix_stars_orders_provider_invoice_id"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_product_type "
        "RENAME TO ix_stars_orders_product_type"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_referral_processed_at "
        "RENAME TO ix_stars_orders_referral_processed_at"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_polling_queue "
        "RENAME TO ix_stars_orders_polling_queue"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_provider_payload "
        "RENAME TO ix_stars_orders_provider_payload"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_provider_reference "
        "RENAME TO ix_stars_orders_provider_reference"
    )
    op.execute(
        "ALTER INDEX ix_store_orders_user_status_created_at "
        "RENAME TO ix_stars_orders_user_status_created_at"
    )

    op.execute(
        "ALTER INDEX ix_stars_checks_code "
        "RENAME TO ix_user_checks_code"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_creator_id "
        "RENAME TO ix_user_checks_creator_id"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_recipient_id "
        "RENAME TO ix_user_checks_recipient_id"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_status "
        "RENAME TO ix_user_checks_status"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_creator_status "
        "RENAME TO ix_user_checks_creator_status"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_inline_message_id "
        "RENAME TO ix_user_checks_inline_message_id"
    )
    op.execute(
        "ALTER INDEX ix_stars_checks_creator_status_updated_at "
        "RENAME TO ix_user_checks_creator_status_updated_at"
    )

    op.rename_table("store_orders", "stars_orders")
    op.rename_table("stars_checks", "user_checks")
