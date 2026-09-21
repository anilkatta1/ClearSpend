from datetime import date
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import ExpenseItemIn, ExpenseReportIn, ResubmissionIn


def item(receipt_id: str | None = None) -> ExpenseItemIn:
    return ExpenseItemIn(
        receipt_id=receipt_id or str(uuid4()),
        merchant="Synthetic City Rail",
        amount_minor=75_000,
        currency="INR",
        incurred_date=date(2026, 9, 15),
    )


def test_report_accepts_multiple_unique_receipts_in_one_category() -> None:
    report = ExpenseReportIn(
        category="travel",
        purpose="Customer workshop trip",
        items=[item(), item()],
    )

    assert len(report.items) == 2
    assert report.category == "travel"


def test_report_rejects_duplicate_receipt_ids() -> None:
    receipt_id = str(uuid4())

    with pytest.raises(ValidationError, match="Each receipt may appear only once"):
        ExpenseReportIn(
            category="travel",
            purpose="Customer workshop trip",
            items=[item(receipt_id), item(receipt_id)],
        )


def test_resubmission_defaults_to_appending_only_new_evidence() -> None:
    body = ResubmissionIn(purpose="Added the missed taxi receipt", items=[item()])

    assert body.items_mode == "APPEND"


def test_resubmission_rejects_ambiguous_single_and_bundle_updates() -> None:
    with pytest.raises(ValidationError, match="either receipt_id or items"):
        ResubmissionIn(
            purpose="Ambiguous update",
            receipt_id=str(uuid4()),
            items=[item()],
        )
