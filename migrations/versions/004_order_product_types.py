"""orders product types

Revision ID: 004
Revises: 003
Create Date: 2026-03-22 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Optional[str] = "003"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "stars_orders",
        sa.Column(
            "product_type",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'stars'"),
        ),
    )
    op.add_column(
        "stars_orders",
        sa.Column("premium_months", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_stars_orders_product_type",
        "stars_orders",
        ["product_type"],
        unique=False,
    )
    op.alter_column("stars_orders", "product_type", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_stars_orders_product_type", table_name="stars_orders")
    op.drop_column("stars_orders", "premium_months")
    op.drop_column("stars_orders", "product_type")
