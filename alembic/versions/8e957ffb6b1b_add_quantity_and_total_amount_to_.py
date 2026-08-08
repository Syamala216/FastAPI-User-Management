"""add quantity and total amount to transactions

Revision ID: 8e957ffb6b1b
Revises: 463ea232927e
Create Date: 2026-08-08 12:51:51.984418

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8e957ffb6b1b"
down_revision: Union[str, Sequence[str], None] = "463ea232927e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "transactions",
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
            server_default="1"
        )
    )

    op.add_column(
        "transactions",
        sa.Column(
            "total_amount",
            sa.Float(),
            nullable=False,
            server_default="0"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("transactions", "total_amount")
    op.drop_column("transactions", "quantity")