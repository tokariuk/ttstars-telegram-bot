"""stars sell resolution fields

Revision ID: 014
Revises: 013
Create Date: 2026-05-15 02:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014"
down_revision: Optional[str] = "013"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "stars_sell_orders",
        sa.Column("resolution_reason", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "stars_sell_orders",
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )
    op.add_column(
        "stars_sell_orders",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "stars_sell_orders",
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("stars_sell_orders", "refunded_at")
    op.drop_column("stars_sell_orders", "rejected_at")
    op.drop_column("stars_sell_orders", "resolution_note")
    op.drop_column("stars_sell_orders", "resolution_reason")
