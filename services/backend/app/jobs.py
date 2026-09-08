import procrastinate
from sqlalchemy import select

from app.config import settings
from app.db import OutboxEvent, SessionLocal, utcnow
from app.services import process_assessment

procrastinate_app = procrastinate.App(
    connector=procrastinate.PsycopgConnector(conninfo=settings.procrastinate_database_url)
)


@procrastinate_app.task(
    queue="assessments",
    retry=procrastinate.RetryStrategy(max_attempts=5, exponential_wait=2),
)
async def assess_expense(expense_id: str, correlation_id: str) -> None:
    with SessionLocal() as session:
        process_assessment(session, expense_id, correlation_id)


async def enqueue_assessment_on_open_app(expense_id: str, correlation_id: str) -> None:
    await assess_expense.configure(
        lock=f"expense:{expense_id}",
        queueing_lock=f"expense:{expense_id}",
    ).defer_async(expense_id=expense_id, correlation_id=correlation_id)


async def enqueue_assessment(expense_id: str, correlation_id: str) -> None:
    async with procrastinate_app.open_async():
        await enqueue_assessment_on_open_app(expense_id, correlation_id)


async def relay_outbox_batch(batch_size: int = 25) -> int:
    """Publish committed assessment events, recovering API enqueue failures."""
    published = 0
    with SessionLocal() as session:
        events = session.scalars(
            select(OutboxEvent)
            .where(
                OutboxEvent.published_at.is_(None),
                OutboxEvent.event_type == "assessment.requested",
            )
            .order_by(OutboxEvent.created_at)
            .with_for_update(skip_locked=True)
            .limit(batch_size)
        ).all()
        for event in events:
            try:
                await enqueue_assessment_on_open_app(
                    str(event.payload["expense_id"]),
                    str(event.payload["correlation_id"]),
                )
            except procrastinate.exceptions.AlreadyEnqueued:
                pass
            event.published_at = utcnow()
            published += 1
        session.commit()
    return published
