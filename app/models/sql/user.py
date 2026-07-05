from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.dto.user import UserDto
from app.utils.custom_types import Int64

from .base import Base
from .mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "balance_cents >= 0",
            name="ck_users_balance_cents_non_negative",
        ),
        CheckConstraint(
            "referral_balance_cents >= 0",
            name="ck_users_referral_balance_cents_non_negative",
        ),
        CheckConstraint(
            "referral_earned_cents >= 0",
            name="ck_users_referral_earned_cents_non_negative",
        ),
        CheckConstraint(
            "referrer_id IS NULL OR referrer_id <> id",
            name="ck_users_referrer_not_self",
        ),
        Index("ix_users_referrer_id", "referrer_id"),
    )

    id: Mapped[Int64] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    language: Mapped[str] = mapped_column(String(length=2))
    language_code: Mapped[Optional[str]] = mapped_column()
    balance_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    referral_balance_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    referral_earned_cents: Mapped[int] = mapped_column(nullable=False, default=0)
    referrer_id: Mapped[Optional[Int64]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    blocked_at: Mapped[Optional[datetime]] = mapped_column()

    def dto(self) -> UserDto:
        return UserDto.model_validate(self)
