"""Scope idempotency keys to the acting user.

Revision ID: 0003_actor_idempotency
Revises: 0002_release_mvp
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_actor_idempotency"
down_revision = "0002_release_mvp"
branch_labels = None
depends_on = None


def _constraint_for(table: str, columns: set[str]) -> str | None:
    constraints = sa.inspect(op.get_bind()).get_unique_constraints(table)
    return next(
        (
            str(item["name"])
            for item in constraints
            if item.get("name") and set(item.get("column_names") or []) == columns
        ),
        None,
    )


def upgrade() -> None:
    old_expense = _constraint_for("expenses", {"organization_id", "idempotency_key"})
    new_expense = _constraint_for(
        "expenses", {"organization_id", "submitter_id", "idempotency_key"}
    )
    if old_expense:
        op.drop_constraint(old_expense, "expenses", type_="unique")
    if not new_expense:
        op.create_unique_constraint(
            "uq_expense_actor_idempotency",
            "expenses",
            ["organization_id", "submitter_id", "idempotency_key"],
        )

    old_decision = _constraint_for("approval_decisions", {"organization_id", "idempotency_key"})
    new_decision = _constraint_for(
        "approval_decisions", {"organization_id", "actor_id", "idempotency_key"}
    )
    if old_decision:
        op.drop_constraint(old_decision, "approval_decisions", type_="unique")
    if not new_decision:
        op.create_unique_constraint(
            "uq_decision_actor_idempotency",
            "approval_decisions",
            ["organization_id", "actor_id", "idempotency_key"],
        )


def downgrade() -> None:
    actor_expense = _constraint_for(
        "expenses", {"organization_id", "submitter_id", "idempotency_key"}
    )
    if actor_expense:
        op.drop_constraint(actor_expense, "expenses", type_="unique")
    op.create_unique_constraint(
        "uq_expense_idempotency",
        "expenses",
        ["organization_id", "idempotency_key"],
    )

    actor_decision = _constraint_for(
        "approval_decisions", {"organization_id", "actor_id", "idempotency_key"}
    )
    if actor_decision:
        op.drop_constraint(actor_decision, "approval_decisions", type_="unique")
    op.create_unique_constraint(
        "uq_decision_idempotency",
        "approval_decisions",
        ["organization_id", "idempotency_key"],
    )
