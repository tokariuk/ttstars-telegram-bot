from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.stars_sell_order import (
    StarsSellOrderResolutionReason,
    StarsSellOrderStatus,
    StarsSellPayoutMethod,
)
from app.models.dto.stars_sell_order import StarsSellOrderDto
from app.utils.custom_types import Int32, Int64

from .base import Base
from .mixins import TimestampMixin


class StarsSellOrder(Base, TimestampMixin):
    __tablename__ = "stars_sell_orders"
    __table_args__ = (
        CheckConstraint(
            "stars_count > 0",
            name="ck_stars_sell_orders_stars_count_positive",
        ),
        CheckConstraint(
            "invoice_total_amount > 0",
            name="ck_stars_sell_orders_invoice_total_amount_positive",
        ),
        CheckConstraint(
            "payout_amount_cents >= 0",
            name="ck_stars_sell_orders_payout_amount_non_negative",
        ),
        Index("ix_stars_sell_orders_user_id_created_at", "user_id", "created_at"),
        Index("ix_stars_sell_orders_status_created_at", "status", "created_at"),
        Index("ix_stars_sell_orders_payout_available_at", "payout_available_at"),
        Index("ix_stars_sell_orders_invoice_payload", "invoice_payload", unique=True),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    stars_count: Mapped[Int32] = mapped_column(nullable=False)
    payout_method: Mapped[StarsSellPayoutMethod] = mapped_column(String(length=32), nullable=False)
    payout_wallet: Mapped[str] = mapped_column(String(length=128), nullable=False)
    payout_amount_cents: Mapped[Int32] = mapped_column(nullable=False)
    invoice_payload: Mapped[str] = mapped_column(String(length=96), nullable=False, unique=True)
    invoice_message_id: Mapped[Optional[Int64]] = mapped_column(nullable=True)
    invoice_total_amount: Mapped[Int32] = mapped_column(nullable=False)
    telegram_payment_charge_id: Mapped[Optional[str]] = mapped_column(
        String(length=128),
        nullable=True,
    )
    provider_payment_charge_id: Mapped[Optional[str]] = mapped_column(
        String(length=128),
        nullable=True,
    )
    paid_stars_amount: Mapped[Optional[Int32]] = mapped_column(nullable=True)
    status: Mapped[StarsSellOrderStatus] = mapped_column(String(length=32), nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(nullable=True)
    resolution_reason: Mapped[Optional[StarsSellOrderResolutionReason]] = mapped_column(
        String(length=64),
        nullable=True,
    )
    resolution_note: Mapped[Optional[str]] = mapped_column(nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    payout_available_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    refunded_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def dto(self) -> StarsSellOrderDto:
        return StarsSellOrderDto.model_validate(self)
