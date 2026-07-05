"""drop legacy payment providers

Revision ID: 012
Revises: 011
Create Date: 2026-05-09 01:40:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012"
down_revision: Optional[str] = "011"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    allowed_providers = (
        "crypto_bot",
        "xrocket_pay",
        "lzt_pay",
        "nice_pay_ru",
        "nice_pay_kz",
        "heleket_pay",
        "platega_pay",
        "balance",
    )
    op.execute(
        sa.text(
            """
            DELETE FROM store_orders
            WHERE payment_provider NOT IN :allowed
            """
        ).bindparams(sa.bindparam("allowed", value=allowed_providers, expanding=True))
    )


def downgrade() -> None:
    # Irreversible data cleanup.
    pass
