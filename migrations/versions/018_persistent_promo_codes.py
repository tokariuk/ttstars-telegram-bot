"""persistent promo codes

Revision ID: 018
Revises: 017
Create Date: 2026-09-05 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "018"
down_revision: Optional[str] = "017"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "promo_codes",
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("activations", sa.Integer(), server_default="0", nullable=False),
        sa.Column("max_activations", sa.Integer(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
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
        sa.CheckConstraint("activations >= 0", name="ck_promo_codes_activations_non_negative"),
        sa.CheckConstraint("amount_cents > 0", name="ck_promo_codes_amount_positive"),
        sa.CheckConstraint(
            "max_activations IS NULL OR max_activations > 0",
            name="ck_promo_codes_max_activations_positive",
        ),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_index("ix_promo_codes_created_at", "promo_codes", ["created_at"])
    op.create_table(
        "promo_code_activations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("promo_code", sa.String(length=40), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["promo_code"], ["promo_codes.code"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("promo_code", "user_id", name="uq_promo_activation_code_user"),
    )
    op.create_index(
        "ix_promo_code_activations_code_created",
        "promo_code_activations",
        ["promo_code", "created_at"],
    )
    op.create_index(
        "ix_promo_code_activations_user_id",
        "promo_code_activations",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("promo_code_activations")
    op.drop_index("ix_promo_codes_created_at", table_name="promo_codes")
    op.drop_table("promo_codes")
