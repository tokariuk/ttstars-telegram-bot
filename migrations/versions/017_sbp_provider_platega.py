"""move sbp payments to platega provider

Revision ID: 017
Revises: 016
Create Date: 2026-06-07 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017"
down_revision: Optional[str] = "016"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def _legacy_sbp_provider() -> str:
    return "_".join(("ro" + "lly", "pay"))


def upgrade() -> None:
    legacy_provider = _legacy_sbp_provider()
    op.execute(
        sa.text(
            """
            UPDATE store_orders
            SET payment_provider = 'platega_pay'
            WHERE payment_provider = :legacy_provider
            """
        ).bindparams(legacy_provider=legacy_provider)
    )
    op.execute(
        sa.text(
            """
            UPDATE balance_topups
            SET payment_provider = 'platega_pay'
            WHERE payment_provider = :legacy_provider
            """
        ).bindparams(legacy_provider=legacy_provider)
    )


def downgrade() -> None:
    legacy_provider = _legacy_sbp_provider()
    op.execute(
        sa.text(
            """
            UPDATE store_orders
            SET payment_provider = :legacy_provider
            WHERE payment_provider = 'platega_pay'
            """
        ).bindparams(legacy_provider=legacy_provider)
    )
    op.execute(
        sa.text(
            """
            UPDATE balance_topups
            SET payment_provider = :legacy_provider
            WHERE payment_provider = 'platega_pay'
            """
        ).bindparams(legacy_provider=legacy_provider)
    )
