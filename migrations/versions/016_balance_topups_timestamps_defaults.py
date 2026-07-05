"""set defaults for balance topups timestamps

Revision ID: 016
Revises: 015
Create Date: 2026-05-23 21:30:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016"
down_revision: Optional[str] = "015"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.alter_column(
        "balance_topups",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("timezone('UTC', now())"),
        nullable=False,
    )
    op.alter_column(
        "balance_topups",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("timezone('UTC', now())"),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "balance_topups",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
    op.alter_column(
        "balance_topups",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        nullable=False,
    )
