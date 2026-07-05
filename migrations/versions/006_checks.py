"""checks

Revision ID: 006
Revises: 005
Create Date: 2026-04-06 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006"
down_revision: Optional[str] = "005"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.create_table(
        "user_checks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=48), nullable=False),
        sa.Column("creator_id", sa.BigInteger(), nullable=False),
        sa.Column("product_type", sa.String(length=16), nullable=False),
        sa.Column("stars_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("premium_months", sa.Integer(), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("recipient_id", sa.BigInteger(), nullable=True),
        sa.Column("inline_message_id", sa.String(length=128), nullable=True),
        sa.Column("provider_tx_hash", sa.String(length=128), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_index("ix_user_checks_code", "user_checks", ["code"], unique=True)
    op.create_index("ix_user_checks_creator_id", "user_checks", ["creator_id"], unique=False)
    op.create_index("ix_user_checks_recipient_id", "user_checks", ["recipient_id"], unique=False)
    op.create_index("ix_user_checks_status", "user_checks", ["status"], unique=False)
    op.create_index(
        "ix_user_checks_creator_status",
        "user_checks",
        ["creator_id", "status"],
        unique=False,
    )
    op.alter_column("user_checks", "stars_count", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_user_checks_creator_status", table_name="user_checks")
    op.drop_index("ix_user_checks_status", table_name="user_checks")
    op.drop_index("ix_user_checks_recipient_id", table_name="user_checks")
    op.drop_index("ix_user_checks_creator_id", table_name="user_checks")
    op.drop_index("ix_user_checks_code", table_name="user_checks")
    op.drop_table("user_checks")
