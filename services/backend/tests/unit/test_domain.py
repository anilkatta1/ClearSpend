from datetime import date

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.domain import (
    CheckStatus,
    ClaimFacts,
    ExpenseState,
    PolicyCheck,
    Recommendation,
    aggregate_recommendation,
    ensure_transition,
)
from app.rules import evaluate_rules


def check(status: CheckStatus, source: str = "DETERMINISTIC") -> PolicyCheck:
    return PolicyCheck(
        check_key="example",
        source=source,
        status=status,
        reason_code="EXAMPLE",
        explanation="Worked example",
        policy_section_ids=["section-1"],
    )


def facts(amount: int = 100_000, category: str = "travel", receipt: bool = True) -> ClaimFacts:
    return ClaimFacts(
        amount_minor=amount,
        currency="INR",
        category=category,
        merchant="Example Hotel",
        purpose="Customer workshop",
        incurred_date=date(2026, 9, 1),
        submitted_date=date(2026, 9, 8),
        receipt_present=receipt,
    )


def test_deterministic_failure_cannot_be_overwritten_by_ai_pass() -> None:
    assert (
        aggregate_recommendation([check(CheckStatus.FAIL), check(CheckStatus.PASS, "AI")])
        == Recommendation.REJECT
    )


def test_unknown_evidence_fails_closed() -> None:
    assert (
        aggregate_recommendation([check(CheckStatus.PASS), check(CheckStatus.UNKNOWN, "AI")])
        == Recommendation.REVIEW
    )


def test_only_all_pass_recommends_approval() -> None:
    assert (
        aggregate_recommendation([check(CheckStatus.PASS), check(CheckStatus.PASS, "AI")])
        == Recommendation.APPROVE
    )


def test_final_state_cannot_be_reopened() -> None:
    with pytest.raises(ValueError):
        ensure_transition(ExpenseState.APPROVED, ExpenseState.SUBMITTED)


@given(amount=st.integers(min_value=1, max_value=10_000_000))
def test_amount_limit_boundary(amount: int) -> None:
    result = evaluate_rules(
        facts(amount=amount), [("amount_limit", {"limit_minor": 5_000_000}, "section-1")]
    )[0]
    assert result.status == (CheckStatus.PASS if amount <= 5_000_000 else CheckStatus.FAIL)


def test_receipt_threshold_is_inclusive() -> None:
    below = evaluate_rules(
        facts(amount=99_999, receipt=False),
        [("receipt_required", {"threshold_minor": 100_000}, "s")],
    )[0]
    exact = evaluate_rules(
        facts(amount=100_000, receipt=False),
        [("receipt_required", {"threshold_minor": 100_000}, "s")],
    )[0]
    assert below.status == CheckStatus.PASS
    assert exact.status == CheckStatus.FAIL


def test_prohibited_category_is_case_insensitive() -> None:
    result = evaluate_rules(
        facts(category="Alcohol"), [("prohibited_category", {"categories": ["alcohol"]}, "s")]
    )[0]
    assert result.status == CheckStatus.FAIL
