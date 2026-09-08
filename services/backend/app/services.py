from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import append_audit
from app.db import (
    ApprovalDecision,
    AssessmentAttempt,
    Expense,
    PolicyRule,
    PolicySection,
    PolicyVersion,
)
from app.domain import ClaimFacts, DecisionAction, ExpenseState, Recommendation, ensure_transition
from app.graph import assess_claim


class DomainConflict(Exception):
    pass


def active_policy(session: Session, organization_id: str) -> PolicyVersion:
    policy = session.scalar(
        select(PolicyVersion)
        .where(
            PolicyVersion.organization_id == organization_id,
            PolicyVersion.status == "PUBLISHED",
        )
        .order_by(PolicyVersion.version.desc())
        .limit(1)
    )
    if policy is None:
        raise DomainConflict("No published policy exists")
    return policy


def serialize_expense(expense: Expense) -> dict[str, Any]:
    latest = max(expense.attempts, key=lambda item: item.created_at, default=None)
    return {
        "id": expense.id,
        "merchant": expense.merchant,
        "amount_minor": expense.amount_minor,
        "currency": expense.currency,
        "incurred_date": expense.incurred_date,
        "category": expense.category,
        "purpose": expense.purpose,
        "state": expense.state,
        "row_version": expense.row_version,
        "revision": expense.revision,
        "receipt_present": expense.receipt_present,
        "created_at": expense.created_at,
        "recommendation": latest.recommendation if latest else None,
        "checks": latest.checks if latest else [],
    }


def process_assessment(session: Session, expense_id: str, correlation_id: str) -> None:
    expense = session.scalar(select(Expense).where(Expense.id == expense_id).with_for_update())
    if expense is None or expense.state not in {ExpenseState.SUBMITTED, ExpenseState.ASSESSING}:
        return
    existing = session.scalar(
        select(AssessmentAttempt).where(
            AssessmentAttempt.expense_id == expense.id,
            AssessmentAttempt.revision == expense.revision,
            AssessmentAttempt.engine_version == "rules-v1",
        )
    )
    if existing:
        return
    if expense.state == ExpenseState.SUBMITTED:
        ensure_transition(ExpenseState.SUBMITTED, ExpenseState.ASSESSING)
        expense.state = ExpenseState.ASSESSING
    policy_rules = session.execute(
        select(PolicyRule.rule_type, PolicyRule.params, PolicySection.id)
        .join(PolicySection, PolicySection.id == PolicyRule.section_id)
        .where(PolicySection.policy_version_id == expense.policy_version_id)
        .order_by(PolicyRule.priority)
    ).all()
    state = assess_claim(
        ClaimFacts(
            amount_minor=expense.amount_minor,
            currency=expense.currency,
            category=expense.category,
            merchant=expense.merchant,
            purpose=expense.purpose,
            incurred_date=expense.incurred_date,
            submitted_date=date.today(),
            receipt_present=expense.receipt_present,
            receipt_hash=expense.receipt_hash,
        ),
        [(row[0], row[1], row[2]) for row in policy_rules],
    )
    attempt = AssessmentAttempt(
        organization_id=expense.organization_id,
        expense_id=expense.id,
        revision=expense.revision,
        technical_status="COMPLETED" if not state.get("technical_failure") else "FALLBACK",
        recommendation=state.get("recommendation", Recommendation.REVIEW),
        checks=[check.model_dump(mode="json") for check in state["checks"]],
        citations=state["section_ids"],
        provider=state.get("provider", "none"),
        model=state.get("model"),
    )
    session.add(attempt)
    ensure_transition(ExpenseState.ASSESSING, ExpenseState.AWAITING_REVIEW)
    expense.state = ExpenseState.AWAITING_REVIEW
    expense.row_version += 1
    append_audit(
        session,
        organization_id=expense.organization_id,
        actor_id=None,
        entity_type="expense",
        entity_id=expense.id,
        action="expense.assessed",
        metadata={"recommendation": str(attempt.recommendation), "revision": expense.revision},
        correlation_id=correlation_id,
    )
    session.commit()


def decide(
    session: Session,
    *,
    expense: Expense,
    actor_id: str,
    action: DecisionAction,
    reason: str,
    expected_version: int,
    idempotency_key: str,
    correlation_id: str,
) -> ApprovalDecision:
    existing = session.scalar(
        select(ApprovalDecision).where(
            ApprovalDecision.organization_id == expense.organization_id,
            ApprovalDecision.idempotency_key == idempotency_key,
        )
    )
    if existing:
        return existing
    if expense.row_version != expected_version or expense.state != ExpenseState.AWAITING_REVIEW:
        raise DomainConflict("Expense is stale or no longer awaiting review")
    latest = max(expense.attempts, key=lambda item: item.created_at, default=None)
    observed = latest.recommendation if latest else Recommendation.REVIEW
    target = {
        DecisionAction.APPROVE: ExpenseState.APPROVED,
        DecisionAction.REJECT: ExpenseState.REJECTED,
        DecisionAction.REQUEST_INFORMATION: ExpenseState.INFORMATION_REQUESTED,
    }[action]
    override = (action == DecisionAction.APPROVE and observed != Recommendation.APPROVE) or (
        action == DecisionAction.REJECT and observed != Recommendation.REJECT
    )
    if (override or action != DecisionAction.APPROVE) and not reason:
        raise DomainConflict("A reason is required for this decision")
    ensure_transition(ExpenseState(expense.state), target)
    decision = ApprovalDecision(
        organization_id=expense.organization_id,
        expense_id=expense.id,
        actor_id=actor_id,
        action=action,
        reason=reason,
        observed_recommendation=observed,
        idempotency_key=idempotency_key,
    )
    session.add(decision)
    expense.state = target
    expense.row_version += 1
    append_audit(
        session,
        organization_id=expense.organization_id,
        actor_id=actor_id,
        entity_type="expense",
        entity_id=expense.id,
        action=f"expense.{action.lower()}",
        metadata={"reason": reason, "observed_recommendation": str(observed), "override": override},
        correlation_id=correlation_id,
    )
    session.commit()
    return decision
