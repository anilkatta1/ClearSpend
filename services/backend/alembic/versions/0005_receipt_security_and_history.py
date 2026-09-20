"""Add encrypted object-storage metadata, scanning, and receipt revision history."""

import sqlalchemy as sa

from alembic import op

revision = "0005_receipt_security"
down_revision = "0004_export_failures"
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    receipt_columns = _columns("receipts")
    with op.batch_alter_table("receipts") as batch:
        if "storage_bucket" not in receipt_columns:
            batch.add_column(sa.Column("storage_bucket", sa.String(120)))
        if "storage_key" not in receipt_columns:
            batch.add_column(sa.Column("storage_key", sa.String(500)))
            batch.create_unique_constraint("uq_receipts_storage_key", ["storage_key"])
        if "encryption_version" not in receipt_columns:
            batch.add_column(sa.Column("encryption_version", sa.String(30)))
        if "scan_status" not in receipt_columns:
            batch.add_column(
                sa.Column(
                    "scan_status",
                    sa.String(30),
                    nullable=False,
                    server_default="LEGACY_UNSCANNED",
                )
            )
            batch.create_index("ix_receipts_scan_status", ["scan_status"])
        if "scan_result" not in receipt_columns:
            batch.add_column(sa.Column("scan_result", sa.String(500)))
        if "security_flags" not in receipt_columns:
            batch.add_column(
                sa.Column("security_flags", sa.JSON(), nullable=False, server_default="[]")
            )
        batch.alter_column("content", existing_type=sa.LargeBinary(), nullable=True)

    if "expense_receipts" not in inspector.get_table_names():
        op.create_table(
            "expense_receipts",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False
            ),
            sa.Column("expense_id", sa.String(36), sa.ForeignKey("expenses.id"), nullable=False),
            sa.Column("receipt_id", sa.String(36), sa.ForeignKey("receipts.id"), nullable=False),
            sa.Column("revision", sa.Integer(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
            sa.Column(
                "attachment_type",
                sa.String(40),
                nullable=False,
                server_default="PRIMARY_RECEIPT",
            ),
            sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("supersedes_id", sa.String(36), sa.ForeignKey("expense_receipts.id")),
            sa.Column("uploaded_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
            sa.UniqueConstraint("expense_id", "revision", "receipt_id"),
            sa.UniqueConstraint("expense_id", "revision", "position"),
        )
        op.create_index(
            "ix_expense_receipts_organization_id",
            "expense_receipts",
            ["organization_id"],
        )
        op.create_index("ix_expense_receipts_expense_id", "expense_receipts", ["expense_id"])
        op.create_index("ix_expense_receipts_receipt_id", "expense_receipts", ["receipt_id"])
        op.create_index("ix_expense_receipts_is_current", "expense_receipts", ["is_current"])
        op.execute(
            sa.text(
                """
                INSERT INTO expense_receipts
                    (id, organization_id, expense_id, receipt_id, revision, position,
                     attachment_type, is_current, uploaded_by, created_at)
                SELECT CAST(gen_random_uuid() AS varchar), organization_id, id, receipt_id,
                       revision, 1, 'PRIMARY_RECEIPT', true, submitter_id, created_at
                FROM expenses
                WHERE receipt_id IS NOT NULL
                """
            )
        )

    attempt_columns = _columns("assessment_attempts")
    with op.batch_alter_table("assessment_attempts") as batch:
        if "receipt_version_ids" not in attempt_columns:
            batch.add_column(
                sa.Column("receipt_version_ids", sa.JSON(), nullable=False, server_default="[]")
            )
        if "receipt_hashes" not in attempt_columns:
            batch.add_column(
                sa.Column("receipt_hashes", sa.JSON(), nullable=False, server_default="[]")
            )


def downgrade() -> None:
    with op.batch_alter_table("assessment_attempts") as batch:
        batch.drop_column("receipt_hashes")
        batch.drop_column("receipt_version_ids")
    op.drop_table("expense_receipts")
    with op.batch_alter_table("receipts") as batch:
        batch.alter_column("content", existing_type=sa.LargeBinary(), nullable=False)
        batch.drop_column("security_flags")
        batch.drop_column("scan_result")
        batch.drop_column("scan_status")
        batch.drop_column("encryption_version")
        batch.drop_column("storage_key")
        batch.drop_column("storage_bucket")
