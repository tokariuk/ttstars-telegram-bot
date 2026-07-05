from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.dto.stars_order import StarsOrderDto
from app.utils.custom_types import Int32, Int64

from .base import Base
from .mixins import TimestampMixin


class StarsOrder(Base, TimestampMixin):
    __tablename__ = "store_orders"
    __table_args__ = (
        CheckConstraint(
            "amount_cents >= 0",
            name="ck_store_orders_amount_cents_non_negative",
        ),
        CheckConstraint(
            "stars_count >= 0",
            name="ck_store_orders_stars_count_non_negative",
        ),
        CheckConstraint(
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
            name="ck_store_orders_product_payload_consistency",
        ),
        CheckConstraint(
            "recipient_user_id IS NULL OR recipient_user_id > 0",
            name="ck_store_orders_recipient_user_id_positive",
        ),
        Index("ix_store_orders_user_id_created_at", "user_id", "created_at"),
        Index("ix_store_orders_status", "status"),
        Index(
            "ix_store_orders_provider_invoice_id",
            "payment_provider",
            "provider_invoice_id",
        ),
        Index("ix_store_orders_product_type", "product_type"),
        Index("ix_store_orders_referral_processed_at", "referral_processed_at"),
        Index("ix_store_orders_polling_queue", "status", "created_at"),
        Index(
            "ix_store_orders_provider_payload",
            "payment_provider",
            "payment_payload",
        ),
        Index(
            "ix_store_orders_provider_reference",
            "payment_provider",
            "provider_reference",
        ),
        Index(
            "ix_store_orders_user_status_created_at",
            "user_id",
            "status",
            "created_at",
        ),
        Index("ix_store_orders_recipient_user_id", "recipient_user_id"),
        Index("ix_store_orders_gift_id", "gift_id"),
        Index("ix_store_orders_funding_topup_id", "funding_topup_id"),
        Index("ix_store_orders_funding_provider", "funding_provider"),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipient_username: Mapped[str] = mapped_column(String(length=32), nullable=False)
    stars_count: Mapped[Int32] = mapped_column(nullable=False)
    product_type: Mapped[StarsOrderProductType] = mapped_column(
        String(length=16),
        nullable=False,
    )
    premium_months: Mapped[Optional[Int32]] = mapped_column(nullable=True)
    recipient_user_id: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    gift_id: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    gift_message: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    gift_sender_private: Mapped[Optional[bool]] = mapped_column(nullable=True)
    amount_cents: Mapped[Int32] = mapped_column(nullable=False)
    payment_provider: Mapped[StarsPaymentProvider] = mapped_column(
        String(length=32),
        nullable=False,
    )
    payment_currency: Mapped[str] = mapped_column(String(length=16), nullable=False)
    status: Mapped[StarsOrderStatus] = mapped_column(String(length=32), nullable=False)
    payment_payload: Mapped[Optional[str]] = mapped_column(nullable=True)
    provider_invoice_id: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    provider_reference: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    provider_amount_minor: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    provider_status: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    checkout_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    checkout_message_id: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    funding_topup_id: Mapped[Optional[Int64]] = mapped_column(
        ForeignKey("balance_topups.id", ondelete="SET NULL"),
        nullable=True,
    )
    funding_provider: Mapped[Optional[StarsPaymentProvider]] = mapped_column(
        String(length=32),
        nullable=True,
    )
    fragment_tx_hash: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    fragment_error: Mapped[Optional[str]] = mapped_column(nullable=True)
    referral_reward_total_cents: Mapped[Int32] = mapped_column(nullable=False, default=0)
    referral_reward_level1_cents: Mapped[Int32] = mapped_column(nullable=False, default=0)
    referral_reward_level2_cents: Mapped[Int32] = mapped_column(nullable=False, default=0)
    referral_reward_level3_cents: Mapped[Int32] = mapped_column(nullable=False, default=0)
    referral_processed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def dto(self) -> StarsOrderDto:
        return StarsOrderDto.model_validate(self)
