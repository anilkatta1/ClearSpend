import csv
import io
from typing import Any, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import append_audit
from app.db import (
    AccountingExport,
    ApprovalDecision,
    AssessmentAttempt,
    Expense,
    PolicyRule,
    PolicySection,
    PolicyVersion,
)
from app.domain import ClaimFacts, DecisionAction, ExpenseState, Recommendation, ensure_transition
from app.graph import assess_claim
from app.rules import evaluate_receipt_match


class DomainConflict(Exception):
    pass


class AccountingExportRenderer(Protocol):
    def __call__(self, *, expense: Expense, account_code: str, cost_center: str) -> str: ...


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
    latest = max(
        expense.attempts,
        key=lambda item: (item.revision, item.created_at, item.id),
        default=None,
    )
    sections = {section.id: section for section in expense.policy_version.sections}
    citation_ids = {
        section_id
        for check in (latest.checks if latest else [])
        for section_id in check.get("policy_section_ids", [])
    }
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
        "receipt_id": expense.receipt_id,
        "receipt": (
            {
                "id": expense.receipt.id,
                "filename": expense.receipt.filename,
                "content_type": expense.receipt.content_type,
                "extraction_status": expense.receipt.extraction_status,
                "extracted_merchant": expense.receipt.extracted_merchant,
                "extracted_date": expense.receipt.extracted_date,
                "extracted_amount_minor": expense.receipt.extracted_amount_minor,
                "extracted_currency": expense.receipt.extracted_currency,
            }
            if expense.receipt
            else None
        ),
        "information_request_message": expense.information_request_message,
        "requested_fields": expense.requested_fields,
        "policy_citations": [
            {"id": key, "title": sections[key].title, "text": sections[key].source_text}
            for key in citation_ids
            if key in sections
        ],
        "export": (
            {
                "id": expense.accounting_export.id,
                "status": expense.accounting_export.status,
                "account_code": expense.accounting_export.account_code,
                "cost_center": expense.accounting_export.cost_center,
                "error_code": expense.accounting_export.error_code,
                "error_detail": expense.accounting_export.error_detail,
            }
            if expense.accounting_export
            else None
        ),
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
        ensure_transition(ExpenseState(expense.state), ExpenseState.ASSESSING)
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
            submitted_date=expense.submitted_at.date(),
            receipt_present=expense.receipt_present,
            receipt_hash=expense.receipt_hash,
        ),
        [(row[0], row[1], row[2]) for row in policy_rules],
    )
    receipt = expense.receipt
    receipt_section_id = next(
        (str(row[2]) for row in policy_rules if row[0] == "receipt_required"),
        expense.policy_version.sections[0].id,
    )
    receipt_check = evaluate_receipt_match(
        ClaimFacts(
            amount_minor=expense.amount_minor,
            currency=expense.currency,
            category=expense.category,
            merchant=expense.merchant,
            purpose=expense.purpose,
            incurred_date=expense.incurred_date,
            submitted_date=expense.submitted_at.date(),
            receipt_present=expense.receipt_present,
            receipt_hash=expense.receipt_hash,
        ),
        extracted_amount_minor=receipt.extracted_amount_minor if receipt else None,
        extracted_currency=receipt.extracted_currency if receipt else None,
        extracted_merchant=receipt.extracted_merchant if receipt else None,
        extracted_date=receipt.extracted_date if receipt else None,
        extraction_status=receipt.extraction_status if receipt else "NO_RECEIPT",
        section_id=receipt_section_id,
    )
    state["checks"] = [*state["checks"], receipt_check]
    if receipt_check.status == "UNKNOWN" and state.get("recommendation") == Recommendation.APPROVE:
        state["recommendation"] = Recommendation.REVIEW
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
    request_hash: str,
    requested_fields: list[str],
    reviewer_active_ms: int | None,
    correlation_id: str,
) -> ApprovalDecision:
    existing = session.scalar(
        select(ApprovalDecision).where(
            ApprovalDecision.organization_id == expense.organization_id,
            ApprovalDecision.actor_id == actor_id,
            ApprovalDecision.idempotency_key == idempotency_key,
        )
    )
    if existing:
        if existing.actor_id != actor_id or existing.request_hash != request_hash:
            raise DomainConflict("Idempotency key was already used for a different decision")
        return existing
    if expense.row_version != expected_version or expense.state != ExpenseState.AWAITING_REVIEW:
        raise DomainConflict("Expense is stale or no longer awaiting review")
    latest = max(
        expense.attempts,
        key=lambda item: (item.revision, item.created_at, item.id),
        default=None,
    )
    observed = latest.recommendation if latest else Recommendation.REVIEW
    target = {
        DecisionAction.APPROVE: ExpenseState.READY_TO_EXPORT,
        DecisionAction.REJECT: ExpenseState.REJECTED,
        DecisionAction.REQUEST_INFORMATION: ExpenseState.INFORMATION_REQUESTED,
    }[action]
    override = (action == DecisionAction.APPROVE and observed != Recommendation.APPROVE) or (
        action == DecisionAction.REJECT and observed != Recommendation.REJECT
    )
    if (override or action != DecisionAction.APPROVE) and not reason:
        raise DomainConflict("A reason is required for this decision")
    if action == DecisionAction.REQUEST_INFORMATION and not requested_fields:
        raise DomainConflict("Select at least one field to request from the employee")
    ensure_transition(ExpenseState(expense.state), target)
    decision = ApprovalDecision(
        organization_id=expense.organization_id,
        expense_id=expense.id,
        actor_id=actor_id,
        action=action,
        reason=reason,
        observed_recommendation=observed,
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        requested_fields=requested_fields,
        reviewer_active_ms=reviewer_active_ms,
    )
    session.add(decision)
    expense.state = target
    expense.row_version += 1
    expense.information_request_message = (
        reason if action == DecisionAction.REQUEST_INFORMATION else None
    )
    expense.requested_fields = (
        requested_fields if action == DecisionAction.REQUEST_INFORMATION else []
    )
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


def render_accounting_csv(*, expense: Expense, account_code: str, cost_center: str) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "expense_id",
            "merchant",
            "date",
            "amount_minor",
            "currency",
            "account_code",
            "cost_center",
        ]
    )
    writer.writerow(
        [
            expense.id,
            expense.merchant,
            expense.incurred_date.isoformat(),
            expense.amount_minor,
            expense.currency,
            account_code,
            cost_center,
        ]
    )
    return output.getvalue()


def export_expense(
    session: Session,
    *,
    expense: Expense,
    actor_id: str,
    account_code: str,
    cost_center: str,
    expected_version: int,
    correlation_id: str,
    renderer: AccountingExportRenderer = render_accounting_csv,
) -> AccountingExport:
    if expense.row_version != expected_version or expense.state not in {
        ExpenseState.READY_TO_EXPORT,
        ExpenseState.EXPORT_FAILED,
    }:
        raise DomainConflict("Expense is stale or not ready for accounting export")
    record = expense.accounting_export or AccountingExport(
        organization_id=expense.organization_id,
        expense_id=expense.id,
        actor_id=actor_id,
        account_code=account_code,
        cost_center=cost_center,
        status="READY_TO_EXPORT",
    )
    record.actor_id = actor_id
    record.account_code = account_code
    record.cost_center = cost_center
    session.add(record)
    try:
        csv_content = renderer(
            expense=expense,
            account_code=account_code,
            cost_center=cost_center,
        )
    except Exception:
        error_code = "CSV_GENERATION_FAILED"
        error_detail = "CSV generation failed; verify coding values and retry."
        record.status = ExpenseState.EXPORT_FAILED
        record.csv_content = None
        record.error_code = error_code
        record.error_detail = error_detail
        if expense.state == ExpenseState.READY_TO_EXPORT:
            ensure_transition(ExpenseState.READY_TO_EXPORT, ExpenseState.EXPORT_FAILED)
        expense.state = ExpenseState.EXPORT_FAILED
        expense.row_version += 1
        append_audit(
            session,
            organization_id=expense.organization_id,
            actor_id=actor_id,
            entity_type="expense",
            entity_id=expense.id,
            action="expense.export_failed",
            metadata={"error_code": error_code, "format": "CSV"},
            correlation_id=correlation_id,
        )
        session.commit()
        raise DomainConflict(f"{error_code}: {error_detail}") from None

    record.status = ExpenseState.EXPORTED
    record.csv_content = csv_content
    record.error_code = None
    record.error_detail = None
    ensure_transition(ExpenseState(expense.state), ExpenseState.EXPORTED)
    expense.state = ExpenseState.EXPORTED
    expense.row_version += 1
    append_audit(
        session,
        organization_id=expense.organization_id,
        actor_id=actor_id,
        entity_type="expense",
        entity_id=expense.id,
        action="expense.exported",
        metadata={"account_code": account_code, "cost_center": cost_center, "format": "CSV"},
        correlation_id=correlation_id,
    )
    session.commit()
    return record
