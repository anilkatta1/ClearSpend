"""Add confirmed line-item facts to versioned receipt associations."""

import sqlalchemy as sa

from alembic import op

revision = "0006_expense_report_items"
down_revision = "0005_receipt_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing = {
        column["name"]
        for column in sa.inspect(op.get_bind()).get_columns("expense_receipts")
    }
    with op.batch_alter_table("expense_receipts") as batch:
        if "claimed_merchant" not in existing:
            batch.add_column(sa.Column("claimed_merchant", sa.String(160)))
        if "claimed_amount_minor" not in existing:
            batch.add_column(sa.Column("claimed_amount_minor", sa.BigInteger()))
        if "claimed_currency" not in existing:
            batch.add_column(sa.Column("claimed_currency", sa.String(3)))
        if "claimed_incurred_date" not in existing:
            batch.add_column(sa.Column("claimed_incurred_date", sa.Date()))
    op.execute(
        sa.text(
            """
            UPDATE expense_receipts er
            SET claimed_merchant = e.merchant,
                claimed_amount_minor = e.amount_minor,
                claimed_currency = e.currency,
                claimed_incurred_date = e.incurred_date
            FROM expenses e
            WHERE er.expense_id = e.id
            """
        )
    )


def downgrade() -> None:
    with op.batch_alter_table("expense_receipts") as batch:
        batch.drop_column("claimed_incurred_date")
        batch.drop_column("claimed_currency")
        batch.drop_column("claimed_amount_minor")
        batch.drop_column("claimed_merchant")
