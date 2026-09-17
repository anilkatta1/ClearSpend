import os
from collections.abc import Iterator
from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from app.db import (
    AccountingExport,
    AuditEvent,
    Expense,
    Organization,
    OutboxEvent,
    PolicyVersion,
    SessionLocal,
    User,
)
from app.jobs import relay_outbox_batch
from app.services import DomainConflict, export_expense

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DATABASE_TESTS") != "1",
        reason="set RUN_DATABASE_TESTS=1 with a migrated PostgreSQL test database",
    ),
]


@pytest.fixture
def ready_expense() -> Iterator[tuple[str, str, str]]:
    suffix = uuid4().hex
    with SessionLocal() as session:
        organization = Organization(slug=f"export-{suffix}", name="Export recovery test")
        user = User(email=f"reviewer-{suffix}@example.test", name="Test reviewer")
        session.add_all([organization, user])
        session.flush()
        policy = PolicyVersion(
            organization_id=organization.id,
            version=1,
            status="PUBLISHED",
            title="Test policy",
        )
        session.add(policy)
        session.flush()
        expense = Expense(
            organization_id=organization.id,
            submitter_id=user.id,
            policy_version_id=policy.id,
            merchant="Example Hotel",
            amount_minor=225_000,
            currency="INR",
            incurred_date=date(2026, 9, 15),
            category="travel",
            purpose="Customer workshop",
            state="READY_TO_EXPORT",
            idempotency_key=f"expense-{suffix}",
            request_hash="a" * 64,
            receipt_present=True,
        )
        session.add(expense)
        session.commit()
        identifiers = (organization.id, user.id, expense.id)

    yield identifiers

    organization_id, user_id, expense_id = identifiers
    with SessionLocal.begin() as session:
        session.execute(delete(AuditEvent).where(AuditEvent.organization_id == organization_id))
        session.execute(delete(AccountingExport).where(AccountingExport.expense_id == expense_id))
        stored_expense = session.get(Expense, expense_id)
        policy_id = stored_expense.policy_version_id if stored_expense else None
        session.execute(delete(Expense).where(Expense.id == expense_id))
        if policy_id:
            session.execute(delete(PolicyVersion).where(PolicyVersion.id == policy_id))
        session.execute(delete(User).where(User.id == user_id))
        session.execute(delete(Organization).where(Organization.id == organization_id))


def test_export_failure_is_durable_and_actionable(
    ready_expense: tuple[str, str, str],
) -> None:
    organization_id, actor_id, expense_id = ready_expense

    def unavailable_renderer(**_: object) -> str:
        raise RuntimeError("synthetic adapter outage")

    with SessionLocal() as session:
        expense = session.get(Expense, expense_id)
        assert expense is not None
        with pytest.raises(DomainConflict, match="CSV_GENERATION_FAILED"):
            export_expense(
                session,
                expense=expense,
                actor_id=actor_id,
                account_code="TRAVEL",
                cost_center="INDIA-SALES",
                expected_version=expense.row_version,
                correlation_id=f"export-failure-{uuid4()}",
                renderer=unavailable_renderer,
            )

    with SessionLocal() as session:
        expense = session.get(Expense, expense_id)
        record = session.scalar(
            select(AccountingExport).where(AccountingExport.expense_id == expense_id)
        )
        assert expense is not None and expense.state == "EXPORT_FAILED"
        assert expense.organization_id == organization_id
        assert record is not None and record.status == "EXPORT_FAILED"
        assert record.error_code == "CSV_GENERATION_FAILED"
        assert record.error_detail == "CSV generation failed; verify coding values and retry."

    with SessionLocal() as session:
        expense = session.get(Expense, expense_id)
        assert expense is not None
        recovered = export_expense(
            session,
            expense=expense,
            actor_id=actor_id,
            account_code="TRAVEL",
            cost_center="INDIA-SALES",
            expected_version=expense.row_version,
            correlation_id=f"export-retry-{uuid4()}",
        )
        assert recovered.status == "EXPORTED"
        assert recovered.error_code is None
        assert recovered.error_detail is None

    with SessionLocal() as session:
        expense = session.get(Expense, expense_id)
        assert expense is not None and expense.state == "EXPORTED"


@pytest.mark.asyncio
async def test_unpublished_outbox_event_is_relayed_and_marked_published(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid4().hex
    calls: list[tuple[str, str]] = []

    async def capture_enqueue(expense_id: str, correlation_id: str) -> None:
        calls.append((expense_id, correlation_id))

    monkeypatch.setattr("app.jobs.enqueue_assessment_on_open_app", capture_enqueue)
    expense_id = str(uuid4())
    correlation_id = f"correlation-{suffix}"
    with SessionLocal() as session:
        organization = Organization(slug=f"outbox-{suffix}", name="Outbox recovery test")
        session.add(organization)
        session.flush()
        event = OutboxEvent(
            organization_id=organization.id,
            aggregate_id=expense_id,
            event_type="assessment.requested",
            payload={
                "expense_id": expense_id,
                "correlation_id": correlation_id,
            },
        )
        session.add(event)
        session.commit()
        organization_id, event_id = organization.id, event.id

    try:
        published = await relay_outbox_batch()
        with SessionLocal() as session:
            recovered = session.get(OutboxEvent, event_id)
            assert recovered is not None and recovered.published_at is not None
        assert published >= 1
        assert (expense_id, correlation_id) in calls
    finally:
        with SessionLocal.begin() as session:
            session.execute(delete(OutboxEvent).where(OutboxEvent.id == event_id))
            session.execute(delete(Organization).where(Organization.id == organization_id))
