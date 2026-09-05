from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.custom_types import Int64

from .base import Base
from .mixins import TimestampMixin


class PromoCode(Base, TimestampMixin):
    __tablename__ = "promo_codes"
    __table_args__ = (
        CheckConstraint("amount_cents > 0", name="ck_promo_codes_amount_positive"),
        CheckConstraint(
            "max_activations IS NULL OR max_activations > 0",
            name="ck_promo_codes_max_activations_positive",
        ),
        CheckConstraint("activations >= 0", name="ck_promo_codes_activations_non_negative"),
        Index("ix_promo_codes_created_at", "created_at"),
    )

    code: Mapped[str] = mapped_column(String(length=40), primary_key=True)
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    activations: Mapped[int] = mapped_column(nullable=False, default=0)
    max_activations: Mapped[int | None] = mapped_column(nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class PromoCodeActivation(Base):
    __tablename__ = "promo_code_activations"
    __table_args__ = (
        UniqueConstraint("promo_code", "user_id", name="uq_promo_activation_code_user"),
        Index("ix_promo_code_activations_code_created", "promo_code", "created_at"),
        Index("ix_promo_code_activations_user_id", "user_id"),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    promo_code: Mapped[str] = mapped_column(
        String(length=40),
        ForeignKey("promo_codes.code", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
