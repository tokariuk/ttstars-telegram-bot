from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.enums.check import CheckStatus
from app.models.dto.check import CheckDto
from app.utils.custom_types import Int32, Int64

from .base import Base
from .mixins import TimestampMixin


class UserCheck(Base, TimestampMixin):
    __tablename__ = "stars_checks"
    __table_args__ = (
        CheckConstraint(
            "amount_cents > 0",
            name="ck_stars_checks_amount_cents_positive",
        ),
        CheckConstraint(
            "stars_count > 0",
            name="ck_stars_checks_stars_count_positive",
        ),
        Index("ix_stars_checks_code", "code", unique=True),
        Index("ix_stars_checks_creator_id", "creator_id"),
        Index("ix_stars_checks_recipient_id", "recipient_id"),
        Index("ix_stars_checks_status", "status"),
        Index("ix_stars_checks_creator_status", "creator_id", "status"),
        Index("ix_stars_checks_inline_message_id", "inline_message_id"),
        Index(
            "ix_stars_checks_creator_status_updated_at",
            "creator_id",
            "status",
            "updated_at",
        ),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(length=48), nullable=False, unique=True)
    creator_id: Mapped[Int64] = mapped_column(ForeignKey("users.id"), nullable=False)
    stars_count: Mapped[Int32] = mapped_column(nullable=False)
    amount_cents: Mapped[Int32] = mapped_column(nullable=False)
    status: Mapped[CheckStatus] = mapped_column(String(length=16), nullable=False)
    claim_username: Mapped[Optional[str]] = mapped_column(String(length=64), nullable=True)
    claim_password_hash: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    recipient_id: Mapped[Optional[Int64]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    inline_message_id: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    provider_tx_hash: Mapped[Optional[str]] = mapped_column(String(length=128), nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(nullable=True)
    redeemed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def dto(self) -> CheckDto:
        return CheckDto.model_validate(self)
