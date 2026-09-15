"""Add receipt-first workflow, safe idempotency, and accounting exports."""

import sqlalchemy as sa

from alembic import op

revision = "0002_release_mvp"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "receipts" not in tables:
        op.create_table(
            "receipts",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False
            ),
            sa.Column("uploader_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("filename", sa.String(200), nullable=False),
            sa.Column("content_type", sa.String(80), nullable=False),
            sa.Column("size_bytes", sa.Integer(), nullable=False),
            sa.Column("content_hash", sa.String(64), nullable=False),
            sa.Column("content", sa.LargeBinary(), nullable=False),
            sa.Column("extraction_status", sa.String(30), nullable=False),
            sa.Column("extracted_text", sa.Text(), nullable=False, server_default=""),
            sa.Column("extracted_merchant", sa.String(160)),
            sa.Column("extracted_date", sa.Date()),
            sa.Column("extracted_amount_minor", sa.BigInteger()),
            sa.Column("extracted_currency", sa.String(3)),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        op.create_index("ix_receipts_organization_id", "receipts", ["organization_id"])
        op.create_index("ix_receipts_uploader_id", "receipts", ["uploader_id"])

    expense_columns = _columns("expenses")
    with op.batch_alter_table("expenses") as batch:
        if "request_hash" not in expense_columns:
            batch.add_column(sa.Column("request_hash", sa.String(64), server_default="0" * 64))
        if "submitted_at" not in expense_columns:
            batch.add_column(sa.Column("submitted_at", sa.DateTime(timezone=True)))
        if "receipt_id" not in expense_columns:
            batch.add_column(sa.Column("receipt_id", sa.String(36), sa.ForeignKey("receipts.id")))
        if "information_request_message" not in expense_columns:
            batch.add_column(sa.Column("information_request_message", sa.String(500)))
        if "requested_fields" not in expense_columns:
            batch.add_column(sa.Column("requested_fields", sa.JSON(), server_default="[]"))
    op.execute("UPDATE expenses SET submitted_at = created_at WHERE submitted_at IS NULL")
    op.create_index("ix_expenses_receipt_id", "expenses", ["receipt_id"], if_not_exists=True)

    decision_columns = _columns("approval_decisions")
    with op.batch_alter_table("approval_decisions") as batch:
        if "request_hash" not in decision_columns:
            batch.add_column(sa.Column("request_hash", sa.String(64), server_default="0" * 64))
        if "requested_fields" not in decision_columns:
            batch.add_column(sa.Column("requested_fields", sa.JSON(), server_default="[]"))
        if "reviewer_active_ms" not in decision_columns:
            batch.add_column(sa.Column("reviewer_active_ms", sa.Integer()))

    if "accounting_exports" not in tables:
        op.create_table(
            "accounting_exports",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False
            ),
            sa.Column(
                "expense_id",
                sa.String(36),
                sa.ForeignKey("expenses.id"),
                nullable=False,
                unique=True,
            ),
            sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("account_code", sa.String(80), nullable=False),
            sa.Column("cost_center", sa.String(80), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("csv_content", sa.Text()),
            sa.Column("error_code", sa.String(80)),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        op.create_index(
            "ix_accounting_exports_organization_id", "accounting_exports", ["organization_id"]
        )
        op.create_index("ix_accounting_exports_expense_id", "accounting_exports", ["expense_id"])


def downgrade() -> None:
    op.drop_table("accounting_exports")
    with op.batch_alter_table("approval_decisions") as batch:
        batch.drop_column("reviewer_active_ms")
        batch.drop_column("requested_fields")
        batch.drop_column("request_hash")
    with op.batch_alter_table("expenses") as batch:
        batch.drop_column("requested_fields")
        batch.drop_column("information_request_message")
        batch.drop_column("receipt_id")
        batch.drop_column("submitted_at")
        batch.drop_column("request_hash")
    op.drop_table("receipts")
