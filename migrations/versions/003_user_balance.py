"""user balance

Revision ID: 003
Revises: 002
Create Date: 2026-03-19 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Optional[str] = "002"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "balance_cents",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.alter_column("users", "balance_cents", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "balance_cents")
