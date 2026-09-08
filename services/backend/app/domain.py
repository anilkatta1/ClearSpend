from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Role(StrEnum):
    EMPLOYEE = "EMPLOYEE"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"


class ExpenseState(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ASSESSING = "ASSESSING"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    INFORMATION_REQUESTED = "INFORMATION_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class Recommendation(StrEnum):
    APPROVE = "APPROVE_RECOMMENDED"
    REJECT = "REJECT_RECOMMENDED"
    REVIEW = "NEEDS_REVIEW"


class DecisionAction(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_INFORMATION = "REQUEST_INFORMATION"


class PolicyCheck(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    check_key: str = Field(min_length=1, max_length=80)
    source: Literal["DETERMINISTIC", "AI"]
    status: CheckStatus
    reason_code: str = Field(min_length=1, max_length=80)
    explanation: str = Field(max_length=500)
    policy_section_ids: list[str] = Field(max_length=10)
    evidence_refs: list[str] = Field(default_factory=list, max_length=10)


@dataclass(frozen=True)
class ClaimFacts:
    amount_minor: int
    currency: str
    category: str
    merchant: str
    purpose: str
    incurred_date: date
    submitted_date: date
    receipt_present: bool
    receipt_hash: str | None = None


ALLOWED_TRANSITIONS: dict[ExpenseState, frozenset[ExpenseState]] = {
    ExpenseState.DRAFT: frozenset({ExpenseState.SUBMITTED}),
    ExpenseState.SUBMITTED: frozenset({ExpenseState.ASSESSING}),
    ExpenseState.ASSESSING: frozenset({ExpenseState.AWAITING_REVIEW}),
    ExpenseState.AWAITING_REVIEW: frozenset(
        {ExpenseState.INFORMATION_REQUESTED, ExpenseState.APPROVED, ExpenseState.REJECTED}
    ),
    ExpenseState.INFORMATION_REQUESTED: frozenset({ExpenseState.SUBMITTED}),
    ExpenseState.APPROVED: frozenset(),
    ExpenseState.REJECTED: frozenset(),
}


def ensure_transition(current: ExpenseState, target: ExpenseState) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid expense transition: {current} -> {target}")


def aggregate_recommendation(
    checks: list[PolicyCheck], *, technical_failure: bool = False
) -> Recommendation:
    if technical_failure or not checks:
        return Recommendation.REVIEW
    deterministic = [c for c in checks if c.source == "DETERMINISTIC"]
    if any(c.status == CheckStatus.FAIL for c in deterministic):
        return Recommendation.REJECT
    if any(c.status == CheckStatus.UNKNOWN for c in checks):
        return Recommendation.REVIEW
    if all(c.status == CheckStatus.PASS for c in checks):
        return Recommendation.APPROVE
    return Recommendation.REVIEW


def validate_rule_params(rule_type: str, params: dict[str, Any]) -> None:
    required: dict[str, set[str]] = {
        "receipt_required": {"threshold_minor"},
        "amount_limit": {"limit_minor"},
        "prohibited_category": {"categories"},
        "business_purpose_required": set(),
        "submission_window": {"days"},
    }
    if rule_type not in required:
        raise ValueError(f"Unsupported rule type: {rule_type}")
    missing = required[rule_type] - params.keys()
    if missing:
        raise ValueError(f"Missing rule parameters: {sorted(missing)}")
