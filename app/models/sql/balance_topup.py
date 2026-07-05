from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.stars_order import StarsOrderProductType, StarsOrderStatus, StarsPaymentProvider
from app.models.dto.balance_topup import BalanceTopupDto
from app.utils.custom_types import Int32, Int64

from .base import Base
from .mixins import TimestampMixin


class BalanceTopup(Base, TimestampMixin):
    __tablename__ = "balance_topups"
    __table_args__ = (
        CheckConstraint(
            "amount_cents >= 0",
            name="ck_balance_topups_amount_cents_non_negative",
        ),
        CheckConstraint(
            "auto_stars_count >= 0",
            name="ck_balance_topups_auto_stars_count_non_negative",
        ),
        CheckConstraint(
            "linked_order_id IS NULL OR linked_order_id > 0",
            name="ck_balance_topups_linked_order_id_positive",
        ),
        Index("ix_balance_topups_user_id_created_at", "user_id", "created_at"),
        Index("ix_balance_topups_status", "status"),
        Index(
            "ix_balance_topups_provider_invoice_id",
            "payment_provider",
            "provider_invoice_id",
        ),
        Index(
            "ix_balance_topups_provider_payload",
            "payment_provider",
            "payment_payload",
        ),
        Index(
            "ix_balance_topups_provider_reference",
            "payment_provider",
            "provider_reference",
        ),
        Index("ix_balance_topups_linked_order_id", "linked_order_id"),
        Index("ix_balance_topups_auto_product_type", "auto_product_type"),
        Index("ix_balance_topups_polling_queue", "status", "created_at"),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    auto_product_type: Mapped[Optional[StarsOrderProductType]] = mapped_column(
        String(length=16),
        nullable=True,
    )
    auto_recipient_username: Mapped[Optional[str]] = mapped_column(
        String(length=32),
        nullable=True,
    )
    auto_stars_count: Mapped[Int32] = mapped_column(nullable=False, default=0)
    auto_premium_months: Mapped[Optional[Int32]] = mapped_column(nullable=True)
    auto_recipient_user_id: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    auto_gift_id: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    auto_gift_message: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    auto_gift_sender_private: Mapped[Optional[bool]] = mapped_column(nullable=True)

    linked_order_id: Mapped[Optional[Int64]] = mapped_column(
        ForeignKey("store_orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)

    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    credited_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def dto(self) -> BalanceTopupDto:
        return BalanceTopupDto.model_validate(self)
