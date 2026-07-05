"""checks stars-only payload

Revision ID: 009
Revises: 008
Create Date: 2026-04-21 00:00:00.000000

"""

from typing import Optional, Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "009"
down_revision: Optional[str] = "008"
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    connection = op.get_bind()
    non_stars_rows = int(
        connection.execute(
            sa.text(
                "SELECT count(*) FROM user_checks WHERE product_type <> 'stars'",
            )
        ).scalar_one()
    )
    if non_stars_rows > 0:
        raise RuntimeError(
            "Cannot migrate user_checks to stars-only schema: found non-stars checks.",
        )

    op.drop_constraint(
        "ck_user_checks_product_payload_consistency",
        "user_checks",
        type_="check",
    )
    op.drop_constraint(
        "ck_user_checks_stars_count_non_negative",
        "user_checks",
        type_="check",
    )

    op.drop_column("user_checks", "premium_months")
    op.drop_column("user_checks", "product_type")

    op.create_check_constraint(
        "ck_user_checks_stars_count_positive",
        "user_checks",
        "stars_count > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_user_checks_stars_count_positive", "user_checks", type_="check")

    op.add_column(
        "user_checks",
        sa.Column(
            "product_type",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'stars'"),
        ),
    )
    op.add_column(
        "user_checks",
        sa.Column("premium_months", sa.Integer(), nullable=True),
    )

    op.create_check_constraint(
        "ck_user_checks_stars_count_non_negative",
        "user_checks",
        "stars_count >= 0",
    )
    op.create_check_constraint(
        "ck_user_checks_product_payload_consistency",
        "user_checks",
        "("
        "(product_type = 'stars' AND stars_count > 0 AND premium_months IS NULL) "
        "OR "
        "("
        "product_type = 'premium' AND stars_count = 0 "
        "AND premium_months IS NOT NULL AND premium_months > 0"
        ") "
        "OR "
        "(product_type = 'topup' AND stars_count = 0 AND premium_months IS NULL)"
        ")",
    )

    op.alter_column("user_checks", "product_type", server_default=None)
