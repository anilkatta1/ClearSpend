"""Persist actionable accounting export failure details.

Revision ID: 0004_export_failures
Revises: 0003_actor_idempotency
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_export_failures"
down_revision = "0003_actor_idempotency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {item["name"] for item in sa.inspect(op.get_bind()).get_columns("accounting_exports")}
    if "error_detail" not in columns:
        op.add_column(
            "accounting_exports",
            sa.Column("error_detail", sa.String(500)),
        )


def downgrade() -> None:
    op.drop_column("accounting_exports", "error_detail")
