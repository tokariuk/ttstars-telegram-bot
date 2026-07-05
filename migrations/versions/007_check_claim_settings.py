"""check claim settings

Revision ID: 007
Revises: 006
Create Date: 2026-04-09 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007"
down_revision: Optional[str] = "006"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    op.add_column(
        "user_checks",
        sa.Column("claim_username", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "user_checks",
        sa.Column("claim_password_hash", sa.String(length=128), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_checks", "claim_password_hash")
    op.drop_column("user_checks", "claim_username")
