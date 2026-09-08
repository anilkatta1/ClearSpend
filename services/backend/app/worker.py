import asyncio
import contextlib

import structlog

from app.jobs import procrastinate_app, relay_outbox_batch

logger = structlog.get_logger()


async def relay_outbox() -> None:
    while True:
        try:
            published = await relay_outbox_batch()
            if published:
                logger.info("outbox.relayed", count=published)
        except Exception as exc:
            logger.exception("outbox.relay_failed", error=type(exc).__name__)
        await asyncio.sleep(2)


async def main() -> None:
    async with procrastinate_app.open_async():
        relay = asyncio.create_task(relay_outbox())
        try:
            await procrastinate_app.run_worker_async(queues=["assessments"], concurrency=4)
        finally:
            relay.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await relay


if __name__ == "__main__":
    asyncio.run(main())
